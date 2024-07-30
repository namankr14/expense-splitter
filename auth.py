from flask import request, jsonify
from functools import wraps
import jwt
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from user_management import UserManagement

# TODO: Replace with a secure secret key management solution
SECRET_KEY = 'your_secret_key'

def token_required(f):
    """
    Decorator to ensure a valid token is present in the request header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = UserManagement().get_user(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

class Auth:
    @staticmethod
    def login(email, password):
        """
        Authenticate a user and return a JWT token.
        """
        user = UserManagement().get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY)
            return jsonify({'token': token})
        return jsonify({'message': 'Invalid credentials'}), 401

    @staticmethod
    def register(name, email, mobile, password):
        """
        Register a new user.
        """
        return UserManagement().create_user(name, email, mobile, password)