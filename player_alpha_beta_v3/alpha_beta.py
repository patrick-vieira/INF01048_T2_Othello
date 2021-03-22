import sys
from time import perf_counter_ns

from common import board
from player_alpha_beta.monitor_performance import MonitorPerformance


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
        self.danger_zone = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 1), (2, 6), (3, 1), (3, 6), (4, 1), (4, 6), (5, 1), (5, 6), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6)]

    def danger_zone(self):
        zone = []
        for col in range(1, 7):  # coluna
            for row in range(1, 7):  # lina
                if col == 1 or col == 6:
                    zone.append((col, row))
                elif row == 1 or row == 6:
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

        return selected_move

    def next_move_alfa_beta(self, max_depth):
        alfa = float('-inf')
        beta = float('+inf')

        v = float('-inf')

        best_move = (-1, -1)

        if len(self.available_moves) > 0:  # se existe algum movimento possivel
            for move in self.available_moves:  # para cada movimento disponivel
                imaginary_board = board.from_string(str(self.board))  # cria um tabuleiro "imaginario"
                score = self.alfa_beta_max(imaginary_board, alfa, beta, max_depth)

                #score += self.move_eval(imaginary_board, move)
                if score > v:
                    v = score
                    best_move = move

        self.show_move_result(best_move)

        return best_move

    def alfa_beta_max(self, a_board, alfa, beta, max_depth):
        if (len(a_board.legal_moves(self.my_color)) > 0) \
                and (max_depth > 0) \
                and (perf_counter_ns() - self.start_time) < self.max_time:
            depth = max_depth - 1
            for move in a_board.legal_moves(self.my_color):
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(move, self.my_color)

                self.node_expands_counter += 1
                v = self.alfa_beta_min(imaginary_board, alfa, beta, depth)
                alfa = max(v, alfa)
                if beta < alfa:
                    self.pruning_counter += 1
                    return alfa
            return alfa
        else:
            score = self.__get_board_score(a_board)
            return score

    def alfa_beta_min(self, a_board, alfa, beta, max_depth):
        if (len(a_board.legal_moves(self.opponent_color)) > 0) \
                and (max_depth > 0) \
                and (perf_counter_ns() - self.start_time) < self.max_time:
            depth = max_depth - 1
            for move in a_board.legal_moves(self.opponent_color):
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(move, self.opponent_color)

                self.node_expands_counter += 1
                v = self.alfa_beta_max(imaginary_board, alfa, beta, depth)

                beta = min(v, beta)
                if alfa >= beta:
                    self.pruning_counter += 1
                    return beta
            return beta
        else:
            score = self.__get_board_score(a_board)  # Retorna o valor do ultimo nó expandido
            return score

    def has_time(self):
        return (perf_counter_ns() - self.start_time) < self.max_time


    def move_eval(self, a_board, move):
        score = 0
        score += self.is_move_on_corner(move)
        score += self.off_center_move(move)
        score += self.is_move_in_danger_zone(a_board, move)

        a_board.process_move(move, self.my_color)
        a_board.legal_moves(self.opponent_color)
        return score

    # se o movimento é uma das bordas recebe prioridade
    def is_move_on_corner(self, move):
        if move == self.top_left or move == self.top_right or move == self.bottom_left or move == self.bottom_right:
            return 10
        return 0

    # movimento que se afasta do centro recebe uma penalidade
    def off_center_move(self, move):
        center = 3.5
        penalty1 = move[0] - center
        penalty2 = move[1] - center
        return (abs(penalty1) + abs(penalty2)) * -1

    def is_move_in_danger_zone(self, a_board, move):
        if move in self.danger_zone:
            return -2
        return 0


if __name__ == '__main__':
    b = board.from_file(sys.argv[1])
    f = open('move.txt', 'w')
    patrick = AlphaBeta(b, sys.argv[2])

    with MonitorPerformance():
        movement = patrick.next_move_alfa_beta(2)

    f.write('%d,%d' % movement)

    f.close()


    #funções de avaliação
    #o movimento é uma das quinas? se sim faz
    #se jogar esse movimento quantos movimentos o adversario vai poder fazer
    #