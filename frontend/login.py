import tkinter as tk
from tkinter import messagebox
import requests


class LoginScreen:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback

        # Create a frame for the login screen
        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(expand=True)

        # Title
        tk.Label(
            self.frame, text="Library Login", font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Username label and entry
        tk.Label(self.frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(self.frame, width=30, fg="grey")
        self.username_entry.insert(0, "Enter your username")  # Placeholder
        self.username_entry.bind("<FocusIn>", self.clear_placeholder)
        self.username_entry.bind("<FocusOut>", self.set_placeholder)
        self.username_entry.grid(row=1, column=1, pady=5)

        # Password label and entry
        tk.Label(self.frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self.frame, show="*", width=30, fg="grey")
        self.password_entry.insert(0, "Enter your password")  # Placeholder
        self.password_entry.bind("<FocusIn>", self.clear_placeholder)
        self.password_entry.bind("<FocusOut>", self.set_placeholder)
        self.password_entry.grid(row=2, column=1, pady=5)

        # Error Label
        self.error_label = tk.Label(self.frame, text="", fg="red")
        self.error_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Login Button with hover effects
        self.login_button = tk.Button(
            self.frame,
            text="Login",
            command=self.handle_login,
            bg="#0078d7",
            fg="white",
            activebackground="#005bb5",
            activeforeground="white",
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=10)

    def clear_placeholder(self, event):
        if event.widget.get() in ["Enter your username", "Enter your password"]:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="black", show="*" if event.widget == self.password_entry else "")

    def set_placeholder(self, event):
        if not event.widget.get():
            if event.widget == self.username_entry:
                event.widget.insert(0, "Enter your username")
                event.widget.config(fg="grey")
            elif event.widget == self.password_entry:
                event.widget.insert(0, "Enter your password")
                event.widget.config(fg="grey", show="")

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Remove placeholders for validation
        if username == "Enter your username":
            username = ""
        if password == "Enter your password":
            password = ""

        # Simple validation
        if not username or not password:
            self.error_label.config(text="Please fill in all fields.")
            return

        # Clear previous error
        self.error_label.config(text="")

        # Perform login request
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/login",
                json={"username": username, "password": password},
            )
            if response.status_code == 200:
                messagebox.showinfo("Login Successful", "Welcome to the dashboard!")
                self.on_success_callback()
                self.frame.destroy()  # Hide login screen
            else:
                self.error_label.config(text="Invalid username or password.")
        except requests.exceptions.RequestException:
            self.error_label.config(text="Error connecting to the server.")
