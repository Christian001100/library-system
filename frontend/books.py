import tkinter as tk

class BooksScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.frame.pack(expand=True, fill="both")

        tk.Label(self.frame, text="Books Screen", font=("Arial", 16)).pack(pady=20)
