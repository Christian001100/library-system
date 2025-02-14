import tkinter as tk
from login import LoginScreen
from dashboard import DashboardScreen
from members import MemberScreen
from books import BookScreen  # ✅ Import BooksScreen
from lendings import LendingsScreen

class Sidebar:
    def __init__(self, root, content_frame):
        self.root = root
        self.content_frame = content_frame

        # Create the sidebar frame
        self.sidebar_frame = tk.Frame(root, bg="#333333", width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Add navigation buttons
        self.add_nav_button("Dashboard", self.show_dashboard)  # ✅ Fixed
       
        self.add_nav_button("Members", MemberScreen)
        self.add_nav_button("Books", BookScreen)  # ✅ Use BookScreen

        self.add_nav_button("Lendings", LendingsScreen)

    def add_nav_button(self, text, screen_class):
        btn = tk.Button(self.sidebar_frame, text=text, bg="#444444", fg="white",
                        font=("Arial", 12), relief=tk.FLAT)
        
        # Fix: Handle `show_dashboard` separately
        if text == "Dashboard":
            btn.config(command=self.show_dashboard)  # ✅ Directly link to method
        else:
            btn.config(command=lambda: self.switch_to(screen_class))

        btn.pack(fill=tk.X, pady=5, padx=10)

    def switch_to(self, screen_class):
        # Clear current content and show the selected screen
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        screen_class(self.content_frame)

    def show_dashboard(self):
        # Clear content and show the Dashboard
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        DashboardScreen(self.content_frame)  # ✅ Show Dashboard properly
