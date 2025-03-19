from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from .models import db, User, Admin, ServiceProfessional, Customer, Service
from .decorators import admin_required
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def create_token(user_id, role):
    # Ensure user_id is converted to string for the subject claim
    payload = {
        'sub': str(user_id),  # Convert user_id to string explicitly
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    print(f"DEBUG - Creating token payload: {payload}")
    print(f"DEBUG - Type of user_id: {type(user_id)}, Value: {user_id}")
    print(f"DEBUG - Type of sub in payload: {type(payload['sub'])}, Value: {payload['sub']}")
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    print(f"DEBUG - Generated token (first 20 chars): {token[:20]}...")
    return token

def verify_token(token):
    try:
        # Enhanced debugging
        print(f"DEBUG - Verifying token (first 20 chars): {token[:20]}...")
        print(f"DEBUG - Token type: {type(token)}")
        
        # Clean up token format
        if isinstance(token, str):
            token = token.strip()
            if token.lower().startswith('bearer '):
                token = token[7:].strip()
        
        print(f"DEBUG - Cleaned token (first 20 chars): {token[:20]}...")
        print(f"DEBUG - SECRET_KEY length: {len(current_app.config['SECRET_KEY'])}")
        
        # Use explicit options to avoid common validation issues
        print(f"DEBUG - About to decode token with JWT")
        payload = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=['HS256'],
            options={"verify_signature": True, "verify_exp": True}
        )
        print(f"DEBUG - Token successfully decoded: {payload}")
        
        # Force subject to be a string
        if 'sub' in payload:
            payload['sub'] = str(payload['sub'])
            print(f"DEBUG - Converted sub to string: {payload['sub']}, type: {type(payload['sub'])}")
            
        return payload
    except jwt.ExpiredSignatureError:
        print("DEBUG - Token expired")
        return {'error': 'Token expired'}
    except jwt.InvalidSignatureError:
        print("DEBUG - Invalid signature")
        print(f"DEBUG - Token (first 20 chars): {token[:20]}...")
        return {'error': 'Invalid signature'}
    except jwt.DecodeError:
        print("DEBUG - Token decode error")
        return {'error': 'Token decode error'}
    except Exception as e:
        print(f"DEBUG - Token verification error: {str(e)}")
        print(f"DEBUG - Exception type: {type(e)}")
        return {'error': f'Token error: {str(e)}'}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_input = data.get('userInput')
    password = data.get('password')
    
    print(f"DEBUG - Login attempt for user: {user_input}")
    
    if not user_input or not password:
        return jsonify({"message": "Username/email and password are required"}), 400
    
    # Check if input is an email or username
    if '@' in user_input:
        user = User.query.filter_by(email=user_input).first()
    else:
        user = User.query.filter_by(username=user_input).first()
    
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    if not user.is_approved:
        return jsonify({"message": "Your account is pending approval"}), 401
    
    # Create token with user info - ensuring user_id is a string
    print(f"DEBUG - Creating token for user ID: {user.id}, type: {type(user.id)}")
    user_id_str = str(user.id)
    print(f"DEBUG - Converted user ID to string: {user_id_str}, type: {type(user_id_str)}")
    
    access_token = create_access_token(
        identity=user_id_str,
        additional_claims={
            "role": user.role, 
            "is_approved": user.is_approved, 
            "is_active": user.is_active,
            "username": user.username
        }
    )
    print(f"DEBUG - Generated access token (first 20 chars): {access_token[:20]}...")
    
    # Ensure user data includes role
    user_data = user.to_dict()
    user_data['role'] = user.role  # Make sure role is included
    
    return jsonify({
        'token': access_token,
        'user': user_data
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'customer')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    # Create appropriate user type based on role
    if role == 'professional':
        # Validate service_type_id exists
        service_type_id = data.get('service_type_id')
        if not service_type_id:
            return jsonify({"msg": "Service type is required for professionals"}), 400
            
        # Check if service exists
        service = Service.query.get(service_type_id)
        if not service:
            return jsonify({"msg": "Invalid service type selected"}), 400
            
        user = ServiceProfessional(
            username=username,
            full_name=data.get('full_name', ''),
            description=data.get('description', ''),
            service_type_id=service_type_id,
            experience_years=data.get('experience_years', 0),
            is_approved=False  # Professionals need approval
        )
    elif role == 'customer':
        user = Customer(
            username=username,
            full_name=data.get('full_name', ''),
            address=data.get('address', ''),
            pin_code=data.get('pin_code', ''),
            phone_number=data.get('phone_number', ''),
            is_approved=True  # Customers are auto-approved
        )
    else:
        return jsonify({"msg": "Invalid role specified"}), 400
        
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "msg": "User registered successfully", 
        "approval_required": not user.is_approved
    }), 201

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    return jsonify(user.to_dict()), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    # Get current user from JWT identity
    current_user_id = get_jwt_identity()
    
    # Ensure current_user_id is a string
    if not isinstance(current_user_id, str):
        current_user_id = str(current_user_id)
    
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.is_active:
        return jsonify({"message": "Account is inactive"}), 401
        
    if not user.is_approved:
        return jsonify({"message": "Account is pending approval"}), 401
    
    # Get the original token's claims
    claims = get_jwt()
    
    # Create new token with same claims but refreshed expiration
    # Ensuring user_id is always a string
    access_token = create_access_token(
        identity=str(user.id),  # Convert to string explicitly
        additional_claims={
            "role": user.role,
            "is_approved": user.is_approved,
            "is_active": user.is_active,
            "username": user.username
        }
    )
    
    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 200
