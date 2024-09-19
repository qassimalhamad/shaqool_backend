import os
import jwt
from flask import request, jsonify
from flask import Response


JWT_SECRET = os.getenv('JWT_SECRET')

def verify_token():

    if request.method.lower() == 'options':
        return Response()
    
    if request.blueprint == 'auth_routes':
        return
    token = request.headers.get('Authorization')
    if token:
        try:
            token = token.split(' ')[1]
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user = decoded 
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': 'Invalid token'}), 401
    else:
        return jsonify({'error': 'Opps something went wrong'}), 401
    