import tkinter as tk
import requests

class LoginScreen:
    def __init__(self, parent):
        self.parent = parent

        # Create the login form
        tk.Label(parent, text="Librarian Login", font=("Arial", 16)).pack(pady=20)
        tk.Label(parent, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(parent)
        self.username_entry.pack(pady=5)

        tk.Label(parent, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(parent, show="*")
        self.password_entry.pack(pady=5)

        login_button = tk.Button(parent, text="Login", command=self.login)
        login_button.pack(pady=20)

        self.message_label = tk.Label(parent, text="", fg="red")
        self.message_label.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Send login request to the backend
        try:
            response = requests.post("http://127.0.0.1:5000/api/login", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                self.message_label.config(text="Login successful!", fg="green")
            else:
                self.message_label.config(text="Invalid credentials!", fg="red")
        except Exception as e:
            self.message_label.config(text=f"Error: {e}", fg="red")
