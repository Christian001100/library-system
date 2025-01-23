from flask import Blueprint, jsonify, request
from models.books import add_book, get_books

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
