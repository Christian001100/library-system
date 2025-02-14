from flask import Blueprint, jsonify, request
from models.books import add_book, get_books, advanced_search_books, update_book, delete_book



book_routes = Blueprint('books', __name__)

@book_routes.route('/books/all', methods=['GET'])
def fetch_books():
    books = get_books()
    return jsonify(books)

@book_routes.route('/books/create', methods=['POST'])
def create_book():
    data = request.json
    # Use get() with default values for optional fields
    add_book(
        data.get('title'),
        data.get('author'),
        data.get('genre', 'Unknown'),
        data.get('isbn'),
        data.get('copies', 1)
    )
    return jsonify({"message": "Book added successfully!"}), 201


@book_routes.route('/books/search', methods=['GET'])
def search_books():
    """Search books with advanced filtering options."""
    title = request.args.get('title')
    author = request.args.get('author')
    isbn = request.args.get('isbn')
    genre = request.args.get('genre')
    available_only = request.args.get('available_only', type=bool, default=False)
    sort_by_popularity = request.args.get('sort_by_popularity', type=bool, default=False)

    books = advanced_search_books(title, author, isbn, genre, available_only, sort_by_popularity)

    # Formatting the books to a JSON-friendly structure
    book_list = []
    for book in books:
        book_list.append({
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "genre": book[3],
            "isbn": book[4],
            "copies": book[5],
            "availability": "Available" if book[5] > 0 else "Borrowed",
            "popularity": book[6]
        })


    return jsonify(book_list)

@book_routes.route('/books/update/<int:book_id>', methods=['PUT'])
def update_book_route(book_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        success = update_book(
            book_id,
            title=data.get('title'),
            author=data.get('author'),
            genre=data.get('genre'),
            isbn=data.get('isbn'),
            copies=data.get('copies')
        )
        if success:
            return jsonify({"message": "Book updated successfully"}), 200
        return jsonify({"error": "No fields to update"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_routes.route('/books/delete/<int:book_id>', methods=['DELETE'])
def delete_book_route(book_id):
    """Delete a book by its ID"""
    try:
        success = delete_book(book_id)
        if success:
            return jsonify({"message": "Book deleted successfully"}), 200
        return jsonify({"error": "Failed to delete book"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
