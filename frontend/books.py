import tkinter as tk
from tkinter import ttk, messagebox
import requests

class BookScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, padx=20, pady=20)
        self.frame.pack(expand=True, fill=tk.BOTH)

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
                    self.tree.insert("", tk.END, values=(book['id'], book['title'], book['author'], book['isbn'], book['availability']))
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

        book_id = self.tree.item(selected, "values")[0]  # Extract book ID from the selected row
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?")
        
        if confirm:
            try:
                response = requests.delete(f"http://127.0.0.1:5000/api/books/delete/{book_id}")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Book deleted successfully!")
                    self.tree.delete(selected)  # Remove the book from the UI
                else:
                    messagebox.showerror("Error", f"Failed to delete book. {response.json().get('message', 'Unknown error')}")
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

        if book:
            title_entry.insert(0, book[1])
            author_entry.insert(0, book[2])
            isbn_entry.insert(0, book[3])

        tk.Button(form, text="Save", command=lambda: save_command(form, book[0] if book else None, title_entry, author_entry, isbn_entry)).grid(row=3, column=1, pady=10)

    def save_book(self, form, _, title_entry, author_entry, isbn_entry):
        """Save new book"""
        title, author, isbn = title_entry.get(), author_entry.get(), isbn_entry.get()
        if title and author and isbn:
            response = requests.post("http://127.0.0.1:5000/api/books/create", json={"title": title, "author": author, "isbn": isbn})
            if response.status_code == 201:
                messagebox.showinfo("Success", "Book added successfully!")
                self.load_books()
                form.destroy()
            else:
                error_msg = response.json().get('message', 'Failed to add book')
                messagebox.showerror("Error", error_msg)

        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    def save_changes(self, form, book_id, title_entry, author_entry, _):
        """Save updated book details"""
        title, author = title_entry.get(), author_entry.get()
        if title and author:
            response = requests.put(f"http://127.0.0.1:5000/api/books/update/{book_id}", json={"title": title, "author": author})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Book updated successfully!")
                self.load_books()
                form.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required.")
