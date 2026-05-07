import tkinter as tk
import random

BOARD_SIZE = 8
CELL = 55
PIECE_PAD = 5
HINT_PAD = 14
WINDOW_W, WINDOW_H = 600, 650
BOT_DELAY_MS = 500

PALETTE = {
    "bg":               "white",
    "board":            "#27ae60",
    "board_border":     "#1a5c30",
    "grid":             "black",
    "hint_fill":        "#FFFF00",
    "hint_outline":     "#d4a017",
    "btn_dark_bg":      "#1a1a1a",
    "btn_dark_fg":      "white",
    "btn_light_bg":     "#e0e0e0",
    "turn_ring":        "#3498db",
}

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

OPPONENT = {"black": "white", "white": "black"}
PLAYER_RU = {"black": "Чёрные", "white": "Белые"}
PLAYER_RU = {"black": "Чёрные", "white": "Белые"}

def make_board() -> list[list]:
    board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    m = BOARD_SIZE // 2
    board[m - 1][m - 1] = "white"
    board[m - 1][m]     = "black"
    board[m][m - 1]     = "black"
    board[m][m]         = "white"
    return board

def _captured_in_dir(board, row, col, player, dr, dc) -> list[tuple]:
    opp = OPPONENT[player]
    r, c = row + dr, col + dc
    line = []
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == opp:
        line.append((r, c))
        r += dr
        c += dc
    if line and 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
        return line
    return []