import tkinter as tk
from tkinter import ttk, messagebox
import requests
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
        lend_frame.pack(fill="x", pady=(10, 20))

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

        # Active Loans Table
        loans_frame = tk.LabelFrame(self.frame, text="Active Loans", padx=10, pady=10)
        loans_frame.pack(fill="both", expand=True, pady=(10, 20))

        # Add Return Button to Active Loans Table
        return_button = tk.Button(loans_frame, text="Return Selected Book", command=self.return_book)
        return_button.pack(side=tk.BOTTOM, pady=5)


        columns = ("ID", "Book", "Member", "Issue Date", "Due Date")
        self.loans_tree = ttk.Treeview(loans_frame, columns=columns, show="headings")
        self.loans_tree.pack(fill="both", expand=True)

        for col in columns:
            self.loans_tree.heading(col, text=col)
            self.loans_tree.column(col, width=100)

        # Search Section
        search_frame = tk.LabelFrame(self.frame, text="Search Active Loans", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(10, 20))

        tk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(search_frame, text="Search", command=self.search_loans).grid(row=0, column=2, padx=5, pady=5)

        # Load initial data and sorting/filtering options
        tk.Label(search_frame, text="Sort By:").grid(row=1, column=0, padx=5, pady=5)
        self.sort_var = tk.StringVar(value="Book Title")
        self.sort_dropdown = ttk.Combobox(search_frame, textvariable=self.sort_var, state="readonly", 
                                           values=["Book Title", "Member Name", "Issue Date", "Due Date"])
        self.sort_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.sort_dropdown.bind("<<ComboboxSelected>>", lambda event: self.sort_loans())



        self.load_data()

    def fetch_lending_records(self):
        """Fetch and display all lending records."""
        try:
            logger.debug("Fetching lending records")
            lending_records = self.fetch_data("http://localhost:5000/api/lending/records")
            logger.debug(f"Lending Records Response: {json.dumps(lending_records, indent=2)}")

            # Clear existing items in the loans table
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)

            if lending_records and isinstance(lending_records, list):
                for record in lending_records:
                    self.loans_tree.insert("", "end", values=(
                        record["LendID"],       # id
                        record["BookTitle"],    # book_title
                        record["MemberName"],    # member_name
                        record["IssueDate"],     # issue_date
                        record["DueDate"],       # due_date
                        record["ReturnDate"]     # return_date
                    ))
        except Exception as e:
            logger.error(f"Failed to fetch lending records: {str(e)}")
            messagebox.showerror("Error", f"Failed to fetch lending records: {str(e)}")

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
                self.member_dropdown['values'] = [f"{m[1]} (ID: {m[0]})" for m in members_response]
            elif members_response and 'data' in members_response:
                self.member_dropdown['values'] = [f"{m[1]} (ID: {m[0]})" for m in members_response['data']]

            # Load active loans
            self.refresh_loans()


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
        """Refresh the active loans table.""" 
        try:
            logger.debug("Refreshing active loans data")
            # Clear existing items
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)

            # Fetch active loans
            loans = self.fetch_data("http://localhost:5000/api/lending/active")
            logger.debug(f"Active Loans Response: {json.dumps(loans, indent=2)}")

            if loans and isinstance(loans, list):
                for loan in loans:
                    # Convert tuple to dictionary
                    loan_dict = {
                        "LendID": loan[0],
                        "BookTitle": loan[1],
                        "MemberName": loan[2],
                        "IssueDate": loan[3],
                        "DueDate": loan[4]
                    }
                    # Ensure correct data order in UI
                    self.loans_tree.insert("", "end", values=(
                        loan_dict["LendID"],       # id
                        loan_dict["BookTitle"],    # book_title
                        loan_dict["MemberName"],   # member_name
                        loan_dict["IssueDate"],    # issue_date
                        loan_dict["DueDate"]       # due_date
                    ))


        except Exception as e:
            logger.error(f"Failed to refresh active loans: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh active loans: {str(e)}")

    def refresh_returned_loans(self):
        """Refresh the returned loans table."""
        try:
            logger.debug("Refreshing returned loans data")
            # Clear existing items (if applicable)
            # Fetch returned loans
            returned_loans = self.fetch_data("http://localhost:5000/api/lending/returned")
            logger.debug(f"Returned Loans Response: {json.dumps(returned_loans, indent=2)}")

            # Assuming there is a Treeview for returned loans, similar to active loans
            # Here you would update the UI with the returned loans data
            # For example:
            # for loan in returned_loans:
            #     self.returned_loans_tree.insert("", "end", values=(loan["LendID"], loan["BookTitle"], loan["MemberName"], loan["ReturnDate"]))

        except Exception as e:
            logger.error(f"Failed to refresh returned loans: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh returned loans: {str(e)}")

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
                self.refresh_returned_loans()
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
            selected_item = self.loans_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a loan to return")
                return

            loan_id = self.loans_tree.item(selected_item)['values'][0]
            response = requests.put(f"http://localhost:5000/api/lending/id{loan_id}")

            if response.status_code == 200:
                messagebox.showinfo("Success", "Book returned successfully!")
                self.refresh_loans()
            else:
                error_msg = response.json().get("message", "Failed to return book")
                logger.error(f"Return failed: {error_msg}")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            logger.error(f"Return error: {str(e)}")
            messagebox.showerror("Error", f"Failed to return book: {str(e)}")

    def sort_loans(self):
        """Sort the active loans based on the selected criteria."""
        sort_by = self.sort_var.get()
        loans = []
        for item in self.loans_tree.get_children():
            loans.append(self.loans_tree.item(item)['values'])
        
        if sort_by == "Book Title":
            loans.sort(key=lambda x: x[1])  # Sort by Book Title
        elif sort_by == "Member Name":
            loans.sort(key=lambda x: x[2])  # Sort by Member Name
        elif sort_by == "Issue Date":
            loans.sort(key=lambda x: x[3])  # Sort by Issue Date
        elif sort_by == "Due Date":
            loans.sort(key=lambda x: x[4])  # Sort by Due Date

        # Clear the tree and reinsert sorted loans
        for item in self.loans_tree.get_children():
            self.loans_tree.delete(item)
        for loan in loans:
            self.loans_tree.insert("", "end", values=loan)

    def search_loans(self):

        """Handle searching loans"""
        search_term = self.search_entry.get().lower()

        for item in self.loans_tree.get_children():
            values = self.loans_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.loans_tree.selection_set(item)
            else:
                self.loans_tree.selection_remove(item)
