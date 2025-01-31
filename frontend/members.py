import tkinter as tk

class MembersScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.frame.pack(expand=True, fill="both")

        tk.Label(self.frame, text="Members Screen", font=("Arial", 16)).pack(pady=20)
