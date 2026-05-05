import random
from sudoku import Sudoku


def solve_dfs(game: Sudoku, randomize: bool = False) -> bool:
    #Solves the Sudoku puzzle using recursive DFS/backtracking.

    #Returns True if a solution is found, otherwise False.
    empty_cell = game.find_empty_cell()

    if empty_cell is None:
        return True

    row, col = empty_cell
    numbers = game.get_candidates(row, col)
    if randomize:
        random.shuffle(numbers)

    for num in numbers:
        game.board[row][col] = num

        if solve_dfs(game, randomize=randomize):
            return True

        game.board[row][col] = 0

    return False