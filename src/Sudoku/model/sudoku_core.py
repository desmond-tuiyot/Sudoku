import copy
import json

from PyQt5.QtCore import QRunnable, pyqtSlot, QThreadPool
from pip._vendor import requests
from pprint import pprint


class Sudoku:

    def __init__(self):
        self._level = "medium"
        self.generate_puzzle()

    def generate_puzzle(self):
        # request a puzzle
        response = requests.get("https://sugoku.herokuapp.com/board", params={"difficulty": self._level})
        response_dict = json.loads(response.text)

        # save it in class variables
        self._original_board = response_dict['board']
        self._board = copy.deepcopy(self._original_board)
        self._solver = SudokuSolver(self._board)
        return self._board

    def get_board(self):
        return self._board

    def get_original_board(self):
        return self._original_board

    # currently only checks if the row, col, and box placement is valid. No look ahead offered
    #   for when a valid placement will led to a non-solution down the line
    def add_value(self, pos, value, board):
        # board[pos[0]][pos[1]] = value
        solver = SudokuSolver(self._board)
        valid = solver.is_valid_spot(pos[0], pos[1], value)
        if valid:
            return True
        else:
            self._board[pos[0]][pos[1]] = 0
            return False

    def solve(self):
        self._solver.solve()
        return self._solver.return_solved_board()

class SudokuSolver:
    def __init__(self, board):
        self._board = copy.deepcopy(board)
        self._valid_spots = self.initialize_valid_placements()
        self._solvable = True
        # self.solve()
        # self._row =

    def initialize_valid_placements(self):
        row_num = len(self._board)
        col_num = len(self._board[0])
        valid_spots = {(row, col): set()
                       for row in range(row_num)
                       for col in range(col_num)
                       if self._board[row][col] == 0}
        for row, col in valid_spots:
                for num in range(1, 10):
                    if self.is_valid_spot(row, col, num):
                        valid_spots[(row, col)].add(num)

        return valid_spots

    def return_solved_board(self):
        return self._board

    # # set of functions to solve the board.
    def solve(self):

        row, col = self.find_next_empty()
        if row == col == 8:
            return True

        for num in range(1, 10):
            if self.is_valid_spot(row, col, num):
                self._board[row][col] = num
                solved = self.solve()
                if solved:
                    self._solvable = True
                    return True
                else:
                    self._board[row][col] = 0

        self._solvable = False
        return False

        # set of functions to solve the board.
    # def solve(self, board):
    #
    #     row, col = self.find_next_empty()
    #     if row == col == 8:
    #         return True
    #
    #     for num in range(1, 10):
    #         if self.is_valid_spot(row, col, num):
    #             board[row][col] = num
    #             solved = self.solve()
    #             if solved:
    #                 self._solvable = True
    #                 return True
    #             else:
    #                 board[row][col] = 0
    #
    #     self._solvable = False
    #     return False

    # this one is a variation of the above. It finds all valid placements
    # for all empty spots in a given board.
    def find_valid_spots(self):

        row, col = self.find_next_empty()
        if row == col == 8:
            return True

        for num in self._valid_spots[(row, col)]:
            self._board[row][col] = num
            solved = self.find_valid_spots()
            if not solved:
                self._valid_spots[(row, col)].remove(num)

        if self._valid_spots[(row, col)]:
            return True

        return False

    def find_next_empty(self):
        for row in range(0, 9):
            for col in range(0, 9):
                if self._board [row][col] == 0:
                    return row, col

        return 8, 8

    def is_valid_spot(self, row, col, num):
        for i in range(9):
            if self._board[i][col] == num:
                return False

        for j in range(9):
            if self._board[row][j] == num:
                return False

        srow, scol, erow, ecol = self.get_limits(row, col)
        for i in range(srow, erow):
            for j in range(scol, ecol):
                if self._board[i][j] == num:
                    return False

        return True

    def get_limits(self, row, col):
        BOX_SIZE = 3

        srow = row // BOX_SIZE * BOX_SIZE
        scol = col // BOX_SIZE * BOX_SIZE
        erow = srow + 2
        ecol = scol + 2

        return srow, scol, erow, ecol

    # set of functions to check if the whole board setup is valid
    # do we even need this
    def is_valid_sudoku(self):
        return self.rows_valid() and self.cols_valid() and self.boxes_valid()

    def line_valid(self, line):
        line = [x for x in line if x != 0]
        print("this is the damn line", line)
        if len(line) != len(set(line)):
            return False
        return True

    def rows_valid(self, board_flipped):
        for row in board_flipped :
            if self.line_valid(row) is False:
                return False

        return True

    def cols_valid(self):
        return self.rows_valid(zip(*self._board ))

    def boxes_valid(self):
        for i in range(3):
            for j in range(3):
                s_row, s_col = i * 3, j * 3
                e_row, e_col = s_row + 2, s_col + 2
                box = []
                for row in range(s_row, e_row + 1):
                    for col in range(s_col, e_col + 1):
                        box.append(self._board [row][col])
                print("box is ", box)
                if self.line_valid(box) is False:
                    return False
        return True

    def solve_thread(self):
        print("inside solve_thread")
        threadpool = QThreadPool()
        worker = Worker(self.solve, self._board)
        threadpool.start(worker)


class Worker(QRunnable):

    def __init__(self, fn, board):
        super().__init__()

        self.fn = fn
        self.board = board

    @pyqtSlot()
    def run(self):
        self.fn()
        print("in thread")



def main():
    sudoku = Sudoku()
    pprint(sudoku.get_board())
    sudoku._solver.solve_thread()
    pprint(sudoku._board)

    # pprint(sudoku.get_board())
    # original = copy.deepcopy(sudoku._solver.initialize_valid_placements())
    # sudoku._solver.find_valid_spots()
    # print("Valid spots")
    # pprint(sudoku._solver._valid_spots)
    # print(sudoku._solver._valid_spots == original)


if __name__ == "__main__":
    main()
