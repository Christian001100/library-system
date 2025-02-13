from flask import Blueprint, jsonify, request
from models.books import add_book, get_books, advanced_search_books

book_routes = Blueprint('books', __name__)

@book_routes.route('/books/all', methods=['GET'])
def fetch_books():
    books = get_books()
    return jsonify(books)

@book_routes.route('/books/create', methods=['POST'])
def create_book():
    data = request.json
    add_book(data['title'], data['author'], data['genre'], data['isbn'], data['copies'])
    return jsonify({"message": "Book added successfully!"})

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
            "BookID": book[0],
            "Title": book[1],
            "Author": book[2],
            "Genre": book[3],
            "ISBN": book[4],
            "Copies": book[5],
            "Popularity": book[6]
        })

    return jsonify(book_list)

