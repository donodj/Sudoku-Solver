class Sudoku:
    def __init__(self, size: int) -> None:
        self.size = size
        self.row_col_length = self.size * self.size
        self.board = []
        self.init_board()


    def init_board(self):
        self.board = []
        for _ in range(self.row_col_length):
            row = [0] * self.row_col_length
            self.board.append(row)


    def get_subgrid_positions(self, row_idx: int, col_idx: int) -> list[tuple[int, int]]:
        if row_idx < 0 or row_idx >= self.size or \
           col_idx < 0 or col_idx >= self.size:
                return []

        positions = []
        for i in range(self.size):
            for j in range(self.size):
                positions.append((row_idx * self.size + i, col_idx * self.size + j))
        return positions


    def can_place(self, row_idx: int, col_idx: int, num: int) -> bool:
        # if number or position is out of range, return false
        if num < 1 or num > self.row_col_length:
            return False
        if row_idx < 0 or row_idx >= self.row_col_length or col_idx < 0 or col_idx >= self.row_col_length:
            return False

        # check if there is already a number at this cell
        if self.board[row_idx][col_idx] != 0:
            return False

        for idx, row_nums in enumerate(self.board):
            if idx == row_idx:  # check if number is in this row, if it is where the number is being placed
                if num in row_nums:
                    return False
            else:
                if row_nums[col_idx] == num:  # check if number is already in the column
                    return False

        # check if num is in the subgrid
        for subgrid_pos in self.get_subgrid_positions(row_idx // self.size, col_idx // self.size):
            if num == self.board[subgrid_pos[0]][subgrid_pos[1]]:
                return False

        return True



    def print_board(self):
        # Find length of the longest string representing a cell
        cell_str_length = 0
        for row in self.board:
            for num in row:
                cell_str_length = max(cell_str_length, len(str(num)))

        # Build horizontal separator line
        line_length = ((cell_str_length + 1) * self.row_col_length) + ((self.size - 1) * 2) - 1
        separator = "-" * line_length

        for i, row in enumerate(self.board):
            # Print horizontal separator every few rows based on board size
            if i % self.size == 0 and i != 0:
                print(separator)

            for j, num in enumerate(row):
                # Print vertical separator every few columns based on board size
                if j % self.size == 0 and j != 0:
                    print("|", end=" ")

                cell = "." if num == 0 else str(num)
                print(f"{cell:>{cell_str_length}}", end=" ")

            print()  # new line after each row




if __name__ == "__main__":
    sudoku = Sudoku(size=3)

    while True:
        sudoku.print_board()

        inp = input("Enter move, formatted as \"row, column, number\": ")

        input_nums = inp.split(",")
        if len(input_nums) != 3:
            print("Error: Expected exactly 3 integers")
            continue

        row, col, num = input_nums
        row, col, num = int(row) - 1, int(col) - 1, int(num)
        if sudoku.can_place(row, col, num):
            sudoku.board[row][col] = num
        else:
            print("Invalid placement")
