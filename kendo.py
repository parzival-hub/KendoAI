import math
import sys
import pygame
import copy


class Piece:
    def __init__(self, team, moving_range):
        self.moving_range = moving_range
        self.team = team
        self.selected = False

    def draw(self, screen, position):
        team_color = (255, 0, 0) if self.team == TEAM_ONE else (0, 0, 255)
        if self.selected:
            pygame.draw.circle(screen, (255, 255, 0), position, SELECT_RADIUS)
        pygame.draw.circle(screen, team_color, position, PIECE_RADIUS)

        # Render text on knot
        font = pygame.font.Font(None, 25)
        text_surface = font.render(str(self.moving_range), True, WHITE)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)


class Knot:
    def __init__(self, name, pos):
        self.name = name
        self.position = pos
        self.__connections = []
        self.piece = None
        self.highlighted = False

    def get_possible_moves(self):
        if not self.piece:
            return []

        # King movement
        if self.piece.moving_range == 1:
            return [t_knot for t_knot in self.get_restricted_connections(only_placeable=True, team=self.get_team())]

        # Pawn movement
        if self.piece.moving_range == 2:
            connections_list = set()

            # get adjecent knots
            for knot_depth_1 in self.get_restricted_connections(only_walkable=True):
                # get two depth knots
                for knot_depth_2 in knot_depth_1.get_restricted_connections(last_hop=knot_depth_1, only_placeable=True, team=self.get_team()):
                    connections_list.add(knot_depth_2)
            return list(connections_list)

        # Knight movement
        if self.piece.moving_range == 3:
            connections_list = set()

            # get adjecent knots
            for knot_depth_1 in self.get_restricted_connections(only_walkable=True):
                # print("Depth: 1", knot_depth_1)
                # get two depth knots
                for knot_depth_2 in knot_depth_1.get_restricted_connections(last_hop=self, only_walkable=True):
                    # print("Depth: 2", knot_depth_2)
                    # get three depth knots
                    for knot_depth_3 in knot_depth_2.get_restricted_connections(last_hop=knot_depth_1, only_placeable=True, team=self.get_team()):
                        connections_list.add(knot_depth_3)
            return list(connections_list)

    def add_connection(self, other_knot, connect_back=True):
        self.__connections.append(other_knot)
        if connect_back:
            other_knot.add_connection(self, connect_back=False)

    def get_connections(self):
        return self.__connections

    def get_restricted_connections(self, last_hop=None, only_placeable=False, only_walkable=False, team=None):
        conn_list = []
        for t_knot in self.__connections:

            if not only_walkable or t_knot.piece == None:
                # if only_walkable:
                # print("passed walkable", t_knot, t_knot.piece)

                if not only_placeable or (not t_knot.piece or t_knot.get_team() != team):
                    # if only_placeable:
                    # print("passed placeable", t_knot, t_knot.piece)

                    if not last_hop or t_knot.name != last_hop.name:
                        # print("passed last_hop", t_knot, t_knot.piece)
                        if t_knot.name != "middle":
                            conn_list.append(t_knot)

        return conn_list

    def get_team(self):
        if self.piece:
            return self.piece.team
        else:
            return -1

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name + str(self.position)  # "[" + ",".join(e.name for e in self.get_connections())+"]"

    def set_piece(self, piece):
        self.piece = piece

    def take_piece(self):
        r = copy.copy(self.piece)
        self.piece = None
        return r

    def draw(self, screen, drawn_connections):
        for connection in self.get_connections():
            if self.name+connection.name not in drawn_connections:
                pygame.draw.line(screen, BLACK, self.position, connection.position, 2)
                drawn_connections.append(self.name+connection.name)
                drawn_connections.append(connection.name+self.name)

        if self.get_name() == "middle":
            pygame.draw.circle(screen, (0, 255, 0), self.position, MIDDLE_RADIUS)
        else:
            if self.highlighted:
                pygame.draw.circle(screen, (0, 0, 255), self.position, SELECT_RADIUS)
            else:
                pygame.draw.circle(screen, BLACK, self.position, KNOT_RADIUS)

        if self.piece:
            self.piece.draw(screen, self.position)


class Game:
    def __init__(self):
        self.board = self.init_board()
        self.add_pieces_to_board()

    def init_board(self):
        board = {}
        start_pixel_y = SCREEN_HEIGHT/2 - DRAW_MIN_DISTANCE*4
        start_pixel_x = SCREEN_WIDTH/2 - DRAW_MIN_DISTANCE * 4
        offset = DRAW_MIN_DISTANCE

        for i in range(1, 7+1):
            name = f"A{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE, start_pixel_y if i % 2 == 0 else start_pixel_y+DRAW_MIN_DISTANCE/2)
            board[name] = Knot(name, pos)

        for i in range(1, 9+1):
            name = f"B{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE-offset, (start_pixel_y if i % 2 == 0 else start_pixel_y+DRAW_MIN_DISTANCE/2) + offset * 1.5)
            board[name] = Knot(name, pos)

        for i in range(1, 11+1):
            name = f"C{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE-offset*2, (start_pixel_y if i % 2 == 0 else start_pixel_y+DRAW_MIN_DISTANCE/2) + offset * 3)
            board[name] = Knot(name, pos)

        for i in range(1, 11+1):
            name = f"D{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE-offset*2, (start_pixel_y if i %
                   2 != 0 else start_pixel_y+DRAW_MIN_DISTANCE/2) + offset*4.5)
            board[name] = Knot(name, pos)

        for i in range(1, 9+1):
            name = f"E{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE-offset, (start_pixel_y if i %
                   2 != 0 else start_pixel_y+DRAW_MIN_DISTANCE/2) + offset*6)
            board[name] = Knot(name, pos)

        for i in range(1, 7+1):
            name = f"F{i}"
            pos = (start_pixel_x+i*DRAW_MIN_DISTANCE, (start_pixel_y if i % 2 != 0 else start_pixel_y+DRAW_MIN_DISTANCE/2)+offset*7.5)
            board[name] = Knot(name, pos)

        c6_pos = board["C6"].position
        board["middle"] = Knot("middle", (c6_pos[0], c6_pos[1]+DRAW_MIN_DISTANCE))

        # add connections to knots
        board["middle"].add_connection(board["C5"])
        board["middle"].add_connection(board["C6"])
        board["middle"].add_connection(board["C7"])
        board["middle"].add_connection(board["D5"])
        board["middle"].add_connection(board["D6"])
        board["middle"].add_connection(board["D7"])

        board["A1"].add_connection(board["B2"])
        board["A3"].add_connection(board["B4"])
        board["A5"].add_connection(board["B6"])
        board["A7"].add_connection(board["B8"])

        board["B1"].add_connection(board["C2"])
        board["B3"].add_connection(board["C4"])
        board["B5"].add_connection(board["C6"])
        board["B7"].add_connection(board["C8"])
        board["B9"].add_connection(board["C10"])

        board["C1"].add_connection(board["D1"])
        board["C3"].add_connection(board["D3"])
        board["C5"].add_connection(board["D5"])
        board["C7"].add_connection(board["D7"])
        board["C9"].add_connection(board["D9"])
        board["C11"].add_connection(board["D11"])

        board["D2"].add_connection(board["E1"])
        board["D4"].add_connection(board["E3"])
        board["D6"].add_connection(board["E5"])
        board["D8"].add_connection(board["E7"])
        board["D10"].add_connection(board["E9"])

        board["F1"].add_connection(board["E2"])
        board["F3"].add_connection(board["E4"])
        board["F5"].add_connection(board["E6"])
        board["F7"].add_connection(board["E8"])

        for letter in ["A", "B", "C", "D", "E", "F"]:
            for index in range(12):
                if f"{letter}{index}" in board.keys() and f"{letter}{index+1}" in board.keys():
                    board[f"{letter}{index}"].add_connection(board[f"{letter}{index+1}"])
        return board

    def add_pieces_to_board(self):
        self.board["A1"].set_piece(Piece(TEAM_ONE, 3))
        self.board["A2"].set_piece(Piece(TEAM_ONE, 3))
        self.board["A3"].set_piece(Piece(TEAM_ONE, 3))
        self.board["A4"].set_piece(Piece(TEAM_ONE, 1))
        self.board["A5"].set_piece(Piece(TEAM_ONE, 3))
        self.board["A6"].set_piece(Piece(TEAM_ONE, 3))
        self.board["A7"].set_piece(Piece(TEAM_ONE, 3))
        self.board["B4"].set_piece(Piece(TEAM_ONE, 2))
        self.board["B5"].set_piece(Piece(TEAM_ONE, 2))
        self.board["B6"].set_piece(Piece(TEAM_ONE, 2))

        self.board["F1"].set_piece(Piece(TEAM_TWO, 3))
        self.board["F2"].set_piece(Piece(TEAM_TWO, 3))
        self.board["F3"].set_piece(Piece(TEAM_TWO, 3))
        self.board["F4"].set_piece(Piece(TEAM_TWO, 1))
        self.board["F5"].set_piece(Piece(TEAM_TWO, 3))
        self.board["F6"].set_piece(Piece(TEAM_TWO, 3))
        self.board["F7"].set_piece(Piece(TEAM_TWO, 3))
        self.board["E4"].set_piece(Piece(TEAM_TWO, 2))
        self.board["E5"].set_piece(Piece(TEAM_TWO, 2))
        self.board["E6"].set_piece(Piece(TEAM_TWO, 2))


# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
KNOT_RADIUS = 17
MIDDLE_RADIUS = 45
PIECE_RADIUS = 12
SELECT_RADIUS = 15
DRAW_MIN_DISTANCE = 70
TEAM_ONE = 1
TEAM_TWO = 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def draw_knots(screen, knots):
    drawn_connections = []

    for knot in knots:
        knot.draw(screen, drawn_connections)


def move_piece(from_knot, to_knot):
    if to_knot in from_knot.get_possible_moves():
        to_knot.set_piece(from_knot.take_piece())


def get_possible_moves(board, team):
    possible_moves = []
    for knot in board:
        if knot.piece == team:
            possible_moves.append(knot.get_possible_moves())


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def handle_knot_click(knots, mouse_pos):
    for knot in knots:
        if distance(knot.position, mouse_pos) <= KNOT_RADIUS:
            print(knot.name, "clicked")  # Print "Test" if the knot is clicked
            if knot.piece:

                # toggle selection
                if knot.piece.selected:
                    knot.piece.selected = False
                    remove_highlights(knots)

                # select new piece
                else:
                    remove_selection(knots)
                    knot.piece.selected = True

                    # highlight for new pieces
                    remove_highlights(knots)
                    for k in knot.get_possible_moves():
                        k.highlighted = True

            # move piece
            elif knot.highlighted:
                for k in knots:
                    if k.piece and k.piece.selected:
                        current_selected_knot = k
                move_piece(current_selected_knot, knot)
                remove_selection(knots)
                remove_highlights(knots)

            # remove selection
            else:
                remove_selection(knots)
                remove_highlights(knots)
            break


def remove_selection(knots):
    for k in knots:
        if k.piece:
            k.piece.selected = False


def remove_highlights(knots):
    for k in knots:
        k.highlighted = False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Kendo")

    game = Game()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    handle_knot_click(game.board.values(), pygame.mouse.get_pos())

        screen.fill(WHITE)
        draw_knots(screen, game.board.values())

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
