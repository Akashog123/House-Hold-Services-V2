from flask import Flask, send_from_directory, redirect
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .models import db, Admin, User
from .auth import auth_bp
from .public_routes import public_bp
from .admin_routes import admin_bp
from .customer_routes import customer_bp
from .serviceProfessional_routes import professional_bp
from .extensions import cache
import os


app = Flask(__name__, static_folder='../dist')
app.config.from_object(Config)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "supports_credentials": True
    }
})

# Celery integration
from backend.celery.celery_factory import celery_init_app
celery = celery_init_app(app)

# Add this to your Flask app configuration
app.config['JWT_JSON_KEY_NAME'] = 'access_token'
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

# Initialize extensions
jwt = JWTManager(app)
db.init_app(app)
cache.init_app(app)

# Very important - make sure we're handling integer vs string conversions properly
@jwt.user_identity_loader
def user_identity_lookup(user):
    print(f"DEBUG - JWT identity loader called with: {user}, type: {type(user)}")
    # Always convert to string to ensure consistent handling
    user_str = str(user)
    print(f"DEBUG - Converted to string: {user_str}, type: {type(user_str)}")
    return user_str

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    print(f"DEBUG - JWT user lookup called with data: {jwt_data}")
    identity = jwt_data["sub"]
    print(f"DEBUG - Identity from JWT: {identity}, type: {type(identity)}")
    
    # Convert to int for database lookup if it's a string containing only digits
    user_id = int(identity) if identity.isdigit() else identity
    print(f"DEBUG - User ID for lookup: {user_id}, type: {type(user_id)}")
    
    return User.query.filter_by(id=user_id).one_or_none()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(public_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(professional_bp, url_prefix='/api')

@app.before_first_request
def create_tables():
    db.create_all()
    # Create admin user if it doesn't exist
    create_default_admin()

def create_default_admin():
    """Create a default admin user if no admin exists."""
    admin_exists = Admin.query.first()
    if not admin_exists:
        admin = Admin(username="admin", full_name="Admin", email="admin@gmail.com")
        admin.set_password("password")
        admin.is_approved = True
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created.")

@app.route('/api')
def api_index():
    """API status endpoint"""
    return {"message": "HouseCare API is up and running"}, 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files or redirect to development server"""
    if app.debug:
        return redirect('http://localhost:5173/' + path)
    
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
