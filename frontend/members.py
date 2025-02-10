import tkinter as tk
from tkinter import ttk, messagebox
import requests

class MemberScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, padx=20, pady=20)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Title
        tk.Label(self.frame, text="Member Management", font=("Arial", 18, "bold")).pack(pady=10)

        # Search Bar
        search_frame = tk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_members).pack(side=tk.LEFT, padx=5)

        # Member List (Treeview)
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Name", "Contact", "Join Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Join Date", text="Join Date")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Buttons for Actions
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Member", command=self.add_member).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update Member", command=self.update_member).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Member", command=self.delete_member).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="View Borrowing History", command=self.view_borrowing_history).pack(side=tk.LEFT, padx=5)

        # Load initial member data
        self.load_members()

    def load_members(self):
        """Fetch members from the Flask backend and load them into the Treeview"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/members/all")
            if response.status_code == 200:
                members = response.json()
                # Clear existing data
                for row in self.tree.get_children():
                    self.tree.delete(row)
                # Add members to the Treeview
                for member in members:
                    # Access fields by index (assuming the order is: MemberID, Name, Contact, JoinDate)
                    self.tree.insert("", tk.END, values=(
                        member[0],  # MemberID
                        member[1],  # Name
                        member[2],  # Contact
                        member[3]   # JoinDate
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch members.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")

    def search_members(self):
        """Filter members based on search criteria"""
        search_term = self.search_entry.get().lower()
        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            if search_term in values[1].lower() or search_term in values[0].lower():  # Search by name or ID
                self.tree.selection_set(row)
                self.tree.focus(row)
            else:
                self.tree.detach(row)

    def add_member(self):
        """Open a form to add a new member"""
        form = tk.Toplevel(self.parent)
        form.title("Add Member")

        tk.Label(form, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(form)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Contact:").grid(row=1, column=0, padx=10, pady=5)
        contact_entry = tk.Entry(form)
        contact_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_member():
            name = name_entry.get()
            contact = contact_entry.get()
            if name:
                try:
                    response = requests.post(
                        "http://127.0.0.1:5000/api/members/create",
                        json={"name": name, "contact": contact}
                    )
                    if response.status_code == 200:
                        messagebox.showinfo("Success", "Member added successfully!")
                        self.load_members()  # Refresh the member list
                        form.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to add member.")
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to connect to the server: {e}")
            else:
                messagebox.showwarning("Input Error", "Name is required.")

        tk.Button(form, text="Save", command=save_member).grid(row=2, column=1, pady=10)

    def update_member(self):
        """Update the selected member's details"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a member to update.")
            return

        # Get the selected member's details
        member_id, name, contact, join_date = self.tree.item(selected, "values")

        # Open a form to update the member
        form = tk.Toplevel(self.parent)
        form.title("Update Member")

        tk.Label(form, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(form)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Contact:").grid(row=1, column=0, padx=10, pady=5)
        contact_entry = tk.Entry(form)
        contact_entry.insert(0, contact)
        contact_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_changes():
            new_name = name_entry.get()
            new_contact = contact_entry.get()
            if new_name:
                try:
                    # Assuming you have an update endpoint (e.g., /members/update/<int:member_id>)
                    response = requests.put(
                        f"http://127.0.0.1:5000/api/members/update/{member_id}",
                        json={"name": new_name, "contact": new_contact}
                    )
                    if response.status_code == 200:
                        messagebox.showinfo("Success", "Member updated successfully!")
                        self.load_members()  # Refresh the member list
                        form.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update member.")
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to connect to the server: {e}")
            else:
                messagebox.showwarning("Input Error", "Name is required.")

        tk.Button(form, text="Save", command=save_changes).grid(row=2, column=1, pady=10)

    def delete_member(self):
        """Delete the selected member"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a member to delete.")
            return

        member_id = self.tree.item(selected, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?")
        if confirm:
            try:
                # Assuming you have a delete endpoint (e.g., /members/delete/<int:member_id>)
                response = requests.delete(f"http://127.0.0.1:5000/api/members/delete/{member_id}")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Member deleted successfully!")
                    self.load_members()  # Refresh the member list
                else:
                    messagebox.showerror("Error", "Failed to delete member.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to connect to the server: {e}")

    def view_borrowing_history(self):
        """Show the borrowing history of the selected member"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a member to view their borrowing history.")
            return

        member_id = self.tree.item(selected, "values")[0]  # Get the selected member's ID
        member_name = self.tree.item(selected, "values")[1]  # Get the selected member's name

        # Fetch borrowing history from the backend
        try:
            response = requests.get(f"http://127.0.0.1:5000/api/members/{member_id}/borrowing-history")
            if response.status_code == 200:
                history = response.json()
                # Open a new window to display borrowing history
                history_window = tk.Toplevel(self.parent)
                history_window.title(f"Borrowing History - {member_name}")

                # Display history in a Treeview
                history_tree = ttk.Treeview(history_window, columns=("BookTitle", "IssueDate", "DueDate", "ReturnDate"), show="headings")
                history_tree.heading("BookTitle", text="Book Title")
                history_tree.heading("IssueDate", text="Issue Date")
                history_tree.heading("DueDate", text="Due Date")
                history_tree.heading("ReturnDate", text="Return Date")
                history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                for record in history:
                    history_tree.insert("", tk.END, values=(
                        record["BookTitle"],  # Updated key
                        record["IssueDate"],
                        record["DueDate"],
                        record["ReturnDate"]
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch borrowing history.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")
