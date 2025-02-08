from db_config import mysql

def add_member(name, contact):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Members (Name, Contact) VALUES (%s, %s)"
    cursor.execute(query, (name, contact))
    mysql.connection.commit()
    cursor.close()

def get_members():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Members"
    cursor.execute(query)
    members = cursor.fetchall()
    cursor.close()
    return members

def get_member(member_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Members WHERE MemberID = %s"
    cursor.execute(query, (member_id,))
    member = cursor.fetchone()
    cursor.close()
    return member
def update_member(member_id, name, contact):
    cursor = mysql.connection.cursor()
    query = "UPDATE Members SET Name = %s, Contact = %s WHERE MemberID = %s"
    cursor.execute(query, (name, contact, member_id))
    mysql.connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    return rows_affected > 0  # Returns True if update was successful

def delete_member(member_id):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM Members WHERE MemberID = %s"
    cursor.execute(query, (member_id,))
    mysql.connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    return rows_affected > 0 

def get_borrowing_history(member_id):
    """Fetch borrowing history of a member."""
    cursor = mysql.connection.cursor(dictionary=True)  # Return data as dictionary
    query = """
        SELECT Books.Title AS BookTitle, Lendings.IssueDate, Lendings.DueDate, Lendings.ReturnDate
        FROM Lendings
        JOIN Books ON Lendings.BookID = Books.BookID
        WHERE Lendings.MemberID = %s
        ORDER BY Lendings.IssueDate DESC
    """
    cursor.execute(query, (member_id,))
    history = cursor.fetchall()
    cursor.close()
    return history