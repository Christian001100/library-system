import tkinter as tk
from login import LoginScreen

class Sidebar:
    def __init__(self, root, content_frame):
        self.content_frame = content_frame

        # Create the sidebar frame
        self.sidebar_frame = tk.Frame(root, bg="#333333", width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Add navigation buttons
        self.add_nav_button("Login", LoginScreen)
        self.add_nav_button("Members", lambda: print("Members Screen"))
        self.add_nav_button("Books", lambda: print("Books Screen"))
        self.add_nav_button("Lendings", lambda: print("Lendings Screen"))

    def add_nav_button(self, text, command):
        btn = tk.Button(self.sidebar_frame, text=text, bg="#444444", fg="white",
                        font=("Arial", 12), relief=tk.FLAT, command=lambda: self.switch_to(command))
        btn.pack(fill=tk.X, pady=5, padx=10)

    def switch_to(self, screen_class):
        # Clear current content and show the selected screen
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        screen_class(self.content_frame)
