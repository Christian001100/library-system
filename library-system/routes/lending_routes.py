from flask import Blueprint, jsonify, request
from db_config import mysql

from models.lending import lend_book, return_book, get_lending_records, get_overdue_books, get_active_loans, get_returned_loans

lending_routes = Blueprint('lending', __name__)

@lending_routes.route('/lending/active', methods=['GET'])
def fetch_active_loans():
    """Fetch and return all active (unreturned) lending records."""
    try:
        active_loans = get_active_loans()
        return jsonify(active_loans)
    except Exception as e:
        return jsonify({"message": "Error fetching active loans.", "error": str(e)}), 500

@lending_routes.route('/lending/returned', methods=['GET'])
def fetch_returned_loans():
    """Fetch and return all returned lending records."""
    try:
        returned_loans = get_returned_loans()
        return jsonify(returned_loans)
    except Exception as e:
        return jsonify({"message": "Error fetching returned loans.", "error": str(e)}), 500

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

        # Check if the book is available
        cursor.execute("SELECT copies FROM Books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if not book or book[0] <= 0:
            return jsonify({"message": "Book is not available."}), 400

        # Insert lending record with CURDATE() for due date
        query = """
            INSERT INTO Lending (BookID, MemberID, DueDate)
            VALUES (%s, %s, CURDATE())
        """
        cursor.execute(query, (book_id, member_id))
        
        # Decrease the number of available copies
        cursor.execute("UPDATE Books SET copies = copies - 1 WHERE id = %s", (book_id,))
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
        
        # Increase the number of available copies
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Books SET copies = copies + 1 WHERE id = (SELECT BookID FROM Lending WHERE id = %s)", (lend_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Book returned successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Error returning book.", "error": str(e)}), 500

# Route to fetch all lending records
@lending_routes.route('/lending/records', methods=['GET'])
def fetch_lending_records():
    """Fetch and return all lending records."""
    try:
        lending_records = get_lending_records()
        return jsonify(lending_records)
    except Exception as e:
        return jsonify({"message": "Error fetching lending records.", "error": str(e)}), 500

@lending_routes.route('/lending/overdue', methods=['GET'])
def fetch_overdue_books():
    """Fetch all overdue lending records."""
    try:
        overdue_books = get_overdue_books()
        return jsonify(overdue_books)
    except Exception as e:
        return jsonify({"message": "Error fetching overdue books.", "error": str(e)}), 500
