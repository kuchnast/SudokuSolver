DIMENSION = 9

def check_row(sudoku_table, row, column):
    count = 0
    for val in sudoku_table[row]:
        if val == sudoku_table[row][column]:
            count += 1
    
    return count == 1

def check_column(sudoku_table, row, column):
    count = 0
    for i in range(DIMENSION):
        if sudoku_table[i][column] == sudoku_table[row][column]:
            count += 1
    
    return count == 1

def check_square(sudoku_table, row, column):
    count = 0
    row_begin = (row // 3) * 3
    column_begin = (column // 3) * 3

    for i in range(row_begin, row_begin + 3):
        for j in range(column_begin, column_begin + 3):
            if sudoku_table[i][j] == sudoku_table[row][column]:
                count += 1

    return count == 1  

def is_position_correct(sudoku_table, row, column):
    return check_row(sudoku_table, row, column) and \
       check_column(sudoku_table, row, column) and \
       check_square(sudoku_table, row, column)

def set_position_value(sudoku_table, row, column):
    for i in range(sudoku_table[row][column] + 1, DIMENSION + 1):
        sudoku_table[row][column] = i
        if is_position_correct(sudoku_table, row, column):
            return 
    
    sudoku_table[row][column] = 0

def get_last_empty_position(sudoku_cp, row, column):
    column -= 1
    while row >= 0:
        while column >= 0:
            if sudoku_cp[row][column] == 0:
                return row, column
            column -= 1
        column = DIMENSION - 1
        row -= 1

    return row, column


def solve(sudoku_table):
    sudoku_cp = []
    for row in sudoku_table:
        sudoku_cp.append(row.copy())

    i = 0
    while i < DIMENSION:
        j = 0
        while j < DIMENSION:
            while sudoku_table[i][j] == 0:
                set_position_value(sudoku_table, i, j)
                while sudoku_table[i][j] == 0:
                    i, j = get_last_empty_position(sudoku_cp, i, j)
                    set_position_value(sudoku_table, i, j)
                    if i < 0 or j < 0:
                        return False
            j += 1
        i += 1
