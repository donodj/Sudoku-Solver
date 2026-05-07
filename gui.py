import time
import tkinter as tk
from copy import deepcopy
from tkinter import simpledialog

from sudoku import Sudoku
import solvers


class SolverPanel:
    def __init__(self, parent: tk.Widget, title: str, size: int = 3) -> None:
        self.title = title
        self.size = size
        self.side = size * size
        self.cells: list[list[tk.Label]] = []
        self.generator = None
        self.running = False
        self.done = False
        self.steps = 0
        self.start_time: float | None = None
        self.elapsed = 0.0

        self.normal_bg = "white"
        self.given_bg = "#e6e6e6"
        self.solve_bg = "#eaf3ff"

        self.frame = tk.Frame(parent, padx=8, pady=8, bd=2, relief="groove")
        tk.Label(self.frame, text=title, font=("Arial", 14, "bold")).pack(pady=(0, 4))

        board_frame = tk.Frame(self.frame, bg="black", bd=2, relief="solid")
        board_frame.pack()

        for r in range(self.side):
            row_cells = []
            for c in range(self.side):
                cell = tk.Label(
                    board_frame,
                    text="",
                    width=2,
                    height=1,
                    font=("Arial", 13),
                    bg=self.normal_bg,
                    relief="solid",
                    bd=1,
                )
                cell.grid(
                    row=r,
                    column=c,
                    padx=(2 if c % size == 0 else 1, 2 if c == self.side - 1 else 0),
                    pady=(2 if r % size == 0 else 1, 2 if r == self.side - 1 else 0),
                    sticky="nsew",
                )
                row_cells.append(cell)
            self.cells.append(row_cells)

        self.timer_label = tk.Label(self.frame, text="Time: 0.0000 s", font=("Arial", 10))
        self.timer_label.pack(pady=(6, 0))
        self.steps_label = tk.Label(self.frame, text="Steps: 0", font=("Arial", 10))
        self.steps_label.pack()
        self.status_label = tk.Label(self.frame, text="Ready", font=("Arial", 10), width=22)
        self.status_label.pack()

    def set_board(self, board: list[list[int]], given_cells: set[tuple[int, int]]) -> None:
        for r in range(self.side):
            for c in range(self.side):
                value = board[r][c]
                cell = self.cells[r][c]
                cell.config(text="" if value == 0 else str(value))

                if (r, c) in given_cells:
                    cell.config(bg=self.given_bg, fg="black", font=("Arial", 13, "bold"))
                else:
                    cell.config(bg=self.solve_bg if value else self.normal_bg, fg="#2255aa", font=("Arial", 13))

    def reset(self, board: list[list[int]], given_cells: set[tuple[int, int]]) -> None:
        self.generator = None
        self.running = False
        self.done = False
        self.steps = 0
        self.start_time = None
        self.elapsed = 0.0
        self.set_board(board, given_cells)
        self.timer_label.config(text="Time: 0.0000 s")
        self.steps_label.config(text="Steps: 0")
        self.status_label.config(text="Ready")

    def start(self, board: list[list[int]], given_cells: set[tuple[int, int]], generator_function) -> None:
        self.reset(board, given_cells)
        self.generator = generator_function(board, self.size)
        self.running = True
        self.start_time = time.perf_counter()
        self.status_label.config(text="Running")

    def stop(self) -> None:
        if self.running and self.start_time is not None:
            self.elapsed = time.perf_counter() - self.start_time
        self.running = False
        self.start_time = None
        self.update_timer()
        if not self.done:
            self.status_label.config(text="Stopped")

    def current_elapsed(self) -> float:
        if self.running and self.start_time is not None:
            return time.perf_counter() - self.start_time
        return self.elapsed

    def update_timer(self) -> None:
        self.timer_label.config(text=f"Time: {self.current_elapsed():.4f} s")

    def finish(self) -> None:
        if self.start_time is not None:
            self.elapsed = time.perf_counter() - self.start_time
        self.running = False
        self.done = True
        self.start_time = None
        self.update_timer()

    def advance(self, given_cells: set[tuple[int, int]], max_updates: int = 20) -> None:
        if not self.running or self.done or self.generator is None:
            self.update_timer()
            return

        try:
            update = None
            for _ in range(max_updates):
                update = next(self.generator)
                if update[3]:
                    break

            if update is None:
                return

            board, steps, status, done = update
            self.steps = steps
            self.set_board(board, given_cells)
            self.steps_label.config(text=f"Steps: {steps}")
            self.status_label.config(text=status)
            self.update_timer()

            if done:
                self.finish()
        except StopIteration:
            self.finish()
            if self.status_label.cget("text") == "Running":
                self.status_label.config(text="Finished")


class SudokuCompareGUI:
    def __init__(self, root: tk.Tk, size: int = 3, blanks: int = 40) -> None:
        self.root = root
        self.root.title("Sudoku Solver Comparison")
        self.sudoku = Sudoku(size)
        self.size = size
        self.side = size * size
        self.blanks = blanks
        self.solving = False
        self.puzzle_board: list[list[int]] = []
        self.given_cells: set[tuple[int, int]] = set()
        self.panels: dict[str, SolverPanel] = {}

        self.build_layout()
        self.new_puzzle()

    def build_layout(self) -> None:
        outer = tk.Frame(self.root, padx=12, pady=12)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Sudoku Solver Comparison", font=("Arial", 22, "bold")).pack(pady=(0, 4))
        tk.Label(
            outer,
            text="Same puzzle solved at the same time with DFS, Knuth Algorithm X, heuristics, and CSP.",
            font=("Arial", 11),
        ).pack(pady=(0, 8))

        controls = tk.Frame(outer)
        controls.pack(pady=(0, 10))
        tk.Button(controls, text="New Puzzle", command=self.ask_new_puzzle).grid(row=0, column=0, padx=4)
        tk.Button(controls, text="Run All Solvers", command=self.run_all_solvers).grid(row=0, column=1, padx=4)
        tk.Button(controls, text="Stop", command=self.stop_all).grid(row=0, column=2, padx=4)
        tk.Button(controls, text="Reset Views", command=self.reset_views).grid(row=0, column=3, padx=4)

        self.status = tk.Label(outer, text="", font=("Arial", 11), anchor="w")
        self.status.pack(fill="x", pady=(0, 8))

        panels_frame = tk.Frame(outer)
        panels_frame.pack()

        for idx, name in enumerate(solvers.SOLVER_GENERATORS):
            panel = SolverPanel(panels_frame, name, self.size)
            panel.frame.grid(row=0, column=idx, padx=6, sticky="n")
            self.panels[name] = panel

    def new_puzzle(self) -> None:
        self.stop_all(update_status=False)
        self.sudoku.generate_puzzle(blanks=self.blanks)
        self.puzzle_board = deepcopy(self.sudoku.board)
        self.given_cells = set(self.sudoku.given_cells)
        self.reset_views()
        self.status.config(text=f"New puzzle generated with {self.blanks} blanks. Click Run All Solvers to compare.")

    def ask_new_puzzle(self) -> None:
        blanks = simpledialog.askinteger(
            "New Puzzle",
            "How many blanks? Easy: 30, Medium: 40, Hard: 50",
            initialvalue=self.blanks,
            minvalue=0,
            maxvalue=self.side * self.side,
        )
        if blanks is not None:
            self.blanks = blanks
            self.new_puzzle()

    def reset_views(self) -> None:
        self.solving = False
        for panel in self.panels.values():
            panel.reset(self.puzzle_board, self.given_cells)

    def run_all_solvers(self) -> None:
        if not self.puzzle_board:
            self.new_puzzle()

        self.solving = True
        for name, panel in self.panels.items():
            panel.start(self.puzzle_board, self.given_cells, solvers.SOLVER_GENERATORS[name])
        self.status.config(text="All four solvers are running on the same puzzle.")
        self.root.after(1, self.tick)

    def tick(self) -> None:
        any_running = False
        for panel in self.panels.values():
            panel.advance(self.given_cells)
            any_running = any_running or panel.running

        if any_running and self.solving:
            self.root.after(10, self.tick)
        else:
            self.solving = False
            self.status.config(text="Comparison finished. Lower time and fewer steps means that method solved this puzzle faster.")

    def stop_all(self, update_status: bool = True) -> None:
        self.solving = False
        for panel in self.panels.values():
            panel.stop()
        if update_status:
            self.status.config(text="Stopped all solvers.")


def run_compare_gui() -> None:
    root = tk.Tk()
    SudokuCompareGUI(root, size=3)
    root.mainloop()