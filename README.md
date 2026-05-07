# Sudoku Multi-Solver

A program that visualizes 4 Sudoku solving algorithms and compares their performance.

Algorithms used:
* Depth-First Search
* Knuth’s Algorithm X
* Least-Constraining-Value (LCV) and Minimum Remaining Values (MRV) Heuristic
* Constraint Satisfaction Problem (CSP) Method

Code is distributed among 4 files:

* sudoku.py - Has all the Sudoku game logic, and code to evaluate the board state and generate puzzles

* solvers.py - Code for all solving algorithms. Each algorithm has a function to send its current state to the GUI to display its steps

* gui.py - Builds the GUI to display a Sudoku board for each solving algorithm. Also visualizes their current progress in solving the puzzle, while tracking the number of steps and time elapsed

* main.py - Runs the entire program