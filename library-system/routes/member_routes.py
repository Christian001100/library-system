from flask import Blueprint, jsonify, request
from models.members import add_member, get_members, get_member, update_member, delete_member, get_borrowing_history

member_routes = Blueprint('members', __name__)

@member_routes.route('/members/all', methods=['GET'])
def fetch_members():
    members = get_members()
    return jsonify(members)

@member_routes.route('/members/id/<int:member_id>', methods=['GET'])
def fetch_member(member_id):
    member = get_member(member_id)
    return jsonify(member)

@member_routes.route('/members/create', methods=['POST'])
def create_member():
    data = request.json
    add_member(data['name'], data.get('contact'))
    return jsonify({"message": "Member added successfully!"})

@member_routes.route('/members/update/<int:member_id>', methods=['PUT'])
def update_member_route(member_id):
    data = request.json
    success = update_member(member_id, data.get('name'), data.get('contact'))
    if success:
        return jsonify({"message": "Member updated successfully!"})
    else:
        return jsonify({"error": "Member not found or update failed"}), 404

@member_routes.route('/members/delete/<int:member_id>', methods=['DELETE'])
def delete_member_route(member_id):
    success = delete_member(member_id)
    if success:
        return jsonify({"message": "Member deleted successfully!"})
    else:
        return jsonify({"error": "Member not found or delete failed"}), 404
    
@member_routes.route('/members/<int:member_id>/borrowing-history', methods=['GET'])
def fetch_borrowing_history(member_id):
    """
    Fetch borrowing history for a specific member.
    :param member_id: ID of the member.
    :return: JSON list of borrowing records.
    """
    borrowing_history = get_borrowing_history(member_id)
    if borrowing_history:
        return jsonify(borrowing_history)
    else:
        return jsonify({"error": "No borrowing history found"}), 404
