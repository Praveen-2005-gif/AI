# =========================================================
# FREE OFFLINE AI CHATBOT
# =========================================================

import tkinter as tk
from tkinter import scrolledtext
from gpt4all import GPT4All
import threading

# =========================================================
# LOAD AI MODEL
# =========================================================

chatbot = GPT4All(
    "orca-mini-3b-gguf2-q4_0.gguf",
    device="cpu"
)

# =========================================================
# WINDOW
# =========================================================

root = tk.Tk()

root.title("Offline AI Chatbot")
root.geometry("900x700")
root.configure(bg="#1e1e1e")

# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="OFFLINE AI CHATBOT",
    font=("Arial", 24, "bold"),
    bg="#1e1e1e",
    fg="#00ffff"
)

title.pack(pady=10)

# =========================================================
# CHAT AREA
# =========================================================

chat_area = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Arial", 13),
    bg="#2b2b2b",
    fg="white",
    insertbackground="white"
)

chat_area.pack(
    padx=15,
    pady=10,
    fill=tk.BOTH,
    expand=True
)

chat_area.insert(
    tk.END,
    "Bot: Hello! I am your offline AI assistant.\n\n"
)

# =========================================================
# INPUT FRAME
# =========================================================

input_frame = tk.Frame(root, bg="#1e1e1e")

input_frame.pack(
    fill=tk.X,
    padx=10,
    pady=10
)

# =========================================================
# USER INPUT
# =========================================================

user_input = tk.Entry(
    input_frame,
    font=("Arial", 14),
    bg="#3b3b3b",
    fg="white",
    insertbackground="white"
)

user_input.pack(
    side=tk.LEFT,
    fill=tk.X,
    expand=True,
    padx=(0, 10)
)

# =========================================================
# PROCESS MESSAGE
# =========================================================

def process_message(message):

    if message.strip() == "":
        return

    # USER MESSAGE
    chat_area.insert(
        tk.END,
        f"You: {message}\n\n"
    )

    # TYPING
    chat_area.insert(
        tk.END,
        "Bot is typing...\n\n"
    )

    chat_area.yview(tk.END)

    user_input.delete(0, tk.END)

    try:

        # AI RESPONSE
        response = chatbot.generate(
            message,
            max_tokens=200
        )

        # REMOVE typing...
        chat_area.delete("end-3l", "end-1l")

        # SHOW BOT RESPONSE
        chat_area.insert(
            tk.END,
            f"Bot: {response}\n\n"
        )

        chat_area.yview(tk.END)

    except Exception as e:

        chat_area.insert(
            tk.END,
            f"Error:\n{e}\n\n"
        )

# =========================================================
# SEND FUNCTION
# =========================================================

def send_message():

    message = user_input.get()

    threading.Thread(
        target=process_message,
        args=(message,)
    ).start()

# =========================================================
# SEND BUTTON
# =========================================================

send_button = tk.Button(
    input_frame,
    text="Send",
    font=("Arial", 12, "bold"),
    bg="#00aa00",
    fg="white",
    width=10,
    command=send_message
)

send_button.pack(side=tk.RIGHT)

# =========================================================
# ENTER KEY SUPPORT
# =========================================================

root.bind(
    "<Return>",
    lambda event: send_message()
)

# =========================================================
# RUN APP
# =========================================================

root.mainloop()