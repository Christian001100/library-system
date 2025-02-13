from flask import Blueprint, jsonify, request
from db_config import mysql

from models.lending import lend_book, return_book, get_lending_records, get_overdue_books

lending_routes = Blueprint('lending', __name__)

# Route to fetch all lending records
@lending_routes.route('/lending/all', methods=['GET'])
def fetch_lending_records():
    """Fetch all lending records."""
    try:
        records = get_lending_records()
        return jsonify(records)
    except Exception as e:
        return jsonify({"message": "Error fetching lending records.", "error": str(e)}), 500

# Route to lend a book to a member
@lending_routes.route('/lending/create', methods=['POST'])
def create_lending():
    """Lend a book to a member, setting the due date to today's date (CURDATE)."""
    data = request.json
    book_id = data.get('book_id')
    member_id = data.get('member_id')

    if not book_id or not member_id:
        return jsonify({"message": "Book ID and Member ID are required."}), 400

    try:
        # Check if the MemberID exists in the Members table
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT MemberID FROM Members WHERE MemberID = %s", (member_id,))
        member = cursor.fetchone()

        if not member:
            return jsonify({"message": "Member not found."}), 404

        # Insert lending record with CURDATE() for due date
        query = """
            INSERT INTO Lending (BookID, MemberID, DueDate)
            VALUES (%s, %s, CURDATE())
        """
        cursor.execute(query, (book_id, member_id))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Book lent successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Error lending book.", "error": str(e)}), 500


# Route to return a book (mark as returned)
@lending_routes.route('/lending/id<int:lend_id>', methods=['PUT'])
def return_lending(lend_id):
    """Mark a book as returned."""
    if not lend_id:
        return jsonify({"message": "Lend ID is required."}), 400

    try:
        return_book(lend_id)
        return jsonify({"message": "Book returned successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Error returning book.", "error": str(e)}), 500

# Route to fetch all overdue books
@lending_routes.route('/lending/overdue', methods=['GET'])
def fetch_overdue_books():
    """Fetch all overdue lending records."""
    try:
        overdue_books = get_overdue_books()
        return jsonify(overdue_books)
    except Exception as e:
        return jsonify({"message": "Error fetching overdue books.", "error": str(e)}), 500
