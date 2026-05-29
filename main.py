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
