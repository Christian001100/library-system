from db_config import mysql
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_book(title, author, genre, isbn, copies):
    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Books (Title, Author, Genre, ISBN, Copies) VALUES (%s, %s, %s, %s, %s)"
        logger.info(f"Executing query: {query} with parameters: {(title, author, genre, isbn, copies)}")
        cursor.execute(query, (title, author, genre, isbn, copies))

        mysql.connection.commit()
        logger.info(f"Successfully added book: {title} by {author} with ISBN: {isbn} and Copies: {copies}")
        return True
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error adding book: {str(e)} - Check if the ISBN is unique and all fields are valid.")
        return False
    finally:
        cursor.close()
def get_book_by_id(book_id):
    """Fetch a single book by its ID"""
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Books WHERE BookID = %s"
        cursor.execute(query, (book_id,))
        book = cursor.fetchone()
        cursor.close()
        
        if book:
            return book  # Return the book details as a tuple
        return None
    except Exception as e:
        logger.error(f"Error fetching book by ID {book_id}: {str(e)}")
        return None

def update_book(book_id, title=None, author=None, genre=None, isbn=None, copies=None):
    """Update book information in the database"""
    # Fetch existing book details to compare
    existing_book = get_book_by_id(book_id)
    if existing_book:
        existing_title, existing_author, existing_genre, existing_isbn, existing_copies, *_ = existing_book

        # Check if new values are different from existing values
        if (title == existing_title and author == existing_author and 
            genre == existing_genre and isbn == existing_isbn and 
            copies == existing_copies):
            logger.info(f"No changes detected for book ID {book_id}. Update skipped.")
            return True

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

        # Log the parameters being used for the update
        logger.info(f"Updating book ID {book_id} with parameters: {params}")

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

def get_book_by_isbn(isbn):
    """Fetch a single book by its ISBN"""
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Books WHERE ISBN = %s"
        cursor.execute(query, (isbn,))
        book = cursor.fetchone()
        cursor.close()
        
        if book:
            return book  # Return the book details as a tuple
        return None
    except Exception as e:
        logger.error(f"Error fetching book by ISBN {isbn}: {str(e)}")
        return None


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

def add_book_with_barcodes(title, author, genre, isbn, copies):
    cursor = mysql.connection.cursor()
    try:
        # Insert the book
        query = "INSERT INTO Books (Title, Author, Genre, ISBN, Copies) VALUES (%s, %s, %s, %s, %s)"
        logger.info(f"Executing query: {query} with parameters: {(title, author, genre, isbn, copies)}")
        cursor.execute(query, (title, author, genre, isbn, copies))
        book_id = cursor.lastrowid
        logger.info(f"Inserted book with ID: {book_id}")

        # Generate unique barcodes
        for i in range(1, copies + 1):
            barcode = f"#_{title.replace(' ', '')}_{book_id}_{i}"  # Ensure unique barcode
            logger.info(f"Generated barcode: {barcode} for book ID: {book_id}")
            
            # Insert barcode into the barcodes table
            query = "INSERT INTO barcodes (BookID, Barcode) VALUES (%s, %s)"
            cursor.execute(query, (book_id, barcode))
            logger.info(f"Inserted barcode: {barcode} for book ID: {book_id}")

        mysql.connection.commit()
        logger.info(f"Successfully added {copies} copies of '{title}' with barcodes for ISBN: {isbn}.")
        return True  # Indicate success
    except Exception as e:
        mysql.connection.rollback()  # Rollback the transaction on error
        logger.error(f"Error adding book with barcodes: {str(e)}")
        return False  # Indicate failure
    finally:
        cursor.close()
def get_barcodes_by_book_id(book_id):
    """Fetch barcodes for a specific book by its ID"""
    cursor = mysql.connection.cursor()
    try:
        query = "SELECT Barcode FROM Barcodes WHERE BookID = %s"
        cursor.execute(query, (book_id,))
        barcodes = cursor.fetchall()
        
        # Convert tuples to a list of barcodes
        barcode_list = [barcode[0] for barcode in barcodes]
        return barcode_list
    except Exception as e:
        logger.error(f"Error fetching barcodes for book ID {book_id}: {str(e)}")
        return []
    finally:
        cursor.close()