from db_config import mysql

def lend_book(book_id, member_id, due_date):
    """Insert a new lending record into the database."""
    cursor = mysql.connection.cursor()
    query = """
        INSERT INTO Lending (BookID, MemberID, DueDate)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (book_id, member_id, due_date))
    mysql.connection.commit()
    cursor.close()

def return_book(lend_id):
    """Update the lending record to set the ReturnDate."""
    cursor = mysql.connection.cursor()
    query = """
        UPDATE Lending
        SET ReturnDate = CURDATE()
        WHERE LendID = %s
    """
    cursor.execute(query, (lend_id,))
    mysql.connection.commit()
    cursor.close()

def get_lending_records():
    """Fetch all lending records, including member and book details."""
    cursor = mysql.connection.cursor()
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
    cursor.close()
    return lending_records


def get_overdue_books():
    """Fetch all overdue lending records where books are not returned."""
    cursor = mysql.connection.cursor()
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
    cursor.close()
    return overdue_books
def get_borrowing_history(member_id):
    """
    Fetch borrowing history for a specific member.
    :param member_id: ID of the member.
    :return: List of borrowing records (each record is a dictionary).
    """
    try:
        # Example: Query the lending table
        # Replace this with your actual database logic
        query = """
            SELECT LendID, BookID, IssueDate, DueDate, ReturnDate
            FROM lending
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
        print(f"Error fetching borrowing history: {e}")
        return None
