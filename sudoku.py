import random
import tkinter as tk
from copy import deepcopy
from tkinter import messagebox, simpledialog
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

    def solve_dfs(self, randomize: bool = False) -> bool:
        #Solves the Sudoku puzzle using recursive DFS/backtracking.

        #Returns True if a solution is found, otherwise False.
        empty_cell = self.find_empty_cell()

        if empty_cell is None:
            return True

        row, col = empty_cell
        numbers = self.get_candidates(row, col)
        if randomize:
            random.shuffle(numbers)

        for num in numbers:
            self.board[row][col] = num

            if self.solve_dfs(randomize=randomize):
                return True

            self.board[row][col] = 0

        return False

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


class SudokuGUI:
    def __init__(self, root: tk.Tk, blanks: int = 40) -> None:
        self.root = root
        self.root.title("Sudoku DFS Solver")
        self.sudoku = Sudoku(size=3)
        self.blanks = blanks
        self.selected_cell: tuple[int, int] | None = None
        self.cells: list[list[tk.Label]] = []

        self.normal_bg = "white"
        self.given_bg = "#e6e6e6"
        self.selected_bg = "#cfe8ff"
        self.error_bg = "#ffcccc"

        self.build_layout()
        self.new_puzzle()

    def build_layout(self) -> None:
        outer = tk.Frame(self.root, padx=12, pady=12)
        outer.pack()

        title = tk.Label(outer, text="Sudoku", font=("Arial", 22, "bold"))
        title.pack(pady=(0, 8))

        self.board_frame = tk.Frame(outer, bg="black", bd=2, relief="solid")
        self.board_frame.pack()

        for r in range(9):
            row_cells = []
            for c in range(9):
                left = 2 if c % 3 == 0 else 1
                top = 2 if r % 3 == 0 else 1
                right = 2 if c == 8 else 0
                bottom = 2 if r == 8 else 0
                cell = tk.Label(
                    self.board_frame,
                    text="",
                    width=3,
                    height=1,
                    font=("Arial", 24),
                    bg=self.normal_bg,
                    relief="solid",
                    bd=1,
                )
                cell.grid(row=r, column=c, padx=(left, right), pady=(top, bottom), sticky="nsew")
                cell.bind("<Button-1>", lambda event, row=r, col=c: self.select_cell(row, col))
                row_cells.append(cell)
            self.cells.append(row_cells)

        keypad = tk.Frame(outer, pady=10)
        keypad.pack()
        for num in range(1, 10):
            button = tk.Button(
                keypad,
                text=str(num),
                width=4,
                font=("Arial", 14),
                command=lambda value=num: self.enter_number(value),
            )
            button.grid(row=0, column=num - 1, padx=2)

        controls = tk.Frame(outer)
        controls.pack(pady=(4, 0))

        tk.Button(controls, text="New Puzzle", command=self.ask_new_puzzle).grid(row=0, column=0, padx=4)
        tk.Button(controls, text="Solve with DFS", command=self.solve_with_dfs).grid(row=0, column=1, padx=4)
        tk.Button(controls, text="Check", command=self.check_board).grid(row=0, column=2, padx=4)
        tk.Button(controls, text="Clear Selected", command=self.clear_selected).grid(row=0, column=3, padx=4)

        self.status = tk.Label(outer, text="", font=("Arial", 11), anchor="w")
        self.status.pack(fill="x", pady=(8, 0))

        self.root.bind("<Key>", self.handle_keypress)

    def new_puzzle(self) -> None:
        self.sudoku.generate_puzzle(blanks=self.blanks)
        self.selected_cell = None
        self.status.config(text=f"New puzzle generated with {self.blanks} blanks.")
        self.refresh_board()

    def ask_new_puzzle(self) -> None:
        blanks = simpledialog.askinteger(
            "New Puzzle",
            "How many blanks? Easy: 30, Medium: 40, Hard: 50",
            initialvalue=self.blanks,
            minvalue=0,
            maxvalue=81,
        )
        if blanks is not None:
            self.blanks = blanks
            self.new_puzzle()

    def select_cell(self, row: int, col: int) -> None:
        self.selected_cell = (row, col)
        self.refresh_board()

        if (row, col) in self.sudoku.given_cells:
            self.status.config(text="That is a starting number, so it cannot be changed.")
        else:
            self.status.config(text=f"Selected row {row + 1}, column {col + 1}.")

    def enter_number(self, num: int) -> None:
        if self.selected_cell is None:
            self.status.config(text="Select an empty square first.")
            return

        row, col = self.selected_cell
        if (row, col) in self.sudoku.given_cells:
            self.status.config(text="You cannot change a starting number.")
            return

        old_value = self.sudoku.board[row][col]
        self.sudoku.board[row][col] = 0

        if self.sudoku.can_place(row, col, num):
            self.sudoku.board[row][col] = num
            self.status.config(text=f"Placed {num} at row {row + 1}, column {col + 1}.")
        else:
            self.sudoku.board[row][col] = old_value
            self.status.config(text=f"{num} cannot legally go there.")
            self.flash_cell(row, col)

        self.refresh_board()

        if self.sudoku.is_complete_and_valid():
            messagebox.showinfo("Sudoku", "Congratulations, you solved it!")

    def clear_selected(self) -> None:
        if self.selected_cell is None:
            self.status.config(text="Select a square to clear.")
            return

        row, col = self.selected_cell
        if (row, col) in self.sudoku.given_cells:
            self.status.config(text="You cannot clear a starting number.")
            return

        self.sudoku.board[row][col] = 0
        self.status.config(text=f"Cleared row {row + 1}, column {col + 1}.")
        self.refresh_board()

    def solve_with_dfs(self) -> None:
        board_before_solving = deepcopy(self.sudoku.board)
        if self.sudoku.solve_dfs():
            self.status.config(text="Solved with DFS/backtracking.")
            self.refresh_board()
        else:
            self.sudoku.board = board_before_solving
            self.status.config(text="No solution exists for this board.")
            messagebox.showerror("Sudoku", "No solution exists for this board.")

    def check_board(self) -> None:
        has_errors = False
        incomplete = False

        for r in range(9):
            for c in range(9):
                num = self.sudoku.board[r][c]
                if num == 0:
                    incomplete = True
                elif not self.sudoku.is_valid_placement(r, c, num):
                    has_errors = True

        self.refresh_board(show_errors=True)

        if has_errors:
            self.status.config(text="There are conflicts on the board.")
            messagebox.showwarning("Check Board", "There are conflicts on the board.")
        elif incomplete:
            self.status.config(text="No conflicts so far, but the puzzle is not complete yet.")
            messagebox.showinfo("Check Board", "No conflicts so far, but the puzzle is not complete yet.")
        else:
            self.status.config(text="The board is complete and valid!")
            messagebox.showinfo("Check Board", "The board is complete and valid!")

    def handle_keypress(self, event: tk.Event) -> None:
        char = event.char
        if char in "123456789":
            self.enter_number(int(char))
        elif event.keysym in {"BackSpace", "Delete", "0"}:
            self.clear_selected()

    def refresh_board(self, show_errors: bool = False) -> None:
        for r in range(9):
            for c in range(9):
                value = self.sudoku.board[r][c]
                label = self.cells[r][c]
                label.config(text="" if value == 0 else str(value))

                if self.selected_cell == (r, c):
                    bg = self.selected_bg
                elif (r, c) in self.sudoku.given_cells:
                    bg = self.given_bg
                else:
                    bg = self.normal_bg

                if show_errors and value != 0 and not self.sudoku.is_valid_placement(r, c, value):
                    bg = self.error_bg

                label.config(bg=bg)

                if (r, c) in self.sudoku.given_cells:
                    label.config(fg="black", font=("Arial", 24, "bold"))
                else:
                    label.config(fg="#2255aa", font=("Arial", 24))

    def flash_cell(self, row: int, col: int) -> None:
        self.cells[row][col].config(bg=self.error_bg)
        self.root.after(250, self.refresh_board)


def play_game() -> None:
    sudoku = Sudoku(size=3)
    sudoku.generate_puzzle(blanks=40)

    print("Generated Sudoku puzzle:")
    sudoku.print_board()

    while True:
        print("\nOptions:")
        print("1. Enter a move as row, column, number")
        print("2. Type 'solve' to solve with DFS")
        print("3. Type 'new' to generate a new puzzle")
        print("4. Type 'quit' to stop")

        inp = input("Your choice: ").strip().lower()

        if inp == "quit":
            break

        if inp == "solve":
            if sudoku.solve_dfs():
                print("\nSolved with DFS/backtracking:")
                sudoku.print_board()
            else:
                print("No solution exists for this board.")
            continue

        if inp == "new":
            sudoku.generate_puzzle(blanks=40)
            print("\nNew puzzle:")
            sudoku.print_board()
            continue

        input_nums = inp.split(",")
        if len(input_nums) != 3:
            print("Error: Expected exactly 3 integers, like: 1, 2, 9")
            continue

        try:
            row, col, num = input_nums
            row, col, num = int(row) - 1, int(col) - 1, int(num)
        except ValueError:
            print("Error: row, column, and number must be integers.")
            continue

        if sudoku.can_place(row, col, num):
            sudoku.board[row][col] = num
            sudoku.print_board()

            if sudoku.is_complete_and_valid():
                print("Congratulations, you solved it!")
                break
        else:
            print("Invalid placement")


def run_gui() -> None:
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
