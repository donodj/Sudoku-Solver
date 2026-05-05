import random
from copy import deepcopy
from typing import Optional


class Sudoku:
    def __init__(self, size: int = 3) -> None:
        #size=3 creates a normal 9x9 Sudoku board.
        #size=2 creates a 4x4 board.
        #size=4 creates a 16x16 board.
        self.size = size
        self.row_col_length = self.size * self.size
        self.board: list[list[int]] = []
        self.solution: list[list[int]] | None = None
        self.given_cells: set[tuple[int, int]] = set()
        self.init_board()


    def init_board(self) -> None:
        self.board = []
        for _ in range(self.row_col_length):
            row = [0] * self.row_col_length
            self.board.append(row)
        self.given_cells = set()


    def get_subgrid_positions(self, row_idx: int, col_idx: int) -> list[tuple[int, int]]:
        #row_idx and col_idx here are SUBGRID indexes.
        #For a normal 9x9 board, valid values are 0, 1, 2.
        if row_idx < 0 or row_idx >= self.size or col_idx < 0 or col_idx >= self.size:
            return []

        positions = []
        for i in range(self.size):
            for j in range(self.size):
                positions.append((row_idx * self.size + i, col_idx * self.size + j))
        return positions


    def is_valid_placement(self, row_idx: int, col_idx: int, num: int) -> bool:
        #Checks whether num can legally appear at board[row_idx][col_idx].
        #This does NOT care whether the cell is currently empty, so it is useful
        #for both solving and checking a completed board.
        if num < 1 or num > self.row_col_length:
            return False
        if row_idx < 0 or row_idx >= self.row_col_length:
            return False
        if col_idx < 0 or col_idx >= self.row_col_length:
            return False

        for c in range(self.row_col_length):
            if c != col_idx and self.board[row_idx][c] == num:
                return False

        for r in range(self.row_col_length):
            if r != row_idx and self.board[r][col_idx] == num:
                return False

        subgrid_row = row_idx // self.size
        subgrid_col = col_idx // self.size
        for r, c in self.get_subgrid_positions(subgrid_row, subgrid_col):
            if (r, c) != (row_idx, col_idx) and self.board[r][c] == num:
                return False

        return True


    def can_place(self, row_idx: int, col_idx: int, num: int) -> bool:
        #Used for player moves and DFS. A move is only legal if the cell is empty
        #AND the number does not break Sudoku rules.
        if row_idx < 0 or row_idx >= self.row_col_length:
            return False
        if col_idx < 0 or col_idx >= self.row_col_length:
            return False
        if self.board[row_idx][col_idx] != 0:
            return False
        return self.is_valid_placement(row_idx, col_idx, num)


    def get_candidates(self, row_idx: int, col_idx: int) -> list[int]:
        """Returns all numbers that can legally go in one empty cell."""
        if self.board[row_idx][col_idx] != 0:
            return []
        return [
            num
            for num in range(1, self.row_col_length + 1)
            if self.can_place(row_idx, col_idx, num)
        ]


    def find_empty_cell(self) -> Optional[tuple[int, int]]:
        #Finds an empty cell. Empty cells are represented by 0.

        #This uses a small DFS improvement called MRV: choose the empty cell with
        #the fewest legal moves. It is still DFS/backtracking, but it avoids a lot
        #of unnecessary branches.
        best_cell = None
        best_candidate_count = self.row_col_length + 1

        for r in range(self.row_col_length):
            for c in range(self.row_col_length):
                if self.board[r][c] == 0:
                    candidate_count = len(self.get_candidates(r, c))
                    if candidate_count < best_candidate_count:
                        best_candidate_count = candidate_count
                        best_cell = (r, c)

                        if candidate_count == 0:
                            return best_cell

        return best_cell


    def generate_full_solution(self) -> bool:
        #Quickly fills the whole board with a valid solved Sudoku grid.
        #This uses a standard Sudoku pattern and shuffles rows, columns, and
        #numbers. The DFS solver is then used for solving puzzles made from it.

        base = self.size
        side = self.row_col_length

        def pattern(row: int, col: int) -> int:
            return (base * (row % base) + row // base + col) % side

        def shuffled(sequence: range) -> list[int]:
            values = list(sequence)
            random.shuffle(values)
            return values

        row_groups = shuffled(range(base))
        rows = [group * base + row for group in row_groups for row in shuffled(range(base))]

        col_groups = shuffled(range(base))
        cols = [group * base + col for group in col_groups for col in shuffled(range(base))]

        nums = shuffled(range(1, side + 1))

        self.board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        self.solution = deepcopy(self.board)
        self.given_cells = {(r, c) for r in range(side) for c in range(side)}
        return True


    def generate_puzzle(self, blanks: int = 40) -> bool:
        #Creates a Sudoku puzzle by generating a complete solution and then removing some numbers.

        #blanks controls how many cells are removed. For a normal 9x9 board:
        #- 30 blanks is easier
        #- 40 blanks is medium-ish
        #- 50+ blanks is harder, but this simple version does not guarantee uniqueness
        if blanks < 0:
            blanks = 0
        max_blanks = self.row_col_length * self.row_col_length
        if blanks > max_blanks:
            blanks = max_blanks

        if not self.generate_full_solution():
            return False

        cells = [(r, c) for r in range(self.row_col_length) for c in range(self.row_col_length)]
        random.shuffle(cells)

        for i in range(blanks):
            r, c = cells[i]
            self.board[r][c] = 0

        self.given_cells = {
            (r, c)
            for r in range(self.row_col_length)
            for c in range(self.row_col_length)
            if self.board[r][c] != 0
        }
        return True


    def is_complete_and_valid(self) -> bool:
        #Returns True only if the board is full and every placement is legal.
        for r in range(self.row_col_length):
            for c in range(self.row_col_length):
                num = self.board[r][c]
                if num == 0 or not self.is_valid_placement(r, c, num):
                    return False
        return True


    def print_board(self) -> None:
        cell_str_length = len(str(self.row_col_length))
        line_length = ((cell_str_length + 1) * self.row_col_length) + ((self.size - 1) * 2) - 1
        separator = "-" * line_length

        for i, row in enumerate(self.board):
            if i % self.size == 0 and i != 0:
                print(separator)

            for j, num in enumerate(row):
                if j % self.size == 0 and j != 0:
                    print("|", end=" ")

                cell = "." if num == 0 else str(num)
                print(f"{cell:>{cell_str_length}}", end=" ")

            print()
