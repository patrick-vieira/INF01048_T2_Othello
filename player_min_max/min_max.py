import sys

from common import board
from player_min_max.monitor_performance import MonitorPerformance


class MinMax:
    def __init__(self, board, my_color):
        self.my_color = board.WHITE if my_color == 'white' else board.BLACK
        self.opponent_color = board.opponent(self.my_color)
        self.board = board

        self.available_moves = board.legal_moves(self.my_color)

    def __get_board_score(self, board):
        scores = [board.piece_count[self.my_color], board.piece_count[self.opponent_color]]
        score = scores[0] - scores[1]
        return score

    def next_move_min_max(self, max_depth):
        v = float('-inf')
        best_move = (-1, -1)

        if len(self.available_moves) > 0:  # se existe algum movimento possivel
            for i, move in enumerate(self.available_moves):  # para cada movimento disponivel
                with MonitorPerformance(False,"evaluating move " + str(i) + "/" + str(len(self.available_moves))):
                    imaginary_board = board.from_string(str(self.board))  # cria um tabuleiro "imaginario"
                    score = self.min_max_max(imaginary_board, max_depth)

                    if v < score:
                        v = score
                        best_move = move

        self.show_move_result(best_move)

        return best_move

    def show_move_result(self, selected_move):
        before_move = self.__get_board_score(self.board)
        self.board.process_move(selected_move, self.my_color)
        after_move = self.__get_board_score(self.board)

        print("Score before movement: " + str(before_move))
        print("Score after movement:  " + str(after_move))

        return selected_move

    def min_max_max(self, a_board, max_depth):
        # se existe algum movimento possivel
        if (len(a_board.legal_moves(self.my_color)) > 0) and (max_depth > 0):
            depth = max_depth - 1

            v = float('-inf')

            for move in a_board.legal_moves(self.my_color):  # para cada movimento disponivel
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(move, self.my_color)  # executa o movimento
                #imaginary_board.print_board()

                score = self.min_max_min(imaginary_board, depth)
                v = max(v, score)

            return v
        else:
            score = self.__get_board_score(a_board)
            return score

    def min_max_min(self, a_board, max_depth):
        # se existe algum movimento possivel do oponente
        if (len(a_board.legal_moves(self.opponent_color)) > 0) and (max_depth > 0):
            depth = max_depth - 1

            v = float('+inf')

            for opponent_move in a_board.legal_moves(self.opponent_color):  # para cada movimento disponivel do oponente
                imaginary_board = board.from_string(str(a_board))
                imaginary_board.process_move(opponent_move, self.opponent_color)  # executa o movimento
                #imaginary_board.print_board()

                score = self.min_max_max(imaginary_board, depth)
                v = min(v, score)

            return v
        else:
            score = self.__get_board_score(a_board)
            return score


if __name__ == '__main__':
    b = board.from_file(sys.argv[1])
    f = open('move.txt', 'w')
    patrick = MinMax(b, sys.argv[2])

    with MonitorPerformance(True):
        movement = patrick.next_move_min_max(2)

    f.write('%d,%d' % movement)

    f.close()
