import tkinter as tk
from tkinter import messagebox
import requests

class DashboardScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, padx=20, pady=20)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Welcome Message
        tk.Label(self.frame, text="Welcome to the Library System Dashboard", 
                 font=("Arial", 18, "bold")).pack(pady=10)

        # Metrics Section
        metrics_frame = tk.Frame(self.frame)
        metrics_frame.pack(pady=10)

        tk.Label(metrics_frame, text="Total Books:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.total_books_label = tk.Label(metrics_frame, text="Loading...", font=("Arial", 12, "bold"))
        self.total_books_label.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(metrics_frame, text="Total Members:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.total_members_label = tk.Label(metrics_frame, text="Loading...", font=("Arial", 12, "bold"))
        self.total_members_label.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(metrics_frame, text="Issued Books:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.issued_books_label = tk.Label(metrics_frame, text="Loading...", font=("Arial", 12, "bold"))
        self.issued_books_label.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(metrics_frame, text="Overdue Returns:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.overdue_returns_label = tk.Label(metrics_frame, text="Loading...", font=("Arial", 12, "bold"))
        self.overdue_returns_label.grid(row=3, column=1, padx=10, pady=5)

        # Quick Actions Section
        quick_actions_frame = tk.Frame(self.frame, pady=10)
        quick_actions_frame.pack()

        tk.Button(quick_actions_frame, text="Add Book", command=self.add_book_action, bg="#0078d7", fg="white", width=15).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(quick_actions_frame, text="Add Member", command=self.add_member_action, bg="#0078d7", fg="white", width=15).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(quick_actions_frame, text="View Records", command=self.view_records_action, bg="#0078d7", fg="white", width=15).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(quick_actions_frame, text="Refresh", command=self.refresh_data, bg="#4CAF50", fg="white", width=15).grid(row=0, column=3, padx=10, pady=5)

        # Recent Activity Placeholder
        tk.Label(self.frame, text="Recent Activity", font=("Arial", 14, "bold")).pack(pady=10)
        recent_activity_frame = tk.Frame(self.frame, relief=tk.SUNKEN, borderwidth=1, padx=10, pady=10)
        recent_activity_frame.pack(fill=tk.BOTH, expand=True)

        self.recent_activity_label = tk.Label(recent_activity_frame, text="No recent activity yet.", font=("Arial", 12, "italic"))
        self.recent_activity_label.pack()

        # Fetch initial stats
        self.refresh_data()

    def add_book_action(self):
        messagebox.showinfo("Add Book", "Add Book functionality is not implemented yet!")

    def add_member_action(self):
        messagebox.showinfo("Add Member", "Add Member functionality is not implemented yet!")

    def view_records_action(self):
        messagebox.showinfo("View Records", "View Records functionality is not implemented yet!")

    def refresh_data(self):
        """Refresh all data (books, members, issued books, overdue returns)"""
        self.fetch_books_count()
        self.fetch_members_count()
        self.fetch_issued_books_count()
        self.fetch_overdue_returns_count()  # NEW

    def fetch_books_count(self):
        """Fetch and update the total number of books"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/books/all")
            if response.status_code == 200:
                books = response.json()
                self.total_books_label.config(text=str(len(books)))
            else:
                self.total_books_label.config(text="Error fetching")
        except requests.exceptions.RequestException as e:
            print("Error fetching books:", e)
            self.total_books_label.config(text="Server error")

    def fetch_members_count(self):
        """Fetch and update the total number of members"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/members/all")
            if response.status_code == 200:
                members = response.json()
                self.total_members_label.config(text=str(len(members)))
            else:
                self.total_members_label.config(text="Error fetching")
        except requests.exceptions.RequestException as e:
            print("Error fetching members:", e)
            self.total_members_label.config(text="Server error")

    def fetch_issued_books_count(self):
        """Fetch and update the total number of issued books"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/lending/all")
            if response.status_code == 200:
                lending_records = response.json()
                issued_books_count = sum(1 for record in lending_records if record[5] is None)
                self.issued_books_label.config(text=str(issued_books_count))
            else:
                self.issued_books_label.config(text="Error fetching")
        except requests.exceptions.RequestException as e:
            print("Error fetching lending records:", e)
            self.issued_books_label.config(text="Server error")

    def fetch_overdue_returns_count(self):
        """Fetch and update the total number of overdue returns"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/lending/overdue")
            if response.status_code == 200:
                overdue_books = response.json()
                self.overdue_returns_label.config(text=str(len(overdue_books)))
            else:
                self.overdue_returns_label.config(text="Error fetching")
        except requests.exceptions.RequestException as e:
            print("Error fetching overdue returns:", e)
            self.overdue_returns_label.config(text="Server error")