import os 
from flask import Blueprint, request, jsonify
from config.database import User, SessionLocal

users_routes = Blueprint('users_routes', __name__)

# Get a single user
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
                'address': user.address,
                'user_type': user.user_type.value
            }), 200
        return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()


# Update a user
@users_routes.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = request.get_json()
        username = user_data.get('username')
        email = user_data.get('email')
        phone = user_data.get('phone')
        address = user_data.get('address')

        if not all([username, email, phone, address]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400
        
        existing_user_email = session.query(User).filter(User.email == email).first()
        if existing_user_email and existing_user_email.id != user_id:
            return jsonify({'error': 'Email already taken'}), 400
        
        existing_user_username = session.query(User).filter(User.username == username).first()
        if existing_user_username and existing_user_username.id != user_id:
            return jsonify({'error': 'Username already taken'}), 400
        
        user.username = username
        user.email = email
        user.phone = phone
        user.address = address
        
        session.commit()
        session.refresh(user)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'user_type': user.user_type.value  
        }), 200
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()

# Delete a user
@users_routes.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session.delete(user)
        session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()
