from flask import Blueprint, jsonify, request
from models.lending import lend_book, return_book, get_lending_records

lending_routes = Blueprint('lending', __name__)

@lending_routes.route('/lending/all', methods=['GET'])
def fetch_lending_records():
    """Fetch all lending records."""
    records = get_lending_records()
    return jsonify(records)

@lending_routes.route('/lending/create', methods=['POST'])
def create_lending():
    """Lend a book to a member."""
    data = request.json
    lend_book(data['book_id'], data['member_id'], data['due_date'])
    return jsonify({"message": "Book lent successfully!"})

@lending_routes.route('/lending/id<int:lend_id>', methods=['PUT'])
def return_lending(lend_id):
    """Mark a book as returned."""
    return_book(lend_id)
    return jsonify({"message": "Book returned successfully!"})
