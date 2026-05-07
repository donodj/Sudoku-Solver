from typing import Generator, Optional

from sudoku import Sudoku

Board = list[list[int]]
SolverYield = tuple[Board, int, str, bool]


def clone_board(board: Board) -> Board:
    return [row[:] for row in board]


def legal_numbers(board: Board, row: int, col: int, size: int = 3) -> list[int]:
    if board[row][col] != 0:
        return []

    side = size * size
    used = set(board[row]) | {board[r][col] for r in range(side)}
    box_row = row // size * size
    box_col = col // size * size

    for r in range(box_row, box_row + size):
        for c in range(box_col, box_col + size):
            used.add(board[r][c])

    return [num for num in range(1, side + 1) if num not in used]


def is_valid_board(board: Board, size: int = 3) -> bool:
    side = size * size

    for r in range(side):
        seen: set[int] = set()
        for c in range(side):
            num = board[r][c]
            if num and num in seen:
                return False
            seen.add(num) if num else None

    for c in range(side):
        seen = set()
        for r in range(side):
            num = board[r][c]
            if num and num in seen:
                return False
            seen.add(num) if num else None

    for box_r in range(0, side, size):
        for box_c in range(0, side, size):
            seen = set()
            for r in range(box_r, box_r + size):
                for c in range(box_c, box_c + size):
                    num = board[r][c]
                    if num and num in seen:
                        return False
                    seen.add(num) if num else None

    return True


def solve_dfs(game: Sudoku, randomize: bool = False) -> bool:
    import random

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


def dfs_generator(start_board: Board, size: int = 3) -> Generator[SolverYield, None, None]:
    board = clone_board(start_board)
    steps = 0
    side = size * size

    if not is_valid_board(board, size):
        yield clone_board(board), steps, "Invalid start", True
        return

    def find_first_empty() -> Optional[tuple[int, int]]:
        for r in range(side):
            for c in range(side):
                if board[r][c] == 0:
                    return r, c
        return None

    def search() -> Generator[SolverYield, None, bool]:
        nonlocal steps
        cell = find_first_empty()
        if cell is None:
            return True

        row, col = cell
        for num in range(1, side + 1):
            if num in legal_numbers(board, row, col, size):
                board[row][col] = num
                steps += 1
                yield clone_board(board), steps, "Running", False

                if (yield from search()):
                    return True

                board[row][col] = 0
                steps += 1
                yield clone_board(board), steps, "Backtracking", False
        return False

    solved = yield from search()
    yield clone_board(board), steps, "Solved" if solved else "No solution", True


def heuristic_generator(start_board: Board, size: int = 3) -> Generator[SolverYield, None, None]:
    board = clone_board(start_board)
    steps = 0
    side = size * size

    if not is_valid_board(board, size):
        yield clone_board(board), steps, "Invalid start", True
        return

    def choose_cell() -> Optional[tuple[int, int, list[int]]]:
        best: tuple[int, int, list[int]] | None = None
        for r in range(side):
            for c in range(side):
                if board[r][c] == 0:
                    candidates = legal_numbers(board, r, c, size)
                    if best is None or len(candidates) < len(best[2]):
                        best = (r, c, candidates)
                        if not candidates:
                            return best
        return best

    def lcv_order(row: int, col: int, candidates: list[int]) -> list[int]:
        peers = {(row, i) for i in range(side)} | {(i, col) for i in range(side)}
        box_row = row // size * size
        box_col = col // size * size
        peers |= {(r, c) for r in range(box_row, box_row + size) for c in range(box_col, box_col + size)}
        peers.discard((row, col))

        def conflicts(num: int) -> int:
            board[row][col] = num
            eliminated = sum (1 
                for r, c in peers
                if board[r][c] == 0 and num in legal_numbers(board, r, c, size))
            board[row][col] = 0
            return eliminated
        return sorted(candidates, key=conflicts)

    def search() -> Generator[SolverYield, None, bool]:
        nonlocal steps
        chosen = choose_cell()
        if chosen is None:
            return True

        row, col, candidates = chosen
        if not candidates:  
            return False

        for num in lcv_order(row, col, candidates):
            board[row][col] = num
            steps += 1
            yield clone_board(board), steps, "Running", False

            if (yield from search()):
                return True

            board[row][col] = 0
            steps += 1
            yield clone_board(board), steps, "Backtracking", False
        return False

    solved = yield from search()
    yield clone_board(board), steps, "Solved" if solved else "No solution", True


def csp_generator(start_board: Board, size: int = 3) -> Generator[SolverYield, None, None]:
    board = clone_board(start_board)
    steps = 0
    side = size * size
    cells = [(r, c) for r in range(side) for c in range(side)]

    if not is_valid_board(board, size):
        yield clone_board(board), steps, "Invalid start", True
        return

    peers: dict[tuple[int, int], set[tuple[int, int]]] = {}
    for r, c in cells:
        box_row = r // size * size
        box_col = c // size * size
        peer_set = {(r, i) for i in range(side)} | {(i, c) for i in range(side)}
        peer_set |= {(rr, cc) for rr in range(box_row, box_row + size) for cc in range(box_col, box_col + size)}
        peer_set.discard((r, c))
        peers[(r, c)] = peer_set

    def initial_domains() -> Optional[dict[tuple[int, int], set[int]]]:
        domains = {}
        for r, c in cells:
            values = {board[r][c]} if board[r][c] else set(legal_numbers(board, r, c, size))
            if not values:
                return None
            domains[(r, c)] = values
        return domains

    def propagate(domains: dict[tuple[int, int], set[int]], queue: list[tuple[int, int]],track_steps: bool = False) -> bool:
        nonlocal steps
        while queue:
            cell = queue.pop()
            if len(domains[cell]) != 1:
                continue

            value = next(iter(domains[cell]))
            for peer in peers[cell]:
                if value in domains[peer] and len(domains[peer]) > 1:
                    domains[peer] = set(domains[peer])
                    domains[peer].remove(value)
                    if not domains[peer]:
                        return False
                    if len(domains[peer]) == 1:
                        queue.append(peer)
                        if track_steps:
                            steps += 1
        return True
    def domains_to_board(domains: dict[tuple[int, int], set[int]]) -> Board:
        return [
            [next(iter(domains[(r, c)])) if len(domains[(r, c)]) == 1 else 0 for c in range(side)]
            for r in range(side)
        ]

    domains = initial_domains()
    if domains is None or not propagate(domains, [cell for cell in cells if len(domains[cell]) == 1], track_steps=True):
        yield clone_board(board), steps, "No solution", True
        return

    def search(domains: dict[tuple[int, int], set[int]]) -> Generator[SolverYield, None, Optional[dict[tuple[int, int], set[int]]]]:
        nonlocal steps
        unsolved = [cell for cell in cells if len(domains[cell]) > 1]
        if not unsolved:
            return domains

        cell = min(unsolved, key=lambda pos: len(domains[pos]))
        for value in sorted(domains[cell]):
            new_domains = {pos: set(values) for pos, values in domains.items()}
            new_domains[cell] = {value}
            steps += 1

            if propagate(new_domains, [cell], track_steps=True):
                yield domains_to_board(new_domains), steps, "Running", False
                result = yield from search(new_domains)
                if result is not None:
                    return result
            else:
                yield domains_to_board(new_domains), steps, "Pruned", False
        return None

    result = yield from search(domains)
    yield domains_to_board(result or domains), steps, "Solved" if result else "No solution", True


def knuth_generator(start_board: Board, size: int = 3) -> Generator[SolverYield, None, None]:
    board = clone_board(start_board)
    steps = 0
    side = size * size

    if not is_valid_board(board, size):
        yield clone_board(board), steps, "Invalid start", True
        return

    def box_index(row: int, col: int) -> int:
        return (row // size) * size + (col // size)

    def constraints(row: int, col: int, num: int) -> tuple[tuple[str, int, int], ...]:
        return (
            ("cell", row, col),
            ("row", row, num),
            ("col", col, num),
            ("box", box_index(row, col), num),
        )

    rows: dict[tuple[int, int, int], tuple[tuple[str, int, int], ...]] = {}
    columns: dict[tuple[str, int, int], set[tuple[int, int, int]]] = {}

    for r in range(side):
        for c in range(side):
            candidates = [board[r][c]] if board[r][c] else range(1, side + 1)
            for n in candidates:
                row_key = (r, c, n)
                rows[row_key] = constraints(r, c, n)
                for col_key in rows[row_key]:
                    columns.setdefault(col_key, set()).add(row_key)

    active_columns = {key: set(value) for key, value in columns.items()}
    solution_rows: list[tuple[int, int, int]] = []

    def select(row_key: tuple[int, int, int]):
        removed = []
        for col_key in rows[row_key]:
            affected_rows = active_columns.pop(col_key, set())
            removed.append((col_key, affected_rows))
            for other_row in affected_rows:
                for other_col in rows[other_row]:
                    if other_col in active_columns:
                        active_columns[other_col].discard(other_row)
        return removed

    def deselect(removed) -> None:
        for col_key, affected_rows in reversed(removed):
            active_columns[col_key] = affected_rows
            for other_row in affected_rows:
                for other_col in rows[other_row]:
                    if other_col != col_key and other_col in active_columns:
                        active_columns[other_col].add(other_row)

    for r in range(side):
        for c in range(side):
            if board[r][c] != 0:
                fixed = (r, c, board[r][c])
                solution_rows.append(fixed)
                select(fixed)

    def solution_to_board() -> Board:
        shown = clone_board(start_board)
        for r, c, n in solution_rows:
            shown[r][c] = n
        return shown

    def search() -> Generator[SolverYield, None, bool]:
        nonlocal steps
        if not active_columns:
            return True

        col_key = min(active_columns, key=lambda key: len(active_columns[key]))
        options = list(active_columns[col_key])
        if not options:
            return False

        for row_key in options:
            solution_rows.append(row_key)
            removed = select(row_key)
            steps += 1
            yield solution_to_board(), steps, "Running", False

            if (yield from search()):
                return True

            deselect(removed)
            solution_rows.pop()
            steps += 1
            yield solution_to_board(), steps, "Backtracking", False
        return False

    solved = yield from search()
    yield solution_to_board(), steps, "Solved" if solved else "No solution", True


SOLVER_GENERATORS = {
    "Depth-First Search": dfs_generator,
    "Knuth Algorithm X": knuth_generator,
    "Heuristics": heuristic_generator,
    "CSP": csp_generator,
}