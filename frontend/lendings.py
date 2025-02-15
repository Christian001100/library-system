import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LendingsScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Lend Book Section
        lend_frame = tk.LabelFrame(self.frame, text="Lend a Book", padx=10, pady=10)
        lend_frame.pack(fill="x", pady=(0, 20))
        
        # Book Selection
        tk.Label(lend_frame, text="Book:").grid(row=0, column=0, padx=5, pady=5)
        self.book_var = tk.StringVar()
        self.book_dropdown = ttk.Combobox(lend_frame, textvariable=self.book_var, state="readonly")
        self.book_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Member Selection
        tk.Label(lend_frame, text="Member:").grid(row=1, column=0, padx=5, pady=5)
        self.member_var = tk.StringVar()
        self.member_dropdown = ttk.Combobox(lend_frame, textvariable=self.member_var, state="readonly")
        self.member_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Lend Button
        tk.Button(lend_frame, text="Lend Book", command=self.lend_book).grid(row=2, column=0, columnspan=2, pady=10)

        # Return Book Section
        return_frame = tk.LabelFrame(self.frame, text="Return a Book", padx=10, pady=10)
        return_frame.pack(fill="x", pady=(0, 20))
        
        # Loan Selection
        tk.Label(return_frame, text="Loan:").grid(row=0, column=0, padx=5, pady=5)
        self.loan_var = tk.StringVar()
        self.loan_dropdown = ttk.Combobox(return_frame, textvariable=self.loan_var, state="readonly")
        self.loan_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Return Button
        tk.Button(return_frame, text="Return Book", command=self.return_book).grid(row=1, column=0, columnspan=2, pady=10)

        # Active Loans Table
        loans_frame = tk.LabelFrame(self.frame, text="Active Loans", padx=10, pady=10)
        loans_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        columns = ("ID", "Book", "Member", "Issue Date", "Due Date")
        self.loans_tree = ttk.Treeview(loans_frame, columns=columns, show="headings")
        self.loans_tree.pack(fill="both", expand=True)
        
        for col in columns:
            self.loans_tree.heading(col, text=col)
            self.loans_tree.column(col, width=100)
        
        # Search & Filter Section
        search_frame = tk.LabelFrame(self.frame, text="Search & Filter", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(search_frame, text="Search", command=self.search_loans).grid(row=0, column=2, padx=5, pady=5)

        # Overdue Books Section
        overdue_frame = tk.LabelFrame(self.frame, text="Overdue Books", padx=10, pady=10)
        overdue_frame.pack(fill="x")
        
        columns = ("ID", "Book", "Member", "Due Date", "Days Overdue")
        self.overdue_tree = ttk.Treeview(overdue_frame, columns=columns, show="headings")
        self.overdue_tree.pack(fill="both", expand=True)
        
        for col in columns:
            self.overdue_tree.heading(col, text=col)
            self.overdue_tree.column(col, width=100)

        # Load initial data
        self.load_data()

    def load_data(self):
        """Load initial data for dropdowns and tables"""
        try:
            logger.debug("Loading books and members data")
            # Load books and members for dropdowns
            books_response = self.fetch_data("http://localhost:5000/api/books/all")
            members_response = self.fetch_data("http://localhost:5000/api/members/all")
            
            logger.debug(f"Books response: {json.dumps(books_response, indent=2)}")
            logger.debug(f"Members response: {json.dumps(members_response, indent=2)}")
            
            if books_response and isinstance(books_response, list):
                self.book_dropdown['values'] = [f"{b['title']} (ID: {b['id']})" for b in books_response]
            elif books_response and 'data' in books_response:
                self.book_dropdown['values'] = [f"{b['title']} (ID: {b['id']})" for b in books_response['data']]
            
            if members_response and isinstance(members_response, list):
                self.member_dropdown['values'] = [f"{m['name']} (ID: {m['id']})" for m in members_response]
            elif members_response and 'data' in members_response:
                self.member_dropdown['values'] = [f"{m['name']} (ID: {m['id']})" for m in members_response['data']]
            
            # Load active loans
            self.refresh_loans()
            
            # Load overdue books
            self.refresh_overdue()
                
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def fetch_data(self, url):
        """Helper method to fetch data from API"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {url}: {str(e)}")
            return None

    def refresh_loans(self):
        """Refresh the active loans table"""
        try:
            logger.debug("Refreshing loans data")
            # Clear existing items
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)
            
            # Load active loans
            loans = self.fetch_data("http://localhost:5000/api/lending/all")
            logger.debug(f"Loans response: {json.dumps(loans, indent=2)}")
            
            if loans and isinstance(loans, list):
                for loan in loans:
                    self.loans_tree.insert("", "end", values=(
                        loan['id'],
                        loan['book_title'],
                        loan['member_name'],
                        loan['issue_date'],
                        loan['due_date']
                    ))
            elif loans and 'data' in loans:
                for loan in loans['data']:
                    self.loans_tree.insert("", "end", values=(
                        loan['id'],
                        loan['book_title'],
                        loan['member_name'],
                        loan['issue_date'],
                        loan['due_date']
                    ))
        except Exception as e:
            logger.error(f"Failed to refresh loans: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh loans: {str(e)}")

    def refresh_overdue(self):
        """Refresh the overdue books table"""
        try:
            logger.debug("Refreshing overdue books data")
            # Clear existing items
            for item in self.overdue_tree.get_children():
                self.overdue_tree.delete(item)
            
            # Load overdue books
            overdue = self.fetch_data("http://localhost:5000/api/lending/overdue")
            logger.debug(f"Overdue response: {json.dumps(overdue, indent=2)}")
            
            if overdue and isinstance(overdue, list):
                for book in overdue:
                    days_overdue = (datetime.now() - datetime.strptime(book['due_date'], "%Y-%m-%d")).days
                    self.overdue_tree.insert("", "end", values=(
                        book['id'],
                        book['book_title'],
                        book['member_name'],
                        book['due_date'],
                        days_overdue
                    ))
            elif overdue and 'data' in overdue:
                for book in overdue['data']:
                    days_overdue = (datetime.now() - datetime.strptime(book['due_date'], "%Y-%m-%d")).days
                    self.overdue_tree.insert("", "end", values=(
                        book['id'],
                        book['book_title'],
                        book['member_name'],
                        book['due_date'],
                        days_overdue
                    ))
        except Exception as e:
            logger.error(f"Failed to refresh overdue books: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh overdue books: {str(e)}")

    def lend_book(self):
        """Handle lending a book"""
        try:
            book_id = self.book_var.get().split("(ID: ")[1][:-1]
            member_id = self.member_var.get().split("(ID: ")[1][:-1]
            
            response = requests.post("http://localhost:5000/api/lending/create", json={
                "book_id": book_id,
                "member_id": member_id
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Book lent successfully!")
                self.refresh_loans()
                self.refresh_overdue()
            else:
                error_msg = response.json().get("message", "Failed to lend book")
                logger.error(f"Lending failed: {error_msg}")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            logger.error(f"Lending error: {str(e)}")
            messagebox.showerror("Error", f"Failed to lend book: {str(e)}")

    def return_book(self):
        """Handle returning a book"""
        try:
            loan_id = self.loan_var.get().split("(ID: ")[1][:-1]
            
            response = requests.put(f"http://localhost:5000/api/lending/id{loan_id}")
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Book returned successfully!")
                self.refresh_loans()
                self.refresh_overdue()
            else:
                error_msg = response.json().get("message", "Failed to return book")
                logger.error(f"Return failed: {error_msg}")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            logger.error(f"Return error: {str(e)}")
            messagebox.showerror("Error", f"Failed to return book: {str(e)}")

    def search_loans(self):
        """Handle searching loans"""
        search_term = self.search_entry.get().lower()
        
        for item in self.loans_tree.get_children():
            values = self.loans_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.loans_tree.selection_set(item)
            else:
                self.loans_tree.selection_remove(item)
