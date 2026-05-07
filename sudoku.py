import random
from copy import deepcopy
from typing import Optional


class Sudoku:
    def __init__(self, size: int = 3) -> None:
        self.size = size
        self.row_col_length = size * size
        self.board: list[list[int]] = []
        self.solution: list[list[int]] | None = None
        self.given_cells: set[tuple[int, int]] = set()
        self.init_board()

    def init_board(self) -> None:
        self.board = [[0] * self.row_col_length for _ in range(self.row_col_length)]
        self.solution = None
        self.given_cells = set()

    def get_subgrid_positions(self, row_idx: int, col_idx: int) -> list[tuple[int, int]]:
        if not (0 <= row_idx < self.size and 0 <= col_idx < self.size):
            return []
        return [
            (row_idx * self.size + r, col_idx * self.size + c)
            for r in range(self.size)
            for c in range(self.size)
        ]

    def is_valid_placement(self, row_idx: int, col_idx: int, num: int) -> bool:
        if not (1 <= num <= self.row_col_length):
            return False
        if not (0 <= row_idx < self.row_col_length and 0 <= col_idx < self.row_col_length):
            return False

        for c in range(self.row_col_length):
            if c != col_idx and self.board[row_idx][c] == num:
                return False

        for r in range(self.row_col_length):
            if r != row_idx and self.board[r][col_idx] == num:
                return False

        for r, c in self.get_subgrid_positions(row_idx // self.size, col_idx // self.size):
            if (r, c) != (row_idx, col_idx) and self.board[r][c] == num:
                return False

        return True

    def can_place(self, row_idx: int, col_idx: int, num: int) -> bool:
        if not (0 <= row_idx < self.row_col_length and 0 <= col_idx < self.row_col_length):
            return False
        return self.board[row_idx][col_idx] == 0 and self.is_valid_placement(row_idx, col_idx, num)

    def get_candidates(self, row_idx: int, col_idx: int) -> list[int]:
        if self.board[row_idx][col_idx] != 0:
            return []
        return [num for num in range(1, self.row_col_length + 1) if self.can_place(row_idx, col_idx, num)]

    def find_empty_cell(self) -> Optional[tuple[int, int]]:
        best_cell = None
        best_count = self.row_col_length + 1

        for r in range(self.row_col_length):
            for c in range(self.row_col_length):  
                if self.board[r][c] == 0:
                    count = len(self.get_candidates(r, c))
                    if count < best_count:
                        best_cell = (r, c)
                        best_count = count
                        if count == 0:
                            return best_cell
        return best_cell

    def generate_full_solution(self) -> bool:
        base = self.size
        side = self.row_col_length

        def pattern(row: int, col: int) -> int:
            return (base * (row % base) + row // base + col) % side

        def shuffled(values: range) -> list[int]:
            values = list(values)
            random.shuffle(values)
            return values

        rows = [group * base + row for group in shuffled(range(base)) for row in shuffled(range(base))]
        cols = [group * base + col for group in shuffled(range(base)) for col in shuffled(range(base))]
        nums = shuffled(range(1, side + 1))

        self.board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        self.solution = deepcopy(self.board)
        self.given_cells = {(r, c) for r in range(side) for c in range(side)}
        return True

    def generate_puzzle(self, blanks: int = 40) -> bool:
        max_blanks = self.row_col_length * self.row_col_length
        blanks = max(0, min(blanks, max_blanks))

        if not self.generate_full_solution():
            return False

        cells = [(r, c) for r in range(self.row_col_length) for c in range(self.row_col_length)]
        random.shuffle(cells)

        for r, c in cells[:blanks]:
            self.board[r][c] = 0

        self.given_cells = {
            (r, c)
            for r in range(self.row_col_length)
            for c in range(self.row_col_length)
            if self.board[r][c] != 0
        }
        return True

    def is_complete_and_valid(self) -> bool:
        return all(
            self.board[r][c] != 0 and self.is_valid_placement(r, c, self.board[r][c])
            for r in range(self.row_col_length)
            for c in range(self.row_col_length)
        )