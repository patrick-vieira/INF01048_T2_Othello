import sys

from common import board


class Patrick:
    def __init__(self, board, my_color):
        self.my_color = board.WHITE if my_color == 'white' else board.BLACK
        self.opponent_color = board.opponent(self.my_color)
        self.board = board

        self.available_moves = board.legal_moves(self.my_color)
        self.alfa = float('inf')  # Melhor escolha de MAX (Maior valor)
        self.beta = float('-inf')  # Melhor escolha de MIN (Menor valor)

        self.console_out = "Select your move: \n 0) Pass"

    def __get_board_score(self, board):
        # print("my>" + self.my_color + " - " + str(board.piece_count[self.my_color]))
        # print("oponent>" + self.opponent_color + " - " + str(board.piece_count[self.opponent_color]))
        scores = [board.piece_count[self.my_color], board.piece_count[self.opponent_color]]
        score = scores[0] - scores[1]
        # print(str(scores) + ' - ' + str(score))
        return score

    def __append_to_console_out(self, index, move, score):
        self.console_out += "\n " + str(index+1) + ") " + str(move) + " - Score = [" + str(score) + "]."

    def __get_player_input(self, best_move, score):
        self.console_out += "\nBest move: " + str(best_move) + " - Score = " + str(score)
        self.console_out += "\n:: "
        return input(self.console_out)

    def next_move(self, human_player=False):
        v = float('-inf')
        best_move = None

        if len(self.available_moves) > 0:  # se existe algum movimento possivel
            for i, move in enumerate(self.available_moves):  # para cada movimento disponivel
                imaginary_board = board.from_string(str(self.board))  # cria um tabuleiro "imaginario"
                score = self.min_max_max(imaginary_board)

                self.__append_to_console_out(i, move, score)

                if v < score:
                    v = score
                    best_move = move

        selected_move = self.get_selected_move(best_move, human_player, v)
        selected_move = self.execute_move(selected_move)

        return selected_move

    def execute_move(self, selected_move):
        before_move = self.__get_board_score(self.board)
        if selected_move is not None:
            self.board.process_move(selected_move, self.my_color)
        else:
            selected_move = (-1, -1)
        after_move = self.__get_board_score(self.board)
        print("Score before movement: " + str(before_move))
        print("Score after movement:  " + str(after_move))
        return selected_move

    def get_selected_move(self, best_move, human_player, v):
        selected_move = None
        if human_player:
            while selected_move is None:
                player_selected_move = int(self.__get_player_input(best_move, v))
                if player_selected_move == 0:
                    selected_move = (-1, -1)
                elif player_selected_move <= len(self.available_moves):
                    selected_move = self.available_moves[player_selected_move-1]
        else:
            selected_move = best_move
        return selected_move

    def min_max_max(self, imaginary_board):
        if len(imaginary_board.legal_moves(self.my_color)) > 0:  # se existe algum movimento possivel

            v = float('-inf')

            for move in imaginary_board.legal_moves(self.my_color):  # para cada movimento disponivel
                imaginary_board.process_move(move, self.my_color)  # executa o movimento
                # imaginary_board.print_board()

                score = self.min_max_min(imaginary_board)
                v = max(v, score)

                return v
        else:
            score = self.__get_board_score(imaginary_board)
            return score

    def min_max_min(self, imaginary_board):
        if len(imaginary_board.legal_moves(self.opponent_color)) > 0:  # se existe algum movimento possivel do oponente

            v = float('+inf')

            for opponent_move in imaginary_board.legal_moves(
                    self.opponent_color):  # para cada movimento disponivel do oponente
                imaginary_board.process_move(opponent_move, self.opponent_color)  # executa o movimento
                # imaginary_board.print_board()

                score = self.min_max_max(imaginary_board)
                v = min(v, score)

                return v
        else:
            score = self.__get_board_score(imaginary_board)
            return score


if __name__ == '__main__':
    b = board.from_file(sys.argv[1])
    f = open('move.txt', 'w')
    patrick = Patrick(b, sys.argv[2])

    human_player = False
    if sys.argv[-1] == "H" or sys.argv[-1] == "human":
        human_player = True

    f.write('%d,%d' % patrick.next_move(human_player))
    f.close()
