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
    def _on_click(self, event):
        if self.is_over:
            return
        if self.mode == "1p" and self.current == "white":
            return

        col = event.x // CELL
        row = event.y // CELL
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if is_valid(self.board, row, col, self.current):
                self._make_move(row, col)

    def _make_move(self, row, col):
        self.board = apply_move(self.board, row, col, self.current)
        if game_over(self.board):
            self.is_over = True
            self._draw()
            self.after(400, self._show_result)
            return
        self.current = next_player(self.board, self.current)
        self._draw()
        if self.mode == "1p" and self.current == "white":
            self.after(BOT_DELAY_MS, self._bot_move)

    def _bot_move(self):
        if self.is_over or self.current != "white":
            return
        moves = valid_moves(self.board, "white")
        if moves:
            self._make_move(*random.choice(moves))
        else:
            self.current = next_player(self.board, self.current)
            self._draw()

    def _draw(self):
        self._canvas.delete("piece", "hint")

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece is None:
                    continue
                cx = c * CELL + CELL // 2
                cy = r * CELL + CELL // 2
                rad = CELL // 2 - PIECE_PAD
                self._canvas.create_oval(cx - rad, cy - rad,
                                         cx + rad, cy + rad,
                                         fill=piece, outline="black",
                                         width=1, tags="piece")

        if not self.is_over:
            for r, c in valid_moves(self.board, self.current):
                cx = c * CELL + CELL // 2
                cy = r * CELL + CELL // 2
                rad = CELL // 2 - HINT_PAD
                self._canvas.create_oval(cx - rad, cy - rad,
                                         cx + rad, cy + rad,
                                         fill=PALETTE["hint_fill"],
                                         outline=PALETTE["hint_outline"],
                                         width=2, tags="hint")

        blk, wht = count(self.board)
        self._blk_lbl.config(text=str(blk))
        self._wht_lbl.config(text=str(wht))

        self._blk_canvas.delete("ring")
        self._wht_canvas.delete("ring")
        if not self.is_over:
            ring = self._blk_canvas if self.current == "black" else self._wht_canvas
            ring.create_oval(2, 2, 38, 38,
                             outline=PALETTE["turn_ring"], width=3, tags="ring")

    def _show_result(self):
        blk, wht = count(self.board)
        for w in self.winfo_children():
            w.destroy()
        ResultScreen(self, blk, wht, on_menu=self.on_exit)

class ResultScreen(tk.Frame):

    def __init__(self, parent, black_n, white_n, on_menu):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)

        if black_n > white_n:
            text = "Черные победили"
        elif white_n > black_n:
            text = "Белые победили"
        else:
            text = "Ничья"

        tk.Label(self, text=text,
                 font=("Arial", 30, "bold"),
                 bg=PALETTE["bg"], fg="black").pack(pady=50)

        score_row = tk.Frame(self, bg=PALETTE["bg"])
        score_row.pack(pady=10)
        self._add_score(score_row, "black", black_n)
        self._add_score(score_row, "white", white_n)

        _dark_button(self, "Главное меню", on_menu,
                     width=15).pack(pady=50)

    def _add_score(self, parent, color, n):
        frame = tk.Frame(parent, bg=PALETTE["bg"])
        frame.pack(side="left", padx=30)

        canvas = tk.Canvas(frame, width=40, height=40,
                           bg=PALETTE["bg"], highlightthickness=0)
        canvas.pack(side="left")
        fill = "black" if color == "black" else "white"
        canvas.create_oval(5, 5, 35, 35, fill=fill, outline="black", width=1)

        tk.Label(frame, text=str(n),
                 font=("Arial", 18, "bold"),
                 bg=PALETTE["bg"], fg="black").pack(side="left", padx=8)
        
class ReversiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Реверси")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])

        self._root_frame = tk.Frame(self, bg=PALETTE["bg"])
        self._root_frame.pack(fill="both", expand=True)

        self._show_menu()

    def _clear(self):
        for w in self._root_frame.winfo_children():
            w.destroy()

    def _show_menu(self):
        self._clear()
        MenuScreen(self._root_frame, on_start=self._start_game)

    def _start_game(self, mode):
        self._clear()
        GameScreen(self._root_frame, mode=mode, on_exit=self._show_menu)


if __name__ == "__main__":
    ReversiApp().mainloop()