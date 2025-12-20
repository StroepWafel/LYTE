#!/usr/bin/env python3
"""
Noughts & Crosses (Tic‑Tac‑Toe) – Player vs. AI

Features
--------
* Two‑player console interface
* AI opponent that plays *perfectly* (Minimax algorithm)
* Option to choose who goes first
"""

from __future__ import annotations
import sys
from typing import List, Tuple, Optional

# --------------------------------------------------------------------------- #
# 1️⃣ Board helpers
# --------------------------------------------------------------------------- #
def create_board() -> List[List[str]]:
    """Return a 3×3 board filled with spaces."""
    return [[" " for _ in range(3)] for _ in range(3)]

def print_board(board: List[List[str]]) -> None:
    """Pretty‑print the board."""
    print("\n   |   |   ")
    for i, row in enumerate(board):
        print(f" {row[0]} | {row[1]} | {row[2]} ")
        if i < 2:
            print("---+---+---")
    print()

def board_full(board: List[List[str]]) -> bool:
    """True if no empty cells remain."""
    return all(cell != " " for row in board for cell in row)

def valid_move(board: List[List[str]], r: int, c: int) -> bool:
    """True if the cell is inside the board and empty."""
    return 0 <= r < 3 and 0 <= c < 3 and board[r][c] == " "

# --------------------------------------------------------------------------- #
# 2️⃣ Game logic (winner detection)
# --------------------------------------------------------------------------- #
def check_win(board: List[List[str]]) -> Optional[str]:
    """Return 'X' or 'O' if there is a winner, otherwise None."""
    # rows & columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
    # diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

# --------------------------------------------------------------------------- #
# 3️⃣ Minimax AI
# --------------------------------------------------------------------------- #
def evaluate(board: List[List[str]], ai: str, human: str) -> int:
    """Return +10 if AI wins, -10 if human wins, 0 otherwise."""
    winner = check_win(board)
    if winner == ai:
        return 10
    if winner == human:
        return -10
    return 0

def minimax(board: List[List[str]], depth: int, is_max: bool,
            ai: str, human: str) -> int:
    """Recursive Minimax – returns the best score for the current player."""
    score = evaluate(board, ai, human)
    if score != 0 or board_full(board):
        return score

    if is_max:  # AI's turn
        best = -float("inf")
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = ai
                    best = max(best, minimax(board, depth + 1, False, ai, human))
                    board[i][j] = " "
        return best
    else:  # Human's turn
        best = float("inf")
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = human
                    best = min(best, minimax(board, depth + 1, True, ai, human))
                    board[i][j] = " "
        return best

def best_move(board: List[List[str]], ai: str, human: str) -> Tuple[int, int]:
    """Return the best (row, col) for AI."""
    best_val = -float("inf")
    move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = ai
                val = minimax(board, 0, False, ai, human)
                board[i][j] = " "
                if val > best_val:
                    best_val = val
                    move = (i, j)
    return move

# --------------------------------------------------------------------------- #
# 4️⃣ Human input
# --------------------------------------------------------------------------- #
def get_move(player: str) -> Tuple[int, int]:
    """Prompt for a row/col and return 0‑based indices."""
    while True:
        raw = input(f"{player} (row col) or 'q' to quit: ").strip()
        if raw.lower() in ("q", "quit"):
            sys.exit("\nGame aborted.\n")
        try:
            r, c = map(int, raw.split())
            return r - 1, c - 1  # convert to 0‑based
        except ValueError:
            print("Please enter two numbers: row and column (1‑3).")

# --------------------------------------------------------------------------- #
# 5️⃣ Main loop
# --------------------------------------------------------------------------- #
def main() -> None:
    board = create_board()

    # Let the user decide who goes first
    while True:
        first = input("Who goes first? (X/O): ").strip().upper()
        if first in ("X", "O"):
            break
        print("Invalid choice – please type X or O.")

    human = "X" if first == "X" else "O"
    ai = "O" if human == "X" else "X"
    current_player = first

    print(f"\nYou are '{human}'. AI is '{ai}'.")
    print(f"{current_player} starts.\n")

    while True:
        print_board(board)

        if current_player == human:
            r, c = get_move(human)
            if not valid_move(board, r, c):
                print("That square is occupied or out of bounds. Try again.")
                continue
            board[r][c] = human
        else:
            print("AI is thinking…")
            r, c = best_move(board, ai, human)
            board[r][c] = ai
            print(f"AI placed at row {r+1}, column {c+1}.")

        winner = check_win(board)
        if winner:
            print_board(board)
            print(f"\n{'You' if winner == human else 'AI'} win!")
            break
        if board_full(board):
            print_board(board)
            print("\nIt's a draw!")
            break

        # Switch turns
        current_player = ai if current_player == human else human

if __name__ == "__main__":
    main()