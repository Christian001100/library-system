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
    for i, book in enumerate(books):
        book_id, title, author, genre, isbn, copies = book
        if copies > 0:
            status = "Available"
        else:
            status = "Borrowed"
        
        # You can also implement dynamic status for Reserved books if needed
        books[i] = list(book)  # Convert tuple to list to modify
        books[i].append(status) 
def advanced_search_books(title=None, author=None, isbn=None, genre=None, available_only=False, sort_by_popularity=False):
    """
    Search books by title, author, ISBN, genre and apply filters for availability and popularity.
    :param title: Title of the book (optional).
    :param author: Author of the book (optional).
    :param isbn: ISBN of the book (optional).
    :param genre: Genre of the book (optional).
    :param available_only: Boolean flag to filter only available books.
    :param sort_by_popularity: Boolean flag to sort books by popularity (borrowed count).
    :return: List of books matching the search criteria.
    """
    cursor = mysql.connection.cursor()
    query = """
        SELECT 
            Books.BookID, Books.Title, Books.Author, Books.Genre, Books.ISBN, Books.Copies, COUNT(Lending.LendID) AS Popularity
        FROM Books
        LEFT JOIN Lending ON Books.BookID = Lending.BookID AND Lending.ReturnDate IS NULL
        WHERE 1=1
    """

    params = []

    if title:
        query += " AND Books.Title LIKE %s"
        params.append(f"%{title}%")

    if author:
        query += " AND Books.Author LIKE %s"
        params.append(f"%{author}%")

    if isbn:
        query += " AND Books.ISBN LIKE %s"
        params.append(f"%{isbn}%")

    if genre:
        query += " AND Books.Genre LIKE %s"
        params.append(f"%{genre}%")

    query += " GROUP BY Books.BookID"

    if available_only:
        query += " HAVING (Books.Copies - COUNT(Lending.LendID)) > 0"

    if sort_by_popularity:
        query += " ORDER BY Popularity DESC"

    cursor.execute(query, tuple(params))
    books = cursor.fetchall()
    cursor.close()
    
    return books

    
