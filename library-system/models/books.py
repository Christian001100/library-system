from db_config import mysql

def add_book(title, author, genre, isbn, copies):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Books (Title, Author, Genre, ISBN, Copies) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (title, author, genre, isbn, copies))
    mysql.connection.commit()
    cursor.close()

def get_books():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Books"
    cursor.execute(query)
    books = cursor.fetchall()
    cursor.close()
    return books
