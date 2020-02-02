class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.squares = []
        self.mines = mines
        self.empties = []
        for i in range(rows):
            self.squares.append([])
            for j in range(cols):
                self.squares[i].append('E')
                self.empties.append((i, j))

    def is_empty(self, coord):
        i, j = coord
        return self.squares[i][j] == 'E'

