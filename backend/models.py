from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(128))
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.String(50))  # admin, professional, customer
    
    # Common fields for all user types
    full_name = db.Column(db.String(100))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def role(self):
        return self.user_type
    
    def to_dict(self):
        """Serialize user to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.user_type,
            'full_name': self.full_name,
            'is_approved': self.is_approved,
            'is_active': self.is_active, 
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    __mapper_args__ = {
        'polymorphic_on': user_type,
        'polymorphic_identity': 'user'
    }

# Subclass for Admin Users
class Admin(User):
    __mapper_args__ = {'polymorphic_identity': 'admin'}
    # You may add admin-specific fields if needed
    def to_dict(self):
        data = super().to_dict()
        # Add admin-specific fields if needed
        return data

# Subclass for Service Professionals
class ServiceProfessional(User):
    __mapper_args__ = {'polymorphic_identity': 'professional'}
    description = db.Column(db.Text)
    service_type_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    experience_years = db.Column(db.Integer)
    service_type = db.relationship('Service', foreign_keys=[service_type_id])
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'description': self.description,
            'service_type_id': self.service_type_id,
            'service_type_name': self.service_type.name if self.service_type else None,
            'experience_years': self.experience_years,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews
        })
        return data

# Subclass for Customers
class Customer(User):
    __mapper_args__ = {'polymorphic_identity': 'customer'}
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'address': self.address,
            'pin_code': self.pin_code,
            'phone_number': self.phone_number
        })
        return data

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    avg_duration = db.Column(db.Integer, nullable=False)  # in minutes
    status = db.Column(db.String(20), default='active')  # active, inactive, deleted (optional)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Service {self.name}>'

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pro_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='requested')  # requested, assigned, in_progress, completed
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)  # Customer notes for the request
    
    service = db.relationship('Service', backref='requests')
    customer = db.relationship('User', foreign_keys=[customer_id])
    professional = db.relationship('User', foreign_keys=[pro_id])

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    request = db.relationship('ServiceRequest', backref='reviews')

