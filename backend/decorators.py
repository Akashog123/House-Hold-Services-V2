from functools import wraps
from flask import jsonify, request, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
import jwt

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f"DEBUG - role_required decorator called for roles: {allowed_roles}")
            
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                print(f"DEBUG - JWT claims: {claims}")
                
                user_role = claims.get("role")
                print(f"DEBUG - User role from JWT: {user_role}")
                
                # Always allow admin unless explicitly excluded
                if user_role == 'admin' and 'admin' not in allowed_roles:
                    return jsonify({"msg": "Access denied: admin not allowed for this endpoint"}), 403
                    
                if user_role in allowed_roles:
                    # Check if user is approved
                    is_approved = claims.get("is_approved", False)
                    if not is_approved and user_role == 'professional':
                        return jsonify({"msg": "Access denied: account pending approval"}), 403
                        
                    # Check if user is active
                    is_active = claims.get("is_active", True)
                    if not is_active:
                        return jsonify({"msg": "Access denied: account is inactive"}), 403
                        
                    return fn(*args, **kwargs)
                else:
                    return jsonify({"msg": "Access denied: insufficient permissions"}), 403
            except Exception as e:
                print(f"DEBUG - role_required decorator error: {str(e)}")
                print(f"DEBUG - Exception type: {type(e)}")
                return jsonify({"msg": f"Authentication error: {str(e)}"}), 401
                
        return wrapper
    return decorator

def admin_required(f):
    """
    Decorator that verifies the JWT token and checks if the user has admin role
    Uses Flask-JWT-Extended for token validation
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        print("DEBUG - admin_required decorator called")
        
        try:
            # Use Flask-JWT-Extended to verify the token
            verify_jwt_in_request()
            
            # Get claims from the token
            claims = get_jwt()
            print(f"DEBUG - JWT claims: {claims}")
            
            # Check if the user has admin role
            if claims.get('role') != 'admin':
                print("DEBUG - Non-admin role detected, access denied")
                return jsonify({'msg': 'Admin privileges required'}), 403
            
            # Store user info in Flask's g object for convenience
            g.user_id = get_jwt_identity()
            g.role = claims.get('role')
            print(f"DEBUG - Admin access granted for user ID: {g.user_id}, role: {g.role}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"DEBUG - Admin decorator error: {str(e)}")
            print(f"DEBUG - Exception type: {type(e)}")
            return jsonify({'msg': str(e)}), 401
            
    return decorated

def professional_required(fn):
    """
    Decorator for endpoints that should be accessible by professionals and admins.
    Checks for approval status for professionals.
    """
    return role_required(['professional', 'admin'])(fn)

def customer_required(fn):
    """
    Decorator for endpoints that should be accessible by customers and admins.
    """
    return role_required(['customer', 'admin'])(fn)

def professional_only(fn):
    """
    Decorator for endpoints that should ONLY be accessible by professionals.
    Excludes admin access.
    """
    return role_required(['professional'])(fn)

def customer_only(fn):
    """
    Decorator for endpoints that should ONLY be accessible by customers.
    Excludes admin access.
    """
    return role_required(['customer'])(fn)

def active_required(fn):
    """
    Decorator to ensure user account is active.
    Can be combined with other role decorators.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_active", True):
            return jsonify({"msg": "Access denied: account is inactive"}), 403
        return fn(*args, **kwargs)
    return wrapper

def approved_professional_required(fn):
    """
    Decorator specifically for approved professionals.
    Combines professional role check and approval status check.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "professional":
            return jsonify({"msg": "Access denied: professional access required"}), 403
        if not claims.get("is_approved", False):
            return jsonify({"msg": "Access denied: pending approval"}), 403
        if not claims.get("is_active", True):
            return jsonify({"msg": "Access denied: account is inactive"}), 403
        return fn(*args, **kwargs)
    return wrapper
