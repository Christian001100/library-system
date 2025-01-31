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