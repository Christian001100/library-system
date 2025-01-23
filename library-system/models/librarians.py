import bcrypt
from db_config import mysql

def create_librarian(username, password):
    """Add a new librarian with a hashed password."""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Librarians (Username, PasswordHash) VALUES (%s, %s)"
    cursor.execute(query, (username, password_hash))
    mysql.connection.commit()
    cursor.close()

def authenticate_librarian(username, password):
    """Check if a librarian's credentials are valid."""
    cursor = mysql.connection.cursor()
    query = "SELECT PasswordHash FROM Librarians WHERE Username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))
    return False

