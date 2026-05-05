import tkinter as tk
from copy import deepcopy
from tkinter import messagebox, simpledialog
from sudoku import Sudoku
import solvers


class SudokuGUI:
    def __init__(self, root: tk.Tk, size: int = 3, blanks: int = 40) -> None:
        self.root = root
        self.root.title("Sudoku DFS Solver")
        self.sudoku = Sudoku(size)
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

        size = self.sudoku.size
        row_col_length = self.sudoku.row_col_length

        for r in range(row_col_length):
            row_cells = []
            for c in range(row_col_length):
                left = 2 if c % size == 0 else 1
                top = 2 if r % size == 0 else 1
                right = 2 if c == row_col_length - 1 else 0
                bottom = 2 if r == row_col_length - 1 else 0
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
        for num in range(1, row_col_length + 1):
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
            maxvalue=self.sudoku.row_col_length * self.sudoku.row_col_length,
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
        if solvers.solve_dfs(self.sudoku):
            self.status.config(text="Solved with DFS/backtracking.")
            self.refresh_board()
        else:
            self.sudoku.board = board_before_solving
            self.status.config(text="No solution exists for this board.")
            messagebox.showerror("Sudoku", "No solution exists for this board.")


    def check_board(self) -> None:
        has_errors = False
        incomplete = False

        for r in range(self.sudoku.row_col_length):
            for c in range(self.sudoku.row_col_length):
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
        for r in range(self.sudoku.row_col_length):
            for c in range(self.sudoku.row_col_length):
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


def play_game(size: int = 3, blanks: int = 40) -> None:
    sudoku = Sudoku(size)
    sudoku.generate_puzzle(blanks)

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
            if solvers.solve_dfs(sudoku):
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
    SudokuGUI(root, size=3)
    root.mainloop()
