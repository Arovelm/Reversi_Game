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

def is_valid(board, row, col, player) -> bool:
    if board[row][col] is not None:
        return False
    return any(_captured_in_dir(board, row, col, player, dr, dc)
               for dr, dc in DIRECTIONS)

def valid_moves(board, player) -> list[tuple]:
    return [(r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if is_valid(board, r, c, player)]

def apply_move(board, row, col, player) -> list[list]:
    new = [row_[:] for row_ in board]
    new[row][col] = player
    for dr, dc in DIRECTIONS:
        for r, c in _captured_in_dir(new, row, col, player, dr, dc):
            new[r][c] = player
    return new

def count(board) -> tuple[int, int]:
    black = sum(cell == "black" for row in board for cell in row)
    white = sum(cell == "white" for row in board for cell in row)
    return black, white

def board_full(board) -> bool:
    return all(cell is not None for row in board for cell in row)

def game_over(board) -> bool:
    return board_full(board) or (
        not valid_moves(board, "black") and not valid_moves(board, "white")
    )

def next_player(board, current) -> str:
    opp = OPPONENT[current]
    return opp if valid_moves(board, opp) else current

def _dark_button(parent, text, command, **kw) -> tk.Button:
    return tk.Button(parent, text=text, command=command,
                     bg=PALETTE["btn_dark_bg"], fg=PALETTE["btn_dark_fg"],
                     activebackground="#333", activeforeground="white",
                     relief="flat", font=("Arial", 14),
                     **kw)

def _light_button(parent, text, command, **kw) -> tk.Button:

    default_kw = {
        "bg": PALETTE["btn_light_bg"],
        "fg": "black",
        "relief": "raised",
        "font": ("Arial", 12)
    }
    default_kw.update(kw)
    return tk.Button(parent, text=text, command=command, **default_kw)

def _piece_score_widget(parent, color) -> tuple[tk.Canvas, tk.Label]:
    frame = tk.Frame(parent, bg=PALETTE["bg"])
    frame.pack(side="left", padx=20)
    canvas = tk.Canvas(frame, width=40, height=40,
                       bg=PALETTE["bg"], highlightthickness=0)
    canvas.pack(side="left")
    fill = "black" if color == "black" else "white"
    canvas.create_oval(5, 5, 35, 35, fill=fill, outline="black", width=1)

    label = tk.Label(frame, text="2",
                     font=("Arial", 18, "bold"),
                     bg=PALETTE["bg"], fg="black")
    label.pack(side="left", padx=6)
    return canvas, label

class MenuScreen(tk.Frame):

    def __init__(self, parent, on_start):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Реверси",
                 font=("Arial", 42, "bold"),
                 bg=PALETTE["bg"], fg="black").place(relx=0.5, rely=0.38, anchor="center")

        _dark_button(self, "1 игрок",  lambda: on_start("1p"), width=12).place(
            relx=0.5, rely=0.52, anchor="center")
        _dark_button(self, "2 игрока", lambda: on_start("2p"), width=12).place(
            relx=0.5, rely=0.63, anchor="center")

        _light_button(self, "Выход", self.quit, font=("Arial", 11), width=8).place(
            relx=0.97, rely=0.97, anchor="se")

class GameScreen(tk.Frame):

    def __init__(self, parent, mode, on_exit):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)

        self.mode = mode
        self.on_exit = on_exit
        self.board = make_board()
        self.current = "black"
        self.is_over = False

        self._build_ui()
        self._draw()

    def _build_ui(self):
        top = tk.Frame(self, bg=PALETTE["bg"])
        top.pack(pady=(12, 6))

        self._blk_canvas, self._blk_lbl = _piece_score_widget(top, "black")
        self._wht_canvas, self._wht_lbl = _piece_score_widget(top, "white")

        board_frame = tk.Frame(self, bg=PALETTE["bg"])
        board_frame.pack()

        size = BOARD_SIZE * CELL
        self._canvas = tk.Canvas(board_frame,
                                 width=size, height=size,
                                 bg=PALETTE["board"],
                                 highlightthickness=2,
                                 highlightbackground=PALETTE["board_border"])
        self._canvas.pack()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self._canvas.create_rectangle(
                    c * CELL, r * CELL,
                    (c + 1) * CELL, (r + 1) * CELL,
                    outline=PALETTE["grid"], width=1,
                    fill=PALETTE["board"]
                )

        self._canvas.bind("<Button-1>", self._on_click)

        _light_button(self, "Выход",
                      self.on_exit, width=22).pack(side="bottom", pady=10)