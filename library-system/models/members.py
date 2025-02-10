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
    connection = mysql.connection  # Use the existing database connection
    cursor = connection.cursor()

    query = """
    SELECT 
        Books.Title AS BookTitle, 
        Lending.IssueDate, 
        Lending.DueDate, 
        Lending.ReturnDate 
    FROM Lending 
    JOIN Books ON Lending.BookID = Books.BookID 
    WHERE Lending.MemberID = %s
    ORDER BY Lending.IssueDate DESC;
    """

    cursor.execute(query, (member_id,))
    
    # Fetch column names
    columns = [col[0] for col in cursor.description]
    
    # Convert query result into a list of dictionaries
    history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()

    return history