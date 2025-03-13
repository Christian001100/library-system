from db_config import mysql
from datetime import datetime, timedelta, date
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Lend Book Function (borrow book logic)
def lend_book(book_id, member_id, is_class_monitor=False):
    """Insert a new lending record into the database and check availability."""
    cursor = mysql.connection.cursor()
    
    try:
        # Check if there are available copies
        query = "SELECT Copies FROM Books WHERE BookID = %s"
        cursor.execute(query, (book_id,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:  # There are available copies
            # Determine borrowing limit based on whether it's a student or class monitor
            limit = 5 if not is_class_monitor else 10  # 5 for students, 10 for class monitors
            
            # Check if the borrower has exceeded their limit
            query = "SELECT COUNT(*) FROM Lending WHERE MemberID = %s AND ReturnDate IS NULL"
            cursor.execute(query, (member_id,))
            borrowed_count = cursor.fetchone()[0]
            
            if borrowed_count < limit:
                # Calculate due date (14 days from today)
                due_date = datetime.now() + timedelta(days=14)
                
                # Update the number of available copies
                query = "UPDATE Books SET Copies = Copies - 1 WHERE BookID = %s"
                cursor.execute(query, (book_id,))
                
                # Insert lending record into Lending table
                query = """
                    INSERT INTO Lending (BookID, MemberID, DueDate)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (book_id, member_id, due_date))
                
                # Commit changes
                mysql.connection.commit()
                logger.info(f"Book lent successfully: BookID {book_id}, MemberID {member_id}")
                return {"message": "Book lent successfully!"}
            else:
                logger.warning(f"Limit exceeded for MemberID {member_id}. Can only borrow {limit} books.")
                return {"message": f"Limit exceeded. You can only borrow {limit} books."}
        else:
            logger.warning(f"No available copies for BookID {book_id}.")
            return {"message": "No available copies."}
    except Exception as e:
        logger.error(f"Error lending book: {str(e)}")
        return {"message": "Error lending book."}
    finally:
        cursor.close()

# Return Book Function (return book logic)
def return_book(lend_id):
    """Update the lending record to set the ReturnDate and handle overdue fines."""
    cursor = mysql.connection.cursor()
    
    try:
        # Check if the lending record exists and if it was borrowed
        query = "SELECT BookID, DueDate FROM Lending WHERE LendID = %s AND ReturnDate IS NULL"
        cursor.execute(query, (lend_id,))
        result = cursor.fetchone()
        
        if result:
            book_id, due_date = result
            return_date = datetime.now()
            
            # Ensure both dates are datetime objects
            if isinstance(due_date, date):
                due_date = datetime.combine(due_date, datetime.min.time())
            if isinstance(return_date, date):
                return_date = datetime.combine(return_date, datetime.min.time())

            # Calculate overdue days safely
            overdue_days = max((return_date - due_date).days, 0)

            # Calculate fine for late return
            fine = overdue_days * 1  # $1 fine for each day overdue
            
            # Update the Lending table with the return date
            query = "UPDATE Lending SET ReturnDate = %s WHERE LendID = %s"
            cursor.execute(query, (return_date, lend_id))
            
            # Update the Books table (increase available copies)
            query = "UPDATE Books SET Copies = Copies + 1 WHERE BookID = %s"
            cursor.execute(query, (book_id,))
            
            # Commit changes
            mysql.connection.commit()
            logger.info(f"Book returned successfully: LendID {lend_id}, Fine: {fine}")
            return {"message": "Book returned successfully!", "fine": fine}
        else:
            logger.warning(f"Lending record does not exist for LendID {lend_id}.")
            return {"message": "This lending record does not exist."}
    except Exception as e:
        logger.error(f"Error returning book: {str(e)}")
        return {"message": "Error returning book."}
    finally:
        cursor.close()

# Fetch Lending Records (fetch details of lent books, including members and due dates)
def get_active_loans():
    """Fetch all active lending records (not yet returned)."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT 
                Lending.LendID,
                Books.Title AS BookTitle,
                Members.Name AS MemberName,
                Lending.IssueDate,
                Lending.DueDate
            FROM Lending
            JOIN Books ON Lending.BookID = Books.BookID
            JOIN Members ON Lending.MemberID = Members.MemberID
            WHERE Lending.ReturnDate IS NULL
        """
        cursor.execute(query)
        active_loans = cursor.fetchall()
        return active_loans
    except Exception as e:
        logger.error(f"Error fetching active loans: {str(e)}")
        return []
    finally:
        cursor.close()

def get_returned_loans():
    """Fetch all returned lending records."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT 
                Lending.LendID,
                Books.Title AS BookTitle,
                Members.Name AS MemberName,
                Lending.IssueDate,
                Lending.DueDate,
                Lending.ReturnDate
            FROM Lending
            JOIN Books ON Lending.BookID = Books.BookID
            JOIN Members ON Lending.MemberID = Members.MemberID
            WHERE Lending.ReturnDate IS NOT NULL
        """
        cursor.execute(query)
        returned_loans = cursor.fetchall()
        return returned_loans
    except Exception as e:
        logger.error(f"Error fetching returned loans: {str(e)}")
        return []
    finally:
        cursor.close()

# Get Overdue Books (fetch lending records where books are overdue)
def get_overdue_books():
    """Fetch all overdue lending records where books are not returned."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT 
                Lending.LendID,
                Books.Title AS BookTitle,
                Members.Name AS MemberName,
                Lending.IssueDate,
                Lending.DueDate
            FROM Lending
            JOIN Books ON Lending.BookID = Books.BookID
            JOIN Members ON Lending.MemberID = Members.MemberID
            WHERE Lending.DueDate < CURDATE() AND Lending.ReturnDate IS NULL
        """
        cursor.execute(query)
        overdue_books = cursor.fetchall()
        return overdue_books
    except Exception as e:
        logger.error(f"Error fetching overdue books: {str(e)}")
        return []
    finally:
        cursor.close()

# Get Lending Records (fetch all lending records)
def get_lending_records():
    """Fetch all lending records including book and member details."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT 
                Lending.LendID,
                Books.Title AS BookTitle,
                Members.Name AS MemberName,
                Lending.IssueDate,
                Lending.DueDate,
                Lending.ReturnDate
            FROM Lending
            JOIN Books ON Lending.BookID = Books.BookID
            JOIN Members ON Lending.MemberID = Members.MemberID
        """
        cursor.execute(query)
        lending_records = cursor.fetchall()
        return lending_records
    except Exception as e:
        logger.error(f"Error fetching lending records: {str(e)}")
        return []
    finally:
        cursor.close()

def get_borrowing_history(member_id):
    """Fetch borrowing history for a specific member."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT LendID, BookID, IssueDate, DueDate, ReturnDate
            FROM Lending
            WHERE MemberID = %s
        """
        cursor.execute(query, (member_id,))
        records = cursor.fetchall()

        # Convert records to a list of dictionaries
        borrowing_history = []
        for record in records:
            borrowing_history.append({
                "LendID": record[0],
                "BookID": record[1],
                "IssueDate": record[2].strftime("%Y-%m-%d") if record[2] else None,
                "DueDate": record[3].strftime("%Y-%m-%d") if record[3] else None,
                "ReturnDate": record[4].strftime("%Y-%m-%d") if record[4] else None
            })
        return borrowing_history
    except Exception as e:
        logger.error(f"Error fetching borrowing history for MemberID {member_id}: {str(e)}")
        return []
    finally:
        cursor.close()

def get_book_borrowing_history(book_id):
    """Fetch borrowing history for a specific book."""
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT 
                Lending.LendID,
                Members.Name AS MemberName,
                Lending.IssueDate,
                Lending.DueDate,
                Lending.ReturnDate
            FROM Lending
            JOIN Members ON Lending.MemberID = Members.MemberID
            WHERE BookID = %s
            ORDER BY Lending.IssueDate DESC
        """
        cursor.execute(query, (book_id,))
        records = cursor.fetchall()

        # Convert records to a list of dictionaries
        borrowing_history = []
        for record in records:
            borrowing_history.append({
                "LendID": record[0],
                "MemberName": record[1],
                "IssueDate": record[2].strftime("%Y-%m-%d") if record[2] else None,
                "DueDate": record[3].strftime("%Y-%m-%d") if record[3] else None,
                "ReturnDate": record[4].strftime("%Y-%m-%d") if record[4] else None
            })
        return borrowing_history
    except Exception as e:
        logger.error(f"Error fetching borrowing history for BookID {book_id}: {str(e)}")
        return []
    finally:
        cursor.close()

def lend_book(member_id, barcode):
    # Check if barcode exists and is available
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""SELECT BookID FROM Barcodes WHERE Barcode = %s AND IsBorrowed = FALSE""", (barcode,))
        book = cursor.fetchone()

        if not book:
            return "Book not available or already lent."

        # Record lending and update barcode status
        book_id = book['BookID']
        cursor.execute("""INSERT INTO Lending (BookID, MemberID, IssueDate, DueDate) VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY))""", (book_id, member_id))

        cursor.execute("""UPDATE Barcodes SET IsBorrowed = TRUE WHERE Barcode = %s""", (barcode,))
        mysql.connection.commit()
        return "Book successfully lent."
    except Exception as e:
        logger.error(f"Error lending book with barcode {barcode}: {str(e)}")
        return "Error lending book."
    finally:
        cursor.close()

def return_book(barcode):
    # Verify if barcode exists
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""SELECT BookID FROM Barcodes WHERE Barcode = %s AND IsBorrowed = TRUE""", (barcode,))
        book = cursor.fetchone()

        if not book:
            return "Invalid barcode or book not borrowed."

        # Update return status
        book_id = book['BookID']
        cursor.execute("""UPDATE Lending SET ReturnDate = CURDATE() WHERE BookID = %s AND ReturnDate IS NULL""", (book_id,))
        cursor.execute("""UPDATE Barcodes SET IsBorrowed = FALSE WHERE Barcode = %s""", (barcode,))
        mysql.connection.commit()
        return "Book returned successfully."
    except Exception as e:
        logger.error(f"Error returning book with barcode {barcode}: {str(e)}")
        return "Error returning book."
    finally:
        cursor.close()
