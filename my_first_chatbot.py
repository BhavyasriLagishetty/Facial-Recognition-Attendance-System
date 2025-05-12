import tkinter as tk
from tkinter import scrolledtext
import requests
import os

# Set your GROQ API key here or use environment variables
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot")
        self.root.geometry("500x600")

        # Chat Display Area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", font=("Arial", 12))
        self.chat_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # User Input Field
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)

        self.input_field = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind("<Return>", self.send_message)

        # Send Button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, font=("Arial", 12), bg="green", fg="white")
        self.send_button.pack(side=tk.RIGHT)

    def get_response(self, user_input):
        """Get response from Groq API."""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0.7
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return (
                "❗ Could not connect to Groq API.\n\n"
                "Make sure:\n"
                "1. You have a valid GROQ_API_KEY.\n"
                "2. Internet connection is active.\n"
                "3. API endpoint is reachable.\n\n"
                f"Error details: {str(e)}"
            )

    def send_message(self, event=None):
        """Handles user input and displays bot response."""
        user_input = self.input_field.get().strip()
        if user_input:
            self.display_message(f"You: {user_input}", "blue")
            response = self.get_response(user_input)
            self.display_message(f"Bot: {response}", "green")
            self.input_field.delete(0, tk.END)

    def display_message(self, message, color):
        """Displays messages in chat area."""
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, message + "\n\n", color)
        self.chat_area.config(state="disabled")
        self.chat_area.tag_config(color, foreground=color)
        self.chat_area.yview(tk.END)

# Run the chatbot
if __name__ == "__main__":
    root = tk.Tk()
    chat = ChatBot(root)
    root.mainloop()
