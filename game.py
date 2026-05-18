import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("Snake and Ladder Game")
root.geometry("760x1200")
root.configure(bg="white")
root.resizable(False, False)

# ---------------- BOARD SETTINGS ----------------
BOARD_SIZE = 620
CELL_SIZE = 62

# ---------------- SNAKES BASED ON BOARD IMAGE ----------------
snakes = {

    # Green snake
    98: 79,

    # Yellow snake
    95: 75,

    # Orange snake
    92: 72,

    # Blue snake
    74: 53,

    # Red snake
    69: 49,

    # Purple snake middle
    62: 38,

    # Green snake bottom
    46: 25,

    # Purple snake bottom
    16: 6
}

# ---------------- LADDERS BASED ON BOARD IMAGE ----------------
ladders = {

    # Left ladder
    19: 42,

    # Small middle ladder
    36: 44,

    # Big middle ladder
    58: 84,

    # Blue snake side ladder
    54: 67,

    # Right ladder
    9: 33,

    # Bottom small ladder
    6: 26,

    # Top-right ladder
    70: 91
}

# ---------------- GAME VARIABLES ----------------
players = []
positions = {}
turn = 0
game_started = False

# ---------------- LOAD BOARD IMAGE ----------------
board = Image.open("board.png")
board = board.resize((BOARD_SIZE, BOARD_SIZE))
board_img = ImageTk.PhotoImage(board)

# ---------------- CANVAS ----------------
canvas = tk.Canvas(
    root,
    width=BOARD_SIZE,
    height=BOARD_SIZE,
    bg="white",
    highlightthickness=0
)
canvas.pack(pady=10)

canvas.create_image(0, 0, anchor="nw", image=board_img)

# ---------------- LOAD PAWN IMAGES ----------------
red = Image.open("red_pawn.png")
red = red.resize((28, 28))
red_img = ImageTk.PhotoImage(red)

blue = Image.open("blue_pawn.png")
blue = blue.resize((28, 28))
blue_img = ImageTk.PhotoImage(blue)

# ---------------- CREATE PAWNS ----------------
red_pawn = canvas.create_image(20, 590, image=red_img)
blue_pawn = canvas.create_image(45, 590, image=blue_img)

# ---------------- GET BOARD COORDINATES ----------------
def get_coordinates(position):

    if position == 0:
        return 25, 665

    position -= 1

    row = position // 10
    col = position % 10

    # Alternate row direction
    if row % 2 == 1:
        col = 9 - col

    x = col * CELL_SIZE + 35
    y = (9 - row) * CELL_SIZE + 35

    return x, y

# ---------------- UPDATE PAWN ----------------
def update_pawn(player):

    x, y = get_coordinates(positions[player])

    if player == players[0]:
        canvas.coords(red_pawn, x, y)
    else:
        canvas.coords(blue_pawn, x + 20, y)

# ---------------- STEP BY STEP MOVEMENT ----------------
def animate_move(player, start, end):

    for step in range(start + 1, end + 1):

        positions[player] = step
        update_pawn(player)

        root.update()
        root.after(250)

# ---------------- MOVE PLAYER ----------------
def move_player(player, dice):

    start = positions[player]
    end = start + dice

    if end > 100:
        return

    # Move step-by-step
    animate_move(player, start, end)

    positions[player] = end

    # Snake
    if end in snakes:

        messagebox.showinfo(
            "Snake",
            f"🐍 {player} bitten by snake!\nGo to {snakes[end]}"
        )

        positions[player] = snakes[end]
        update_pawn(player)

    # Ladder
    elif end in ladders:

        messagebox.showinfo(
            "Ladder",
            f"🪜 {player} climbed ladder!\nGo to {ladders[end]}"
        )

        positions[player] = ladders[end]
        update_pawn(player)

# ---------------- ROLL DICE ----------------
def roll_dice():

    global turn

    if not game_started:

        messagebox.showwarning(
            "Game",
            "Please choose game mode first"
        )
        return

    current_player = players[turn]

    dice = random.randint(1, 6)

    # Show dice value
    dice_label.config(
        text=f"🎲 {current_player} rolled : {dice}"
    )

    # Move player
    move_player(current_player, dice)

    # Check winner
    if positions[current_player] == 100:

        messagebox.showinfo(
            "Winner",
            f"🎉 {current_player} Wins!"
        )

        return

    # Change turn
    turn = 1 - turn

    next_player = players[turn]

    status_label.config(
        text=f"{next_player}'s Turn"
    )

    # Computer auto move
    if next_player == "Computer":
        root.after(1000, roll_dice)

# ---------------- PLAYER VS PLAYER ----------------
def start_pvp():

    global players
    global positions
    global turn
    global game_started

    players = ["Player 1", "Player 2"]

    positions = {
        "Player 1": 0,
        "Player 2": 0
    }

    turn = 0
    game_started = True

    update_pawn("Player 1")
    update_pawn("Player 2")

    status_label.config(
        text="Player 1 Turn"
    )

    dice_label.config(
        text="🎲 Dice : -"
    )

# ---------------- PLAYER VS COMPUTER ----------------
def start_computer():

    global players
    global positions
    global turn
    global game_started

    players = ["Player 1", "Computer"]

    positions = {
        "Player 1": 0,
        "Computer": 0
    }

    turn = 0
    game_started = True

    update_pawn("Player 1")
    update_pawn("Computer")

    status_label.config(
        text="Player 1 Turn"
    )

    dice_label.config(
        text="🎲 Dice : -"
    )

# ---------------- BUTTON FRAME ----------------
frame = tk.Frame(root, bg="white")
frame.pack(pady=10)

# ---------------- BUTTONS ----------------
pvp_button = tk.Button(
    frame,
    text="👥 Player vs Player",
    font=("Arial", 12, "bold"),
    bg="lightgreen",
    width=18,
    command=start_pvp
)
pvp_button.grid(row=0, column=0, padx=10)

computer_button = tk.Button(
    frame,
    text="🤖 Vs Computer",
    font=("Arial", 12, "bold"),
    bg="lightblue",
    width=18,
    command=start_computer
)
computer_button.grid(row=0, column=1, padx=10)

dice_button = tk.Button(
    frame,
    text="🎲 Roll Dice",
    font=("Arial", 12, "bold"),
    bg="orange",
    width=15,
    command=roll_dice
)
dice_button.grid(row=1, column=0, pady=10)

exit_button = tk.Button(
    frame,
    text="❌ Exit",
    font=("Arial", 12, "bold"),
    bg="red",
    fg="white",
    width=15,
    command=root.destroy
)
exit_button.grid(row=1, column=1)

# ---------------- DICE LABEL ----------------
dice_label = tk.Label(
    root,
    text="🎲 Dice : -",
    font=("Arial", 16, "bold"),
    bg="white"
)
dice_label.pack(pady=5)

# ---------------- STATUS LABEL ----------------
status_label = tk.Label(
    root,
    text="Choose Game Mode",
    font=("Arial", 16, "bold"),
    bg="white"
)
status_label.pack()

# ---------------- START GAME ----------------
root.mainloop()