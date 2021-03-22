import sys
from time import perf_counter_ns

from player_alpha_beta_v2.common import board
from player_alpha_beta_v2.monitor_performance import MonitorPerformance


class AlphaBeta:
    top_left = (0, 0)
    top_right = (0, 7)
    bottom_left = (7, 0)
    bottom_right = (7, 7)

    def __init__(self, board, my_color):
        self.my_color = board.WHITE if my_color == 'white' else board.BLACK
        self.opponent_color = board.opponent(self.my_color)
        self.board = board

        self.available_moves = board.legal_moves(self.my_color)
        self.pruning_counter = 0
        self.node_expands_counter = 0

        self.start_time = perf_counter_ns()
        self.max_time = 4.7 * 10 ** 9
        self.danger_zone = self.get_danger_zone()
        self.borders_zone = self.get_borders_zone()


    def get_danger_zone(self):
        zone = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 1), (2, 6), (3, 1), (3, 6), (4, 1), (4, 6), (5, 1), (5, 6), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6)]
        if len(zone) < 0: #hardcoded para não calcular denovo
            for col in range(1, 7):  # coluna
                for row in range(1, 7):  # lina
                    if col == 1 or col == 6:
                        zone.append((col, row))
                    elif row == 1 or row == 6:
                        zone.append((col, row))
        return zone

    def get_borders_zone(self):
        zone = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 0), (1, 7), (2, 0), (2, 7), (3, 0), (3, 7), (4, 0), (4, 7), (5, 0), (5, 7), (6, 0), (6, 7), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        if len(zone) < 0:  # hardcoded para não calcular denovo
            for col in range(0, 8):  # coluna
                for row in range(0, 8):  # lina
                    if col == 0 or col == 7:
                        zone.append((col, row))
                    elif row == 0 or row == 7:
                        zone.append((col, row))
        return zone

    def __get_board_score(self, board):
        scores = [board.piece_count[self.my_color], board.piece_count[self.opponent_color]]
        score = scores[0] - scores[1]
        return score

    def show_move_result(self, selected_move):
        before_move = self.__get_board_score(self.board)
        self.board.process_move(selected_move, self.my_color)
        after_move = self.__get_board_score(self.board)

        print("Score before movement: " + str(before_move))
        print("Score after movement:  " + str(after_move))
        print("Node expand count:  " + str(self.node_expands_counter))
        print("Pruning count:  " + str(self.pruning_counter))
        print("Selected move:  " + str(selected_move))

        return selected_move

    def next_move_alfa_beta(self, max_depth):
        alfa = float('-inf')
        beta = float('+inf')

        v = float('-inf')
        best_move = (-1, -1)

        if len(self.available_moves) < 1:
            return best_move

        depth = 1
        while depth <= max_depth:
            for move in self.board.legal_moves(self.my_color):
                with MonitorPerformance(False, "Execution time for depth: " + str(depth)):
                    imaginary_board = board.from_string(str(self.board))
                    score = self.alfa_beta_max(imaginary_board, alfa, beta, depth)
                    score += self.move_eval(imaginary_board, move, self.my_color)
                    if score > v:
                        v = score
                        best_move = move
            depth += 1

        self.show_move_result(best_move)

        return best_move

    def cut_test(self, a_board, alfa, beta, max_depth):
        # termina a execução se passou do tempo maximo
        if (perf_counter_ns() - self.start_time) > self.max_time:
            return True

        if len(a_board.legal_moves(self.my_color)) > 0 and (max_depth > 0):
            return False
        else:
            return True

    def alfa_beta_max(self, a_board, alfa, beta, max_depth):
        if self.cut_test(a_board, alfa, beta, max_depth):
            score = self.__get_board_score(a_board)
            return score

        for move in a_board.legal_moves(self.my_color):
            imaginary_board = board.from_string(str(a_board))
            imaginary_board.process_move(move, self.my_color)

            self.node_expands_counter += 1

            v = self.alfa_beta_min(imaginary_board, alfa, beta, max_depth - 1)
            v += self.move_eval(imaginary_board, move, self.my_color)

            alfa = max(v, alfa)
            if beta < alfa:
                self.pruning_counter += 1
                return alfa

        return alfa

    def alfa_beta_min(self, a_board, alfa, beta, max_depth):
        if self.cut_test(a_board, alfa, beta, max_depth):
            score = self.__get_board_score(a_board)
            return score

        for move in a_board.legal_moves(self.opponent_color):
            imaginary_board = board.from_string(str(a_board))
            imaginary_board.process_move(move, self.opponent_color)

            self.node_expands_counter += 1
            v = self.alfa_beta_max(imaginary_board, alfa, beta, max_depth - 1)
            v += self.move_eval(imaginary_board, move, self.opponent_color)

            beta = min(v, beta)
            if alfa >= beta:
                self.pruning_counter += 1
                return beta
        return beta

    def move_eval(self, a_board, move, color):
        score = 0
        score += self.is_move_on_corner(move)
        #score += self.off_center_move(move) # não deu muito certo
        score += self.is_move_in_danger_zone(move)
        score += self.is_move_in_borders(move)
        score += self.check_opponent_next_move(a_board, move, color)

        return score

    def check_opponent_next_move(self, a_board, move, color):
        score = 0
        a_board.process_move(move, color)

        opponent_next_moves = a_board.legal_moves(a_board.opponent(color))

        if len(opponent_next_moves) < 3:  #se oponente não tem poucos  movimentos é bom
            score += 5

        if len(opponent_next_moves) < 1: #se oponente não tem mais movimentos é bom
            score += 10

        for opponent_move in opponent_next_moves:
            if self.is_move_on_corner(opponent_move):  #se oponente pode usar canto é ruim
                score -= 2
                return score

            if self.is_move_in_borders(opponent_move):  #se oponente pode usar borda é ruim
                score -= 1
                return score
        return score

    # se o movimento é uma das bordas recebe prioridade
    def is_move_on_corner(self, move):
        if move == self.top_left \
                or move == self.top_right \
                or move == self.bottom_left \
                or move == self.bottom_right:
            return 5
        return 0

    # movimento que se afasta do centro recebe uma penalidade
    def off_center_move(self, move):
        center = 3.5
        penalty1 = move[0] - center
        penalty2 = move[1] - center
        return (abs(penalty1) + abs(penalty2)) * -1

    def is_move_in_danger_zone(self, move):
        if move in self.danger_zone:
            return -2
        return 0

    def is_move_in_borders(self, move):
        if move in self.borders_zone:
            return 3
        return 0


if __name__ == '__main__':
    b = board.from_file(sys.argv[1])
    f = open('move.txt', 'w')
    patrick = AlphaBeta(b, sys.argv[2])

    with MonitorPerformance(True):
        movement = patrick.next_move_alfa_beta(2)

    f.write('%d,%d' % movement)

    f.close()

