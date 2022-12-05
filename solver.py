
class Solver:
    DIMENSION = 9
    def __init__(self, sudoku_table):
        self.sudoku_table = sudoku_table
        self.sudoku_cp = []
        for row in sudoku_table:
            self.sudoku_cp.append(row.copy())


    def _check_row(self, row, column):
        count = 0
        for val in self.sudoku_table[row]:
            if val == self.sudoku_table[row][column]:
                count += 1
        
        return count == 1

    def _check_column(self, row, column):
        count = 0
        for i in range(self.DIMENSION):
            if self.sudoku_table[i][column] == self.sudoku_table[row][column]:
                count += 1
        
        return count == 1

    def _check_square(self, row, column):
        count = 0
        row_begin = (row // 3) * 3
        column_begin = (column // 3) * 3

        for i in range(row_begin, row_begin + 3):
            for j in range(column_begin, column_begin + 3):
                if self.sudoku_table[i][j] == self.sudoku_table[row][column]:
                    count += 1

        return count == 1  

    def _is_position_correct(self, row, column):
        return self._check_row(row, column) and \
               self._check_column(row, column) and \
               self._check_square(row, column)

    def _set_position_value(self, row, column):
        for i in range(self.sudoku_table[row][column] + 1, self.DIMENSION + 1):
            self.sudoku_table[row][column] = i
            if self._is_position_correct(row, column):
                return 
        
        self.sudoku_table[row][column] = 0

    def _get_last_empty_position(self, row, column):
        column -= 1
        while row >= 0:
            while column >= 0:
                if self.sudoku_cp[row][column] == 0:
                    return row, column
                column -= 1
            column = self.DIMENSION - 1
            row -= 1

        return row, column


    def solve(self):
        i = 0
        while i < self.DIMENSION:
            j = 0
            while j < self.DIMENSION:
                while self.sudoku_table[i][j] == 0:
                    self._set_position_value(i, j)
                    while self.sudoku_table[i][j] == 0:
                        i, j = self._get_last_empty_position(i, j)
                        if i < 0 or j < 0:
                            return False
                        self._set_position_value(i, j)
                j += 1
            i += 1

        return True
