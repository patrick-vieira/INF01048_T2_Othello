import heapq
import sys

from common import board
from player_alpha_beta.monitor_performance import MonitorPerformance
from player_alpha_beta.move_score import MoveScore


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
            for move in self.get_ordered_best_moves_for_player(self.board):  # para cada movimento disponivel
            #for i, move in enumerate(self.available_moves):  # para cada movimento disponivel
                imaginary_board = board.from_string(str(self.board))  # cria um tabuleiro "imaginario"
                score = self.alfa_beta_max(imaginary_board, alfa, beta, max_depth)

                if score > v:
                    v = score
                    best_move = move

        self.show_move_result(best_move)

        return best_move

    def alfa_beta_max(self, a_board, alfa, beta, max_depth):
        if (len(a_board.legal_moves(self.my_color)) > 0) and (max_depth > 0):
            depth = max_depth - 1
            #for move in self.get_ordered_best_moves_for_oponent(a_board):
            #for move in self.get_ordered_best_moves_for_player(a_board):
            #for i, move in enumerate(a_board.legal_moves(self.my_color)):
            for move in a_board.legal_moves(self.my_color):
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(move, self.my_color)

                self.node_expands_counter += 1
                v = self.alfa_beta_min(imaginary_board, alfa, beta, depth)
                alfa = max(v, alfa)
                if beta < alfa:
                    self.pruning_counter += 1
                    #print("Nós podados na profundidade [" + str(max_depth) + "]=" + str(len(a_board.legal_moves(self.my_color)) - i) + " - MAX")
                    return alfa
            return alfa
        else:
            score = self.__get_board_score(a_board)
            return score

    def alfa_beta_min(self, a_board, alfa, beta, max_depth):
        if (len(a_board.legal_moves(self.opponent_color)) > 0) and (max_depth > 0):
            depth = max_depth - 1
            #for move in self.get_ordered_best_moves_for_player(a_board):
            #for move in self.get_ordered_best_moves_for_oponent(a_board):
            #for i, move in enumerate(a_board.legal_moves(self.opponent_color)):
            for move in a_board.legal_moves(self.opponent_color):
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(move, self.opponent_color)

                self.node_expands_counter += 1
                v = self.alfa_beta_max(imaginary_board, alfa, beta, depth)

                beta = min(v, beta)
                if alfa >= beta:
                    self.pruning_counter += 1
                    # print("Nós podados na profundidade [" + str(max_depth) + "]=" + str(len(a_board.legal_moves(self.opponent_color)) - i) + " - MIN")
                    return beta
            return beta
        else:
            score = self.__get_board_score(a_board)  # Retorna o valor do ultimo nó expandido
            return score

    """
    Antes e de usar essa funcionalidade o numero de podas para cada profundidade usando o estado state_teste_poda.txt:
    1: 0;169                                 0;169;84657400
    2: 143;728                               156;533;571373400
    3:  1131; 20488;6857975100                338; 3952;2553580300
    4: 19188;205582;70718427300              19526;180531;136965686300
    """

    def get_ordered_best_moves_for_player(self, a_board):
        best_moves = []
        heapq.heapify(best_moves)
        for move in a_board.legal_moves(self.my_color):
            imaginary_board = board.from_string(str(a_board))
            imaginary_board.process_move(move, self.my_color)

            score = self.__get_board_score(imaginary_board)
            move_score = MoveScore(move, (-1 * score), self.my_color)
            heapq.heappush(best_moves, move_score)
            # score invertido para ordenar pelo de maior valor ;)

        ordered_moves = []

        while len(best_moves) > 0:
            best_move = heapq.heappop(best_moves)
            ordered_moves.append(best_move.get_move())

        return ordered_moves

    def get_ordered_best_moves_for_oponent(self, a_board):
        best_moves = []
        heapq.heapify(best_moves)
        for move in a_board.legal_moves(self.opponent_color):
            imaginary_board = board.from_string(str(a_board))
            imaginary_board.process_move(move, self.opponent_color)

            score = self.__get_board_score(imaginary_board)
            move_score = MoveScore(move, score, self.opponent_color)
            heapq.heappush(best_moves, move_score)
            # o heap vai ordenar pelo menor valor

        ordered_moves = []

        # o melhor movimento do oponente é o que ao jogador menos pontos
        while len(best_moves) > 0:
            best_move = heapq.heappop(best_moves)
            ordered_moves.append(best_move.get_move())

        return ordered_moves

    #se o movimento é uma das bordas recebe prioridade
    def is_move_on_corner(self, move):
        if move == self.top_left or move == self.top_right or move == self.bottom_left or move == self.bottom_right:
            return 2

    #movimento que se afasta do centro recebe uma penalidade
    def off_center_move(self, move):
        center = 3.5
        penalty = move[0] - center
        return abs(penalty)


    def is_move_in_danger_zone(self, a_board, move):
        danger_column_left = 1
        danger_column_right = 6
        danger_line_top = 1
        danger_line_bottom = 6

        if move[0] == 6 & (move[1] > 0 & move[1 < 7]):
            return True

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