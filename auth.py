import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config
from models import User

def generate_jwt_token(user):
    """Generate JWT token for a user"""
    payload = {
        'user_id': str(user['_id']),
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token

def decode_jwt_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and 'Bearer ' in auth_header:
            token = auth_header.split('Bearer ')[1]
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Authorization token required.'}), 401
        
        # Decode token
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token.'}), 403
        
        # Get user from database
        user = User.find_by_id(payload['user_id'])
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404
        
        # Pass user to the route
        return f(current_user=user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and 'Bearer ' in auth_header:
            token = auth_header.split('Bearer ')[1]
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Authorization token required.'}), 401
        
        # Decode token
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token.'}), 403
        
        # Check admin role
        if payload.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'Admin access required.'}), 403
        
        # Get user from database
        user = User.find_by_id(payload['user_id'])
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404
        
        # Pass user to the route
        return f(current_user=user, *args, **kwargs)
    
    return decorated
