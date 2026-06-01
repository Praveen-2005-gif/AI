"""
Snake & Ladder PRO - Complete Working Version
=============================================
Features:
- Colourful board (yellow/cyan tiles)
- Cartoon snakes with bezier curves
- Wooden ladders
- Difficulty: Easy / Medium / Hard
- Modes: Human vs Human | Human vs AI | Free Play (2-4)
- Token colour chooser
- Animated dice
- Win celebration
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math
import time

# ═══════════════════════════════════════════════════════
#  BOARD GEOMETRY
# ═══════════════════════════════════════════════════════
CELL = 60
COLS = 10
ROWS = 10
PAD  = 4
BW   = COLS * CELL + 2 * PAD   # 608
BH   = ROWS * CELL + 2 * PAD   # 608

# ═══════════════════════════════════════════════════════
#  DIFFICULTY CONFIGS
# ═══════════════════════════════════════════════════════
CONFIGS = {
    "Easy": {
        "snakes":  {17: 7,  54: 34, 62: 19, 97: 78},
        "ladders": {4: 14,  9: 31,  20: 38, 28: 84, 40: 59, 63: 81, 71: 91},
        "desc":    "4 snakes  7 ladders  Short drops",
    },
    "Medium": {
        "snakes":  {17: 7,  42: 11, 54: 19, 72: 33, 88: 24, 97: 78},
        "ladders": {4: 14,  9: 31,  20: 38, 28: 84, 40: 59, 63: 81, 71: 91},
        "desc":    "6 snakes  7 ladders  Classic game",
    },
    "Hard": {
        "snakes":  {17: 7,  27: 3,  42: 11, 54: 19, 62: 2,
                    72: 33, 88: 24, 95: 56, 97: 78, 99: 10},
        "ladders": {4: 14,  9: 31,  20: 38, 51: 67, 63: 81},
        "desc":    "10 snakes  5 ladders  Brutal drops",
    },
}

# ═══════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════
TILE_YELLOW = "#FFD700"
TILE_CYAN   = "#00BFFF"

SNAKE_PALETTES = [
    ("#2ECC40", "#27AE60", "#FFFF00"),
    ("#E74C3C", "#C0392B", "#FF8C00"),
    ("#9B59B6", "#7D3C98", "#F8C471"),
    ("#1ABC9C", "#148F77", "#F9E79F"),
    ("#E67E22", "#D35400", "#F7DC6F"),
    ("#3498DB", "#1A5276", "#FDFEFE"),
]

LADDER_RAIL  = "#8B4513"
LADDER_RUNG  = "#D2691E"
LADDER_SHINE = "#F4A460"

BG     = "#1A1A2E"
BG2    = "#16213E"
CARD   = "#0F3460"
ACCENT = "#E94560"
GOLD   = "#FFD700"
TXT    = "#EAEAEA"
TDIM   = "#8892A4"

TOKEN_OPTIONS = {
    "Red":    "#E74C3C",
    "Blue":   "#2980B9",
    "Green":  "#27AE60",
    "Yellow": "#F39C12",
    "Purple": "#8E44AD",
    "Pink":   "#E91E8C",
}

DICE_FACES = ["1", "2", "3", "4", "5", "6"]
DICE_DOTS  = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5),
        (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.2), (0.75, 0.2), (0.25, 0.5),
        (0.75, 0.5), (0.25, 0.8), (0.75, 0.8)],
}

# ═══════════════════════════════════════════════════════
#  GEOMETRY HELPERS
# ═══════════════════════════════════════════════════════
def cell_centre(n):
    n -= 1
    row = n // COLS
    col = n % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    sr = ROWS - 1 - row
    x  = PAD + col * CELL + CELL // 2
    y  = PAD + sr  * CELL + CELL // 2
    return x, y

def cell_rect(n):
    cx, cy = cell_centre(n)
    h = CELL // 2
    return cx - h, cy - h, cx + h, cy + h

def bezier_points(x0, y0, cx, cy, x1, y1, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t)**2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
        y = (1 - t)**2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1
        pts.append((x, y))
    return pts

# ═══════════════════════════════════════════════════════
#  BOARD DRAWING
# ═══════════════════════════════════════════════════════
_snake_ctrl = {}  # cache control points so they don't change each redraw

def draw_board(canvas, snakes, ladders):
    canvas.delete("all")

    # Border
    canvas.create_rectangle(0, 0, BW, BH, fill="#FF6B35", outline="")
    canvas.create_rectangle(PAD - 2, PAD - 2, BW - PAD + 2, BH - PAD + 2,
                            fill="#FF6B35", outline="#CC4400", width=3)

    # Tiles
    for n in range(1, 101):
        x0, y0, x1, y1 = cell_rect(n)
        row = (n - 1) // COLS
        col_in_row = (n - 1) % COLS
        if (row + col_in_row) % 2 == 0:
            fill = TILE_YELLOW
            outline = "#CCAA00"
        else:
            fill = TILE_CYAN
            outline = "#0090CC"
        canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=1)

    # Cell numbers
    for n in range(1, 101):
        cx, cy = cell_centre(n)
        canvas.create_text(cx, cy - 16, text=str(n),
                           font=("Arial", 9, "bold"), fill="#003366")

    # LADDERS
    for bottom, top in ladders.items():
        bx, by = cell_centre(bottom)
        tx, ty = cell_centre(top)
        angle = math.atan2(ty - by, tx - bx)
        perp  = angle + math.pi / 2
        off   = 7

        for side in (-1, 1):
            ox = side * off * math.cos(perp)
            oy = side * off * math.sin(perp)
            # Shadow
            canvas.create_line(bx + ox + 2, by + oy + 2,
                               tx + ox + 2, ty + oy + 2,
                               fill="#555555", width=6, capstyle="round")
            # Rail
            canvas.create_line(bx + ox, by + oy, tx + ox, ty + oy,
                               fill=LADDER_RAIL, width=6, capstyle="round")
            # Shine
            canvas.create_line(bx + ox - 1, by + oy - 1,
                               tx + ox - 1, ty + oy - 1,
                               fill=LADDER_SHINE, width=2, capstyle="round")

        dist  = math.hypot(tx - bx, ty - by)
        steps = max(3, int(dist // 22))
        for s in range(1, steps):
            t_ = s / steps
            rx = bx + t_ * (tx - bx)
            ry = by + t_ * (ty - by)
            ox = off * math.cos(perp)
            oy = off * math.sin(perp)
            canvas.create_line(rx - ox + 2, ry - oy + 2,
                               rx + ox + 2, ry + oy + 2,
                               fill="#333333", width=5, capstyle="round")
            canvas.create_line(rx - ox, ry - oy, rx + ox, ry + oy,
                               fill=LADDER_RUNG, width=5, capstyle="round")

        # Base badge
        canvas.create_oval(bx - 13, by - 13, bx + 13, by + 13,
                           fill="#27AE60", outline="#1E8449", width=2)
        canvas.create_text(bx, by, text="L", font=("Arial", 10, "bold"), fill="white")

        # Top badge
        canvas.create_oval(tx - 10, ty - 10, tx + 10, ty + 10,
                           fill="#2980B9", outline="#1A5276", width=2)
        canvas.create_text(tx, ty, text="^", font=("Arial", 10, "bold"), fill="white")

    # SNAKES
    for idx, (head, tail) in enumerate(snakes.items()):
        col, dark, belly = SNAKE_PALETTES[idx % len(SNAKE_PALETTES)]
        hx, hy = cell_centre(head)
        tx, ty = cell_centre(tail)

        key = (head, tail)
        if key not in _snake_ctrl:
            dx = random.choice([-1, 1]) * random.randint(25, 50)
            dy = random.choice([-1, 1]) * random.randint(20, 45)
            _snake_ctrl[key] = ((hx + tx) / 2 + dx, (hy + ty) / 2 + dy)
        mx, my = _snake_ctrl[key]

        pts  = bezier_points(hx, hy, mx, my, tx, ty, 40)
        flat = [c for p in pts for c in p]

        # Shadow
        canvas.create_line(*flat, fill="#444444", width=14,
                           smooth=True, capstyle="round", joinstyle="round")
        # Body
        canvas.create_line(*flat, fill=col, width=13,
                           smooth=True, capstyle="round", joinstyle="round")
        # Belly stripe
        canvas.create_line(*flat, fill=belly, width=5,
                           smooth=True, capstyle="round", joinstyle="round",
                           dash=(6, 8))
        # Outline
        canvas.create_line(*flat, fill=dark, width=1,
                           smooth=True, capstyle="round", joinstyle="round")

        # Scale dots
        for i in range(3, len(pts) - 3, 4):
            px, py = pts[i]
            canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                               fill=dark, outline="")

        # Head circle
        canvas.create_oval(hx - 16, hy - 16, hx + 16, hy + 16,
                           fill=col, outline=dark, width=3)
        # Eyes
        for ex, ey in [(hx - 5, hy - 5), (hx + 5, hy - 5)]:
            canvas.create_oval(ex - 4, ey - 4, ex + 4, ey + 4,
                               fill="white", outline=dark, width=1)
            canvas.create_oval(ex - 2, ey - 2, ex + 2, ey + 2,
                               fill="black")
        # Tongue
        canvas.create_line(hx, hy + 10, hx, hy + 17, fill="#E74C3C", width=2)
        canvas.create_line(hx, hy + 17, hx - 4, hy + 22, fill="#E74C3C", width=2)
        canvas.create_line(hx, hy + 17, hx + 4, hy + 22, fill="#E74C3C", width=2)

        # Tail dot
        canvas.create_oval(tx - 6, ty - 6, tx + 6, ty + 6,
                           fill=col, outline=dark, width=2)

    # Trophy on 100
    cx, cy = cell_centre(100)
    canvas.create_text(cx, cy + 14, text="WIN", font=("Arial", 9, "bold"), fill="#8B0000")

# ═══════════════════════════════════════════════════════
#  DRAW DICE
# ═══════════════════════════════════════════════════════
def draw_dice(canvas, value, x, y, size=56, highlight=False):
    canvas.delete("all")
    r = 10
    bg = "#FFFDE7" if not highlight else "#FFD700"
    # Shadow
    canvas.create_rectangle(x + 3, y + 3, x + size + 3, y + size + 3,
                            fill="#444444", outline="")
    # Body
    canvas.create_rectangle(x, y, x + size, y + size,
                            fill=bg, outline="#333333", width=2)
    # Dots
    dot_r = size * 0.085
    for (dx, dy) in DICE_DOTS.get(value, []):
        cx = x + dx * size
        cy = y + dy * size
        canvas.create_oval(cx - dot_r, cy - dot_r,
                           cx + dot_r, cy + dot_r,
                           fill="#1A1A2E", outline="")

# ═══════════════════════════════════════════════════════
#  APP SHELL
# ═══════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake & Ladder PRO")
        self.geometry("1000x750")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._page = None
        self.goto(WelcomePage)

    def goto(self, Cls, **kw):
        if self._page:
            self._page.destroy()
        self._page = Cls(self, **kw)
        self._page.pack(fill="both", expand=True)

# ═══════════════════════════════════════════════════════
#  PAGE 1 — WELCOME
# ═══════════════════════════════════════════════════════
class WelcomePage(tk.Frame):
    print("Welcome page build started")
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._stars = []
        self._build()

    def _build(self):
        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        for _ in range(100):
            x = random.randint(0, 960)
            y = random.randint(0, 720)
            r = random.uniform(1, 2.5)
            s = self.cv.create_oval(x - r, y - r, x + r, y + r,
                                    fill="white", outline="")
            self._stars.append((s, random.uniform(0.5, 2.2)))
        self._twinkle()

        tk.Label(self, text="SNAKE & LADDER",
                 font=("Impact", 42), fg=GOLD, bg=BG
                 ).place(relx=.5, rely=.13, anchor="center")
        tk.Label(self, text="PRO EDITION",
                 font=("Courier", 17, "bold"), fg=ACCENT, bg=BG
                 ).place(relx=.5, rely=.22, anchor="center")
        tk.Label(self, text="Choose Your Mode",
                 font=("Courier", 16, "bold"), fg=TXT, bg=BG
                 ).place(relx=.5, rely=.33, anchor="center")

        self._btn("Human  vs  Human",  .5, .44,
                  lambda: self.master.goto(DifficultyPage, mode="hvh"))
        self._btn("Human  vs  AI",     .5, .56,
                  lambda: self.master.goto(DifficultyPage, mode="hvai"))
        self._btn("Free Play  (2-4)",  .5, .68,
                  lambda: self.master.goto(DifficultyPage, mode="free"))

    def _btn(self, txt, rx, ry, cmd):
        b = tk.Button(self, text=txt,
                      font=("Courier", 14, "bold"),
                      fg=TXT, bg=CARD,
                      activebackground=ACCENT,
                      activeforeground="white",
                      relief="flat", cursor="hand2",
                      padx=36, pady=12, command=cmd)
        b.place(relx=rx, rely=ry, anchor="center")
        b.bind("<Enter>", lambda e: b.config(bg=ACCENT))
        b.bind("<Leave>", lambda e: b.config(bg=CARD))

    def _twinkle(self):
        t = time.time()
        for s, sp in self._stars:
            a = int(90 + 165 * abs(math.sin(t * sp)))
            col = f"#{a:02x}{a:02x}{a:02x}"
            self.cv.itemconfig(s, fill=col)
        self.after(60, self._twinkle)

# ═══════════════════════════════════════════════════════
#  PAGE 2 — DIFFICULTY
# ═══════════════════════════════════════════════════════
class DifficultyPage(tk.Frame):
    def __init__(self, master, mode):
        super().__init__(master, bg=BG2)
        self.mode = mode
        self._build()

    def _build(self):
        tk.Label(self, text="SELECT DIFFICULTY",
                 font=("Impact", 30), fg=GOLD, bg=BG2
                 ).pack(pady=(30, 8))
        tk.Label(self, text="How hard do you want it?",
                 font=("Courier", 13), fg=TDIM, bg=BG2
                 ).pack(pady=(0, 24))

        info = {
            "Easy":   ("Easy",   "Beginner Friendly", "Few snakes, many ladders"),
            "Medium": ("Medium", "Classic Challenge",  "Balanced snakes & ladders"),
            "Hard":   ("Hard",   "Brutal Mode",        "Many long snakes, few ladders"),
        }

        for diff, (emoji, title, sub) in info.items():
            card = tk.Frame(self, bg=CARD, padx=22, pady=14, cursor="hand2")
            card.pack(padx=80, pady=8, fill="x")

            col = {"Easy": "#2ECC71", "Medium": "#F39C12", "Hard": "#E74C3C"}[diff]
            tk.Label(card, text=f"[{emoji}]",
                     font=("Courier", 18, "bold"), fg=col, bg=CARD
                     ).pack(side="left", padx=(0, 12))
            tf = tk.Frame(card, bg=CARD)
            tf.pack(side="left")
            tk.Label(tf, text=title,
                     font=("Courier", 15, "bold"), fg=TXT, bg=CARD, anchor="w"
                     ).pack(anchor="w")
            tk.Label(tf, text=CONFIGS[diff]["desc"],
                     font=("Courier", 11), fg=TDIM, bg=CARD, anchor="w"
                     ).pack(anchor="w")

            def _click(d=diff):
                self.master.goto(SetupPage, mode=self.mode, difficulty=d)

            for w in [card] + list(card.winfo_children()):
                w.bind("<Button-1>", lambda e, f=_click: f())
            for w in tf.winfo_children():
                w.bind("<Button-1>", lambda e, f=_click: f())

            card.bind("<Enter>", lambda e, c=card:
                      [w.config(bg=ACCENT) for w in [c] + list(c.winfo_children())])
            card.bind("<Leave>", lambda e, c=card:
                      [w.config(bg=CARD) for w in [c] + list(c.winfo_children())])

        tk.Button(self, text="<-- Back",
                  font=("Courier", 11), fg=TDIM, bg=BG2,
                  relief="flat", cursor="hand2",
                  command=lambda: self.master.goto(WelcomePage)
                  ).pack(pady=18)

# ═══════════════════════════════════════════════════════
#  PAGE 3 — SETUP
# ═══════════════════════════════════════════════════════
class SetupPage(tk.Frame):
    def __init__(self, master, mode, difficulty):
        super().__init__(master, bg=BG2)
        self.mode = mode
        self.diff = difficulty
        self.rows = []
        self._build()

    def _build(self):
        diff_col = {"Easy": "#2ECC71", "Medium": "#F39C12", "Hard": "#E74C3C"}
        tk.Label(self, text="PLAYER SETUP",
                 font=("Impact", 28), fg=GOLD, bg=BG2).pack(pady=(22, 4))
        tk.Label(self, text=f"Difficulty: {self.diff}",
                 font=("Courier", 14, "bold"),
                 fg=diff_col[self.diff], bg=BG2).pack(pady=(0, 14))

        if self.mode == "free":
            nf = tk.Frame(self, bg=BG2)
            nf.pack(pady=6)
            tk.Label(nf, text="Number of Players:",
                     font=("Courier", 13), fg=TXT, bg=BG2).pack(side="left", padx=8)
            self.nvar = tk.IntVar(value=2)
            for n in (2, 3, 4):
                tk.Radiobutton(nf, text=str(n), variable=self.nvar, value=n,
                               font=("Courier", 13, "bold"), fg=GOLD, bg=BG2,
                               selectcolor=BG, activebackground=BG2,
                               command=self._refresh).pack(side="left", padx=8)
        else:
            self.nvar = tk.IntVar(value=2)

        self.rf = tk.Frame(self, bg=BG2)
        self.rf.pack(pady=10)
        self._refresh()

        tk.Button(self, text="START GAME",
                  font=("Courier", 15, "bold"), fg="white", bg=ACCENT,
                  activebackground="#C0392B", relief="flat",
                  cursor="hand2", padx=30, pady=12,
                  command=self._start).pack(pady=18)
        tk.Button(self, text="<-- Back",
                  font=("Courier", 11), fg=TDIM, bg=BG2,
                  relief="flat", cursor="hand2",
                  command=lambda: self.master.goto(DifficultyPage, mode=self.mode)
                  ).pack()

    def _refresh(self):
        for w in self.rf.winfo_children():
            w.destroy()
        self.rows = []
        n = self.nvar.get()
        cols = list(TOKEN_OPTIONS.keys())

        for i in range(n):
            is_ai = (self.mode == "hvai" and i == n - 1)
            row = tk.Frame(self.rf, bg=CARD, pady=9, padx=14)
            row.pack(fill="x", padx=40, pady=5)

            lbl = "[AI]" if is_ai else f"[P{i + 1}]"
            tk.Label(row, text=lbl,
                     font=("Courier", 13, "bold"),
                     fg=GOLD if is_ai else TXT,
                     bg=CARD, width=7, anchor="w").pack(side="left")

            nv = tk.StringVar(value="CPU" if is_ai else f"Player {i + 1}")
            e = tk.Entry(row, textvariable=nv,
                         font=("Courier", 13),
                         fg=TXT, bg=BG, insertbackground=TXT,
                         relief="flat", width=12)
            if is_ai:
                e.config(state="disabled")
            e.pack(side="left", padx=10)

            tk.Label(row, text="Token:",
                     font=("Courier", 11), fg=TDIM, bg=CARD
                     ).pack(side="left", padx=(6, 3))
            cv = tk.StringVar(value=cols[i % len(cols)])
            om = tk.OptionMenu(row, cv, *TOKEN_OPTIONS.keys())
            om.config(font=("Courier", 11), fg=TXT, bg=BG,
                      relief="flat", activebackground=ACCENT, bd=0, width=7)
            om["menu"].config(font=("Courier", 11), bg=BG,
                              fg=TXT, activebackground=ACCENT)
            om.pack(side="left", padx=4)

            prev = tk.Canvas(row, width=26, height=26, bg=CARD, highlightthickness=0)
            prev.pack(side="left", padx=4)
            circ = prev.create_oval(3, 3, 23, 23,
                                    fill=TOKEN_OPTIONS[cv.get()],
                                    outline="white", width=2)

            def _upd(*a, cv=cv, prev=prev, circ=circ):
                prev.itemconfig(circ, fill=TOKEN_OPTIONS[cv.get()])
            cv.trace_add("write", _upd)
            self.rows.append({"name": nv, "color": cv, "is_ai": is_ai})

    def _start(self):
        players = []
        used = set()
        for i, r in enumerate(self.rows):
            c = r["color"].get()
            if c in used:
                for a in TOKEN_OPTIONS:
                    if a not in used:
                        c = a
                        break
            used.add(c)
            players.append({
                "name":       r["name"].get() or f"P{i + 1}",
                "color":      TOKEN_OPTIONS[c],
                "color_name": c,
                "is_ai":      r["is_ai"],
                "pos":        0,
                "turns":      0,
            })
        cfg = CONFIGS[self.diff]
        self.master.goto(GamePage,
                         players=players,
                         snakes=cfg["snakes"],
                         ladders=cfg["ladders"],
                         difficulty=self.diff)

# ═══════════════════════════════════════════════════════
#  PAGE 4 — GAME
# ═══════════════════════════════════════════════════════
class GamePage(tk.Frame):
    TOKEN_OFFSETS = [(-11, -11), (11, -11), (-11, 11), (11, 11)]

    def __init__(self, master, players, snakes, ladders, difficulty):
        super().__init__(master, bg=BG)
        self.players    = players
        self.snakes     = snakes
        self.ladders    = ladders
        self.difficulty = difficulty
        self.current    = 0
        self.busy       = False
        self._tokens    = {}
        self._dice_val  = 1
        self._build()
        self._draw()
        self._init_tokens()
        self._refresh_panel()
        if self.players[0]["is_ai"]:
            self.after(900, self._roll)

    # ── Layout ──────────────────────────────────────
    def _build(self):
        # Board canvas
        self.bc = tk.Canvas(self, width=BW, height=BH,
                            bg="#FF6B35",
                            highlightthickness=4,
                            highlightbackground=GOLD)
        self.bc.pack(side="left", padx=12, pady=12)

        # Side panel
        self.pn = tk.Frame(self, bg=BG2, width=310)
        self.pn.pack(side="right", fill="both", expand=True,
                     padx=(0, 12), pady=12)
        self.pn.pack_propagate(False)

        diff_col = {"Easy": "#2ECC71", "Medium": "#F39C12", "Hard": "#E74C3C"}
        tk.Label(self.pn, text="SNAKE & LADDER",
                 font=("Impact", 16), fg=GOLD, bg=BG2).pack(pady=(14, 0))
        tk.Label(self.pn, text=self.difficulty,
                 font=("Courier", 12, "bold"),
                 fg=diff_col[self.difficulty], bg=BG2).pack()

        # Dice canvas
        self.dc = tk.Canvas(self.pn, width=80, height=80,
                            bg=BG2, highlightthickness=0)
        self.dc.pack(pady=12)
        draw_dice(self.dc, 1, 12, 12, size=56)

        # Roll button
        self.roll_btn = tk.Button(self.pn, text="ROLL DICE",
                                  font=("Courier", 13, "bold"),
                                  fg="white", bg=ACCENT,
                                  activebackground="#C0392B",
                                  relief="flat", cursor="hand2",
                                  padx=18, pady=9,
                                  command=self._roll)
        self.roll_btn.pack(pady=4)

        # Score / log area
        self.score_frame = tk.Frame(self.pn, bg=BG2)
        self.score_frame.pack(fill="x", padx=10, pady=8)

        self.log_box = tk.Text(self.pn, width=30, height=12,
                               bg=CARD, fg=TXT,
                               font=("Courier", 10),
                               relief="flat", state="disabled",
                               wrap="word")
        self.log_box.pack(fill="x", padx=10, pady=4)

        # Turn label
        self.turn_lbl = tk.Label(self.pn, text="",
                                 font=("Courier", 12, "bold"),
                                 fg=GOLD, bg=BG2, wraplength=260)
        self.turn_lbl.pack(pady=6)

        # Back button
        tk.Button(self.pn, text="<-- Menu",
                  font=("Courier", 10), fg=TDIM, bg=BG2,
                  relief="flat", cursor="hand2",
                  command=lambda: self.master.goto(WelcomePage)
                  ).pack(side="bottom", pady=10)

    # ── Board ────────────────────────────────────────
    def _draw(self):
        draw_board(self.bc, self.snakes, self.ladders)

    # ── Tokens ───────────────────────────────────────
    def _init_tokens(self):
        for i, p in enumerate(self.players):
            ox, oy = self.TOKEN_OFFSETS[i % 4]
            cx, cy = (PAD + CELL // 2, BH - PAD - CELL // 2)  # off board start
            tid = self.bc.create_oval(cx + ox - 10, cy + oy - 10,
                                       cx + ox + 10, cy + oy + 10,
                                       fill=p["color"],
                                       outline="white", width=2,
                                       tags=f"tok{i}")
            lbl = self.bc.create_text(cx + ox, cy + oy,
                                       text=str(i + 1),
                                       font=("Arial", 8, "bold"),
                                       fill="white",
                                       tags=f"lbl{i}")
            self._tokens[i] = (tid, lbl)

    def _move_token(self, pi, pos):
        tid, lbl = self._tokens[pi]
        ox, oy   = self.TOKEN_OFFSETS[pi % 4]
        if pos == 0:
            cx, cy = PAD + CELL // 2, BH - PAD - CELL // 2
        else:
            cx, cy = cell_centre(pos)
        self.bc.coords(tid, cx + ox - 10, cy + oy - 10,
                        cx + ox + 10, cy + oy + 10)
        self.bc.coords(lbl, cx + ox, cy + oy)
        self.bc.tag_raise(f"tok{pi}")
        self.bc.tag_raise(f"lbl{pi}")

    # ── Panel ────────────────────────────────────────
    def _refresh_panel(self):
        for w in self.score_frame.winfo_children():
            w.destroy()
        for i, p in enumerate(self.players):
            is_cur = (i == self.current)
            bg = ACCENT if is_cur else CARD
            row = tk.Frame(self.score_frame, bg=bg, pady=5, padx=8)
            row.pack(fill="x", pady=2)
            dot = tk.Canvas(row, width=18, height=18, bg=bg, highlightthickness=0)
            dot.pack(side="left", padx=(0, 6))
            dot.create_oval(2, 2, 16, 16, fill=p["color"], outline="white")
            name = p["name"] + (" (AI)" if p["is_ai"] else "")
            tk.Label(row, text=name,
                     font=("Courier", 11, "bold" if is_cur else "normal"),
                     fg="white", bg=bg, anchor="w"
                     ).pack(side="left", fill="x", expand=True)
            pos_txt = f"Sq {p['pos']}" if p['pos'] > 0 else "Start"
            tk.Label(row, text=pos_txt,
                     font=("Courier", 10), fg=TDIM if not is_cur else GOLD,
                     bg=bg).pack(side="right")

        p = self.players[self.current]
        name = p["name"] + (" (AI)" if p["is_ai"] else "")
        self.turn_lbl.config(text=f"{name}'s Turn")
        self.roll_btn.config(
            state="disabled" if p["is_ai"] or self.busy else "normal"
        )

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ── Dice Animation ───────────────────────────────
    def _animate_dice(self, final, callback, frames=10):
        if frames <= 0:
            draw_dice(self.dc, final, 12, 12, size=56, highlight=True)
            self.after(300, callback)
            return
        v = random.randint(1, 6)
        draw_dice(self.dc, v, 12, 12, size=56)
        self.after(60, lambda: self._animate_dice(final, callback, frames - 1))

    # ── Roll ─────────────────────────────────────────
    def _roll(self):
        if self.busy:
            return
        self.busy = True
        self.roll_btn.config(state="disabled")
        val = random.randint(1, 6)
        self._dice_val = val
        self._animate_dice(val, lambda: self._apply_move(val))

    def _apply_move(self, val):
        p   = self.players[self.current]
        old = p["pos"]
        new = old + val

        if new > 100:
            self._log(f"{p['name']} rolled {val}. Needs {100 - old} to win. No move.")
            self._end_turn()
            return

        p["turns"] += 1
        p["pos"]    = new
        self._move_token(self.current, new)
        self._log(f"{p['name']} rolled {val}: {old} -> {new}")

        # Check snake or ladder
        self.after(400, lambda: self._check_cell(new))

    def _check_cell(self, pos):
        p = self.players[self.current]

        if pos in self.snakes:
            dest = self.snakes[pos]
            p["pos"] = dest
            self._log(f"  SNAKE! {pos} -> {dest}")
            self._move_token(self.current, dest)
            self.bc.itemconfig(self._tokens[self.current][0],
                               outline="#FF0000", width=3)
            self.after(400, lambda: self.bc.itemconfig(
                self._tokens[self.current][0], outline="white", width=2))
            self.after(500, self._end_turn)
            return

        if pos in self.ladders:
            dest = self.ladders[pos]
            p["pos"] = dest
            self._log(f"  LADDER! {pos} -> {dest}")
            self._move_token(self.current, dest)
            self.bc.itemconfig(self._tokens[self.current][0],
                               outline="#00FF00", width=3)
            self.after(400, lambda: self.bc.itemconfig(
                self._tokens[self.current][0], outline="white", width=2))
            self.after(500, self._check_win)
            return

        self._check_win()

    def _check_win(self):
        p = self.players[self.current]
        if p["pos"] == 100:
            self._celebrate(p)
            return
        self._end_turn()

    def _end_turn(self):
        self.current = (self.current + 1) % len(self.players)
        self.busy    = False
        self._refresh_panel()
        # AI turn
        if self.players[self.current]["is_ai"]:
            self.after(900, self._roll)

    # ── Win Celebration ──────────────────────────────
    def _celebrate(self, winner):
        self.busy = True
        self.roll_btn.config(state="disabled")
        self._log(f"\n*** {winner['name']} WINS! ***")
        self._log(f"Completed in {winner['turns']} turns!")

        # Overlay
        ov = tk.Frame(self, bg="black")
        ov.place(x=0, y=0, relwidth=1, relheight=1)

        box = tk.Frame(ov, bg=CARD, padx=40, pady=30)
        box.place(relx=.5, rely=.5, anchor="center")

        tk.Label(box, text="WINNER!",
                 font=("Impact", 46), fg=GOLD, bg=CARD).pack()
        dot = tk.Canvas(box, width=40, height=40, bg=CARD, highlightthickness=0)
        dot.pack(pady=6)
        dot.create_oval(4, 4, 36, 36, fill=winner["color"],
                        outline="white", width=3)

        tk.Label(box, text=winner["name"],
                 font=("Courier", 22, "bold"), fg=TXT, bg=CARD).pack()
        tk.Label(box, text=f"Finished in {winner['turns']} turns",
                 font=("Courier", 13), fg=TDIM, bg=CARD).pack(pady=6)

        tk.Button(box, text="Play Again",
                  font=("Courier", 13, "bold"), fg="white", bg=ACCENT,
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=lambda: self.master.goto(WelcomePage)
                  ).pack(pady=(14, 4))
        tk.Button(box, text="Quit",
                  font=("Courier", 11), fg=TDIM, bg=CARD,
                  relief="flat", cursor="hand2",
                  command=self.master.destroy
                  ).pack()

        # Confetti
        self._confetti_canvas = tk.Canvas(ov, bg="", highlightthickness=0)
        self._confetti_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._confetti_canvas.lift()
        self._confetti_pieces = []
        for _ in range(60):
            x = random.randint(100, 860)
            y = random.randint(-20, 0)
            col = random.choice([GOLD, ACCENT, "#2ECC71", "#3498DB", "#E74C3C"])
            size = random.randint(6, 14)
            item = self._confetti_canvas.create_rectangle(
                x, y, x + size, y + size, fill=col, outline="")
            self._confetti_pieces.append(
                [item, random.uniform(-1, 1), random.uniform(2, 5)])
        self._fall_confetti()

    def _fall_confetti(self):
        alive = []
        h = self.winfo_height()
        for piece in self._confetti_pieces:
            item, vx, vy = piece
            try:
                coords = self._confetti_canvas.coords(item)
                if not coords:
                    continue
                if coords[1] < h + 20:
                    self._confetti_canvas.move(item, vx, vy)
                    alive.append(piece)
            except tk.TclError:
                pass
        self._confetti_pieces = alive
        if alive:
            self.after(30, self._fall_confetti)

# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
