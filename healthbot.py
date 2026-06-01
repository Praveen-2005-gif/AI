import customtkinter as ctk
from tkinter import END
from google import genai
import threading

# ==========================
# GEMINI API KEY
# ==========================
API_KEY = "AQ.Ab8RN6IzCTZyHXYNqLEpP63ISjdjUzh69htLOIB4JS2s7hck6w"

client = genai.Client(api_key=API_KEY)

# ==========================
# HEALTH BOT PROMPT
# ==========================
SYSTEM_PROMPT = """
You are HealthBot, a professional hospital assistant.

Hospital Name: City Care Hospital

Departments:
- Cardiology
- Neurology
- Orthopedics
- Pediatrics
- Dermatology
- General Medicine

Emergency Number: +91-9876543210
Reception Number: +91-9876543211

Rules:
- Answer hospital and healthcare questions.
- Be polite and professional.
- Do not prescribe medicines.
- Suggest consulting a doctor for serious conditions.
"""

# ==========================
# WINDOW
# ==========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("💙 HealthBot")
app.geometry("900x700")

# Background
app.configure(fg_color=("#0f172a", "#0f172a"))

# ==========================
# HEADER
# ==========================
header = ctk.CTkFrame(
    app,
    corner_radius=20,
    fg_color="#0284c7",
    height=100
)
header.pack(fill="x", padx=15, pady=15)

title = ctk.CTkLabel(
    header,
    text="💙 HealthBot",
    font=("Segoe UI", 30, "bold"),
    text_color="white"
)
title.pack(pady=(15, 0))

subtitle = ctk.CTkLabel(
    header,
    text="Your Personal Health Assistant",
    font=("Segoe UI", 15),
    text_color="white"
)
subtitle.pack()

# ==========================
# CHAT AREA
# ==========================
chat_frame = ctk.CTkFrame(
    app,
    corner_radius=20
)
chat_frame.pack(fill="both", expand=True, padx=15)

chat_box = ctk.CTkTextbox(
    chat_frame,
    font=("Segoe UI", 15),
    wrap="word"
)
chat_box.pack(fill="both", expand=True, padx=10, pady=10)

chat_box.insert(
    END,
    "🏥 Welcome to HealthBot!\n\n"
    "I can help you with:\n"
    "• Hospital Information\n"
    "• Doctor Departments\n"
    "• Appointments\n"
    "• Emergency Contacts\n"
    "• General Health Guidance\n\n"
    "How can I help you today?\n\n"
)

# ==========================
# SEND MESSAGE
# ==========================
def get_response(message):

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser: {message}"
        )

        reply = response.text

    except Exception as e:
        reply = f"Error: {e}"

    chat_box.insert(END, f"\n💙 HealthBot:\n{reply}\n\n")
    chat_box.see(END)

def send_message():

    msg = entry.get().strip()

    if not msg:
        return

    chat_box.insert(END, f"\n🧑 You:\n{msg}\n")
    chat_box.see(END)

    entry.delete(0, END)

    threading.Thread(
        target=get_response,
        args=(msg,),
        daemon=True
    ).start()

# ==========================
# INPUT AREA
# ==========================
bottom = ctk.CTkFrame(
    app,
    corner_radius=20,
    height=80
)
bottom.pack(fill="x", padx=15, pady=15)

entry = ctk.CTkEntry(
    bottom,
    placeholder_text="Type your health question...",
    height=45,
    font=("Segoe UI", 15)
)
entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=10,
    pady=10
)

send_btn = ctk.CTkButton(
    bottom,
    text="➤ Send",
    width=120,
    height=45,
    command=send_message,
    font=("Segoe UI", 15, "bold"),
    fg_color="#06b6d4",
    hover_color="#0891b2"
)
send_btn.pack(side="right", padx=10)

entry.bind("<Return>", lambda event: send_message())

# ==========================
# RUN
# ==========================
app.mainloop()
