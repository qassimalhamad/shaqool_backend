import os
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from config.database import User, SessionLocal, UserEnum

auth_routes = Blueprint('auth_routes', __name__)

JWT_SECRET = os.getenv('JWT_SECRET')

@auth_routes.route('/auth/sign-up', methods=['POST'])
def signup():
    session = SessionLocal()
    try:
        new_user_data = request.get_json()
        username = new_user_data.get('username')
        email = new_user_data.get('email')
        password = new_user_data.get('password')
        confirm_password = new_user_data.get('confirm_password')
        phone = new_user_data.get('phone')
        address = new_user_data.get('address')
        user_type = new_user_data.get('user_type', 'customer')  

        if not all([username, email, password, confirm_password, phone, address]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match.'}), 400
        
        existing_user_email = session.query(User).filter(User.email == email).first()
        if existing_user_email:
            return jsonify({'error': 'Email already taken.'}), 400
        
        existing_user_username = session.query(User).filter(User.username == username).first()
        if existing_user_username:
            return jsonify({'error': 'Username already taken.'}), 400
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_type_enum = UserEnum[user_type]

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password.decode('utf-8'),
            phone=phone,
            address=address,
            user_type=user_type_enum
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        token_payload = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'phone': new_user.phone,
            'address': new_user.address,
            'user_type': new_user.user_type.value  
        }

        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')

        return jsonify({'token': token, 'payload': token_payload}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@auth_routes.route('/auth/sign-in', methods=['POST'])
def signin():
    session = SessionLocal()
    try:
        user_data = request.get_json()
        email = user_data.get('email')
        password = user_data.get('password')

        if not all([email, password]):
            return jsonify({"error": "Incomplete data. Both email and password are required."}), 400 

        user = session.query(User).filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            token_payload = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'user_type': user.user_type.value 
            }

            token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')

            return jsonify({"token": token}), 200
        
        return jsonify({"error": "Invalid email or password."}), 401

    except Exception as e:
        session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
