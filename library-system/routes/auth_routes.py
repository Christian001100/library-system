from flask import Blueprint, request, jsonify, session
from models.librarians import create_librarian, authenticate_librarian

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/signup', methods=['POST'])
def signup():
    data = request.json
    create_librarian(data['username'], data['password'])
    return jsonify({"message": "Signup successful!"})

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    if authenticate_librarian(data['username'], data['password']):
        session['librarian'] = data['username']
        return jsonify({"message": "Login successful!"})
    return jsonify({"error": "Invalid credentials"}), 401

@auth_routes.route('/logout', methods=['POST'])
def logout():
    session.pop('librarian', None)
    return jsonify({"message": "Logout successful!"})
