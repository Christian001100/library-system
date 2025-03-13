import tkinter as tk
from tkinter import ttk, messagebox
import requests

class BookScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, padx=20, pady=20)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Initialize the variable for generating barcode
        self.generate_barcode_var = tk.BooleanVar()

        # Title
        tk.Label(self.frame, text="Book Management", font=("Arial", 18, "bold")).pack(pady=10)

        # Search Bar
        search_frame = tk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Search: ").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_books).pack(side=tk.LEFT, padx=5)

        # Book List (Treeview)
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Title", "Author", "ISBN", "Availability"), show="headings")
        for col in ("ID", "Title", "Author", "ISBN", "Availability"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Buttons for Actions
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Book", command=self.add_book).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update Book", command=self.update_book).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Book", command=self.delete_book).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="View History", command=self.view_history).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_books).pack(side=tk.LEFT, padx=5)

        # Load initial book data
        self.load_books()

    def load_books(self):
        """Fetch books from the Flask backend and load them into the Treeview"""
        try:
            response = requests.get("http://127.0.0.1:5000/api/books/all")
            if response.status_code == 200:
                books = response.json()
                self.tree.delete(*self.tree.get_children())  # Clear existing data
                for book in books:
                    self.tree.insert("", tk.END, values=(
                        book['id'],
                        book['title'],
                        book['author'],
                        book['isbn'],
                        "Available" if book['copies'] > 0 else "Borrowed"
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch books.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")

    def search_books(self):
        """Filter books based on search criteria"""
        search_term = self.search_entry.get().lower()
        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            if any(search_term in str(value).lower() for value in values):
                self.tree.reattach(row, "", tk.END)  # Show row if it matches search
            else:
                self.tree.detach(row)  # Hide row if it doesn't match

    def add_book(self):
        """Open a form to add a new book"""
        self.book_form("Add Book", self.save_book)

    def update_book(self):
        """Update selected book"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book to update.")
            return

        book_values = self.tree.item(selected, "values")
        self.book_form("Update Book", self.save_changes, book_values)

    def delete_book(self):
        """Delete the selected book"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book to delete.")
            return

        book_id = self.tree.item(selected, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?")
        if confirm:
            try:
                response = requests.delete(f"http://127.0.0.1:5000/api/books/delete/{book_id}")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Book deleted successfully!")
                    self.tree.delete(selected)
                else:
                    error_msg = response.json().get('error', 'Failed to delete book')
                    messagebox.showerror("Error", error_msg)
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to connect to the server: {e}")

    def book_form(self, title, save_command, book=None):
        """Create book form for adding/updating"""
        form = tk.Toplevel(self.parent)
        form.title(title)

        tk.Label(form, text="Title:").grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(form)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Author:").grid(row=1, column=0, padx=10, pady=5)
        author_entry = tk.Entry(form)
        author_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form, text="ISBN:").grid(row=2, column=0, padx=10, pady=5)
        isbn_entry = tk.Entry(form)
        isbn_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form, text="Copies Available:").grid(row=3, column=0, padx=10, pady=5)
        copies_entry = tk.Entry(form)
        copies_entry.grid(row=3, column=1, padx=10, pady=5)

        # Add Generate Barcode checkbox
        tk.Checkbutton(form, text="Generate Barcode", variable=self.generate_barcode_var).grid(row=4, column=0, padx=10, pady=5)

        if book:
            title_entry.insert(0, book[1])  # Populate title field
            author_entry.insert(0, book[2])  # Populate author field
            isbn_entry.insert(0, book[3])    # Populate ISBN field
            copies_entry.insert(0, book[4])  # Populate copies field

        tk.Button(form, text="Save", command=lambda: save_command(form, book[0] if book else None, title_entry, author_entry, isbn_entry, copies_entry)).grid(row=5, column=1, pady=10)

    def save_book(self, form, _, title_entry, author_entry, isbn_entry, copies_entry):
        """Save new book"""
        title = title_entry.get()
        author = author_entry.get()
        isbn = isbn_entry.get()
        copies = copies_entry.get()
        generate_barcode = self.generate_barcode_var.get()

        if title and author and isbn and copies:
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/api/books/create",
                    json={
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "copies": int(copies),
                        "generate_barcode": generate_barcode
                    }
                )
                if response.status_code == 201:
                    messagebox.showinfo("Success", "Book added successfully!")
                    self.load_books()
                    form.destroy()
                else:
                    error_msg = response.json().get('error', 'Failed to add book')
                    messagebox.showerror("Error", error_msg)
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to connect to the server: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    def save_changes(self, form, book_id, title_entry, author_entry, isbn_entry, copies_entry):
        """Save updated book details"""
        title = title_entry.get()
        author = author_entry.get()
        isbn = isbn_entry.get()
        copies = copies_entry.get()

        if title and author and copies and copies.isdigit():
            try:
                response = requests.put(
                    f"http://127.0.0.1:5000/api/books/update/{book_id}",
                    json={
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "copies": int(copies)
                    }
                )
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Book updated successfully!")
                    self.load_books()
                    form.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update book.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to connect to the server: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    def view_history(self):
        """Show borrowing history for selected book"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book to view its history.")
            return
            
        book_id = self.tree.item(selected, "values")[0]
        try:
            response = requests.get(f"http://127.0.0.1:5000/api/books/history/{book_id}")
            if response.status_code == 200:
                history = response.json()
                self.show_history_window(history)
            else:
                messagebox.showerror("Error", "Failed to fetch book history.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")

    def show_history_window(self, history):
        """Create a window to display borrowing history"""
        history_window = tk.Toplevel(self.parent)
        history_window.title("Book Borrowing History")
        
        # Create Treeview
        tree = ttk.Treeview(history_window, columns=("Member", "Issue Date", "Due Date", "Return Date"), show="headings")
        tree.heading("Member", text="Member")
        tree.heading("Issue Date", text="Issue Date")
        tree.heading("Due Date", text="Due Date")
        tree.heading("Return Date", text="Return Date")
        tree.pack(fill=tk.BOTH, expand=True)

        # Insert history records
        for record in history:
            tree.insert("", tk.END, values=(
                record["MemberName"],
                record["IssueDate"],
                record["DueDate"],
                record["ReturnDate"]
            ))

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BookScreen(root)
    root.mainloop()