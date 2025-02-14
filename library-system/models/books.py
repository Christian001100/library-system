from db_config import mysql
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_book(title, author, genre, isbn, copies):
    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Books (Title, Author, Genre, ISBN, Copies) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (title, author, genre, isbn, copies))
        mysql.connection.commit()
        logger.info(f"Successfully added book: {title} by {author}")
        return True
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error adding book: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()


def update_book(book_id, title=None, author=None, genre=None, isbn=None, copies=None):
    """Update book information in the database"""
    try:
        cursor = mysql.connection.cursor()
        
        # Build the update query dynamically based on provided fields
        updates = []
        params = []
        
        if title is not None:
            updates.append("Title = %s")
            params.append(title)
        if author is not None:
            updates.append("Author = %s")
            params.append(author)
        if genre is not None:
            updates.append("Genre = %s")
            params.append(genre)
        if isbn is not None:
            updates.append("ISBN = %s")
            params.append(isbn)
        if copies is not None:
            updates.append("Copies = %s")
            params.append(copies)
            
        if not updates:
            logger.warning("No fields provided for update")
            return False
            
        query = f"UPDATE Books SET {', '.join(updates)} WHERE BookID = %s"
        params.append(book_id)
        
        cursor.execute(query, tuple(params))
        mysql.connection.commit()
        logger.info(f"Successfully updated book ID {book_id}")
        return True
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error updating book ID {book_id}: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()



def get_books():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Books"
    cursor.execute(query)
    books = cursor.fetchall()
    cursor.close()
    
    # Convert tuples to dictionaries
    book_list = []
    for book in books:
        book_id, title, author, genre, isbn, copies = book
        book_list.append({
            "id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "isbn": isbn,
            "copies": copies,
            "availability": "Available" if copies > 0 else "Borrowed"
        })
    return book_list

def delete_book(book_id):
    """Delete a book from the database by its ID"""
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Books WHERE BookID = %s"
        cursor.execute(query, (book_id,))
        mysql.connection.commit()
        logger.info(f"Successfully deleted book ID {book_id}")
        return True
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error deleting book ID {book_id}: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()


def advanced_search_books(title=None, author=None, isbn=None, genre=None, available_only=False, sort_by_popularity=False):
    """
    Search books by title, author, ISBN, genre and apply filters for availability and popularity.

    :param title: Title of the book (optional).
    :param author: Author of the book (optional).
    :param isbn: ISBN of the book (optional).
    :param genre: Genre of the book (optional).
    :param available_only: Boolean flag to filter only available books.
    :param sort_by_popularity: Boolean flag to sort books by popularity (borrowed count).
    :return: List of dictionaries containing book information.
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
