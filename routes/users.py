import os 
from flask import Blueprint, request, jsonify
from config.database import User, SessionLocal , UserRole , Service

users_routes = Blueprint('users_routes', __name__)

# Get all users
@users_routes.route('/users', methods=['GET'])
def get_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return jsonify([
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            } for user in users
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get a user by id
@users_routes.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):  
    session = SessionLocal()
    try:

        user = session.query(User).filter(User.id == user_id).first()  
        if user:
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            }), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@users_routes.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    session = SessionLocal()
    try:
        # Check if the authenticated user is trying to update their own information
        if request.user.get('id') != user_id:
            return jsonify({'error': 'You are not authorized to update this user.'}), 403
        
        updated_data = request.get_json()

        # Check for username uniqueness
        if 'username' in updated_data:
            existing_user = session.query(User).filter(
                User.username == updated_data['username'], User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400

        # Check for email uniqueness
        if 'email' in updated_data:
            existing_user = session.query(User).filter(
                User.email == updated_data['email'], User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400

        # Update user information
        session.query(User).filter(User.id == user_id).update(updated_data)
        session.commit()

        # Retrieve the updated user
        user = session.query(User).filter(User.id == user_id).first()

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'role': user.role.value,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Delete a user by id
@users_routes.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        services = session.query(Service).filter_by(owner_id=user_id).all()
        for service in services:
            session.delete(service)

        user_roles = session.query(UserRole).filter_by(user_id=user_id).all()
        for role in user_roles:
            session.delete(role)

        session.delete(user)
        session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()
