
class MoveScore:
    def __init__(self, move, score, color):
        self.move = move
        self.score = score
        self.color = color

    def get_move(self):
        return self.move

    def get_score(self):
        return self.score

    def __str__(self):
        to_string = "Move [" + str(self.move) + "] Score: " + str(self.score) + " - Color: " + str(self.color)
        return to_string

    def __repr__(self):  # função para visualizar os valores no debbuger sem precisar abrir o objeto
        return self.__str__()

    def __eq__(self, other):  # função para comparar movimentos
        """Overrides the default implementation"""
        if isinstance(other, MoveScore):
            return self.move == other.move \
                   and self.score == other.score \
                   and self.color == other.color

        return NotImplemented

    def __hash__(self):  # hash unico para cada movimento
        """Overrides the default implementation"""
        return hash(self.move) ^ hash(self.score) ^ hash(self.color)

    def __lt__(self, other):  # Usado na comparação de ordenação
        if isinstance(other, MoveScore):
            return self.score < other.score

        return NotImplemented

