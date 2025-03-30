from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from .models import db, User, Document, ServiceProfessional, Customer, Service
import jwt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    try:
        print(f"DEBUG - Registration request received: Content-Type: {request.content_type}")
        # Check if request is form data with files
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Process form data with files
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'customer')
            full_name = request.form.get('fullName', '')
            phone_number = request.form.get('phoneNumber', '')
            
            print(f"DEBUG - Form data registration: username={username}, email={email}, role={role}, full_name={full_name}, phone_number={phone_number}")
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                return jsonify({"message": "Username already exists"}), 400
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return jsonify({"message": "Email already exists"}), 400
            
            # Create appropriate user type based on role
            if role == 'professional':
                # Get professional-specific form data
                service_type_id = request.form.get('serviceTypeId')
                description = request.form.get('description', '')
                experience_years = request.form.get('experienceYears', 0)
                pin_code = request.form.get('pinCode', '')
                
                print(f"DEBUG - Professional registration: service_type_id={service_type_id}")
                
                # Validate service_type_id exists
                if not service_type_id:
                    return jsonify({"message": "Service type is required for professionals"}), 400
                    
                # Check if service exists
                service = Service.query.get(service_type_id)
                if not service:
                    return jsonify({"message": f"Invalid service type selected (ID: {service_type_id})"}), 400
                    
                # Create professional user - ensure field names match model
                user = ServiceProfessional(
                    username=username,
                    email=email,
                    full_name=full_name,
                    phone_number=phone_number,
                    description=description,
                    pin_code=pin_code,
                    service_type_id=service_type_id,
                    experience_years=int(experience_years) if experience_years else 0,
                    is_approved=False  # Professionals need approval
                )
                
                # Process and save document files
                id_proof = request.files.get('idProof')
                address_proof = request.files.get('addressProof')
                qualification = request.files.get('qualification')
                
                print(f"DEBUG - Document files: id_proof={id_proof.filename if id_proof else None}, "
                      f"address_proof={address_proof.filename if address_proof else None}, "
                      f"qualification={qualification.filename if qualification else None}")
                
                # Check all required documents
                if not id_proof or not address_proof or not qualification:
                    return jsonify({"message": "ID proof, address proof, and qualification documents are all required"}), 400
                
                # Set password and save user to get an ID
                user.set_password(password)
                db.session.add(user)
                db.session.flush()  # Get ID without committing
                
                # Process ID proof
                if id_proof and allowed_file(id_proof.filename):
                    save_document(id_proof, user.id, 'idProof')
                
                # Process address proof
                if address_proof and allowed_file(address_proof.filename):
                    save_document(address_proof, user.id, 'addressProof')
                
                # Process qualification
                if qualification and allowed_file(qualification.filename):
                    save_document(qualification, user.id, 'qualification')
                    
            elif role == 'customer':
                # Get customer-specific form data
                address = request.form.get('address', '')
                
                # Create customer user
                user = Customer(
                    username=username,
                    email=email,
                    full_name=full_name,
                    phone_number=phone_number,
                    address=address,
                    is_approved=True  # Customers are auto-approved
                )
            else:
                return jsonify({"message": "Invalid role specified"}), 400
            
            # Finish user setup
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"DEBUG - User registered successfully: ID={user.id}, Role={user.role}")
            
            return jsonify({
                "message": "User registered successfully", 
                "approval_required": not user.is_approved,
                "user_id": user.id,
                "role": user.role
            }), 201
        else:
            # Process regular JSON data (legacy support)
            data = request.get_json()
            print(f"DEBUG - JSON registration data: {data}")
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role', 'customer')
            
            if not username or not password:
                return jsonify({"message": "Username and password are required"}), 400
            
            if User.query.filter_by(username=username).first():
                return jsonify({"message": "Username already exists"}), 400
                
            if email and User.query.filter_by(email=email).first():
                return jsonify({"message": "Email already exists"}), 400
            
            # Create appropriate user type based on role
            if role == 'professional':
                # Validate service_type_id exists
                service_type_id = data.get('service_type_id') or data.get('serviceTypeId')  # Support both formats
                if not service_type_id:
                    return jsonify({"message": "Service type is required for professionals"}), 400
                    
                # Check if service exists
                service = Service.query.get(service_type_id)
                if not service:
                    return jsonify({"message": f"Invalid service type selected (ID: {service_type_id})"}), 400
                    
                user = ServiceProfessional(
                    username=username,
                    email=email,
                    full_name=data.get('full_name', '') or data.get('fullName', ''),
                    phone_number=data.get('phone_number', '') or data.get('phoneNumber', ''),
                    description=data.get('description', ''),
                    pin_code=data.get('pin_code', '') or data.get('pinCode', ''),
                    service_type_id=service_type_id,
                    experience_years=data.get('experience_years', 0) or data.get('experienceYears', 0),
                    is_approved=False  # Professionals need approval
                )
            elif role == 'customer':
                user = Customer(
                    username=username,
                    email=email,
                    full_name=data.get('full_name', '') or data.get('fullName', ''),
                    address=data.get('address', ''),
                    phone_number=data.get('phone_number', '') or data.get('phoneNumber', ''),
                    is_approved=True  # Customers are auto-approved
                )
            else:
                return jsonify({"message": "Invalid role specified"}), 400
                
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            print(f"DEBUG - User registered successfully via JSON: ID={user.id}, Role={user.role}")
            
            return jsonify({
                "message": "User registered successfully", 
                "approval_required": not user.is_approved,
                "user_id": user.id,
                "role": user.role
            }), 201
    except Exception as e:
        db.session.rollback()
        print(f"ERROR in registration: {str(e)}")
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

def save_document(file, user_id, doc_type):
    """Save uploaded document and create database record"""
    try:
        filename = secure_filename(file.filename)
        # Create user-specific directory
        user_upload_dir = os.path.join(UPLOAD_FOLDER, f'user_{user_id}')
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Create full path with timestamp to prevent overwriting
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # Full path for saving to disk
        full_path = os.path.join(user_upload_dir, f'{doc_type}_{timestamp}_{filename}')
        
        # Save the file
        file.save(full_path)
        
        # Create document record
        document = Document(
            professional_id=user_id,
            document_type=doc_type,
            filename=filename,
            file_path=full_path,
            verified=False
        )
        
        db.session.add(document)
        return True
    except Exception as e:
        print(f"Error saving document: {e}")
        return False

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
