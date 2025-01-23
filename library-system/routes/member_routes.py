from flask import Blueprint, jsonify, request
from models.members import add_member, get_members, get_member

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
