from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import admin_required, professional_required, customer_required
from .models import db, User, ServiceProfessional, Customer, Service, ServiceRequest, Review
from datetime import datetime
from sqlalchemy import func
from datetime import timedelta

routes_bp = Blueprint('routes', __name__)

# Admin routes for user management
@routes_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        # Filter out admin users from the query
        users = User.query.filter(User.role != 'admin').all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/professionals', methods=['GET'])
@admin_required
def get_professionals():
    try:
        professionals = ServiceProfessional.query.all()
        return jsonify([pro.to_dict() for pro in professionals]), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/customers', methods=['GET'])
@admin_required
def get_customers():
    try:
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/approve/<int:user_id>', methods=['PUT'])
@admin_required
def approve_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.is_approved = True
        db.session.commit()
        
        return jsonify({'message': 'User approved successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/reject/<int:user_id>', methods=['PUT'])
@admin_required
def reject_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.is_approved = False
        db.session.commit()
        
        return jsonify({'message': 'User rejected successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/block/<int:user_id>', methods=['PUT'])
@admin_required
def block_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User blocked successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/unblock/<int:user_id>', methods=['PUT'])
@admin_required
def unblock_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'User unblocked successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

# Admin routes for service management
@routes_bp.route('/admin/services', methods=['GET', 'POST'])
@jwt_required()  # Add JWT requirement
@admin_required
def manage_services():
    try:
        print(f"DEBUG - Admin services endpoint called: {request.method}")
        
        if request.method == 'GET':
            services = Service.query.all()
            print(f"DEBUG - Found {len(services)} services")
            return jsonify({
                'status': 'success',
                'data': [{
                    'id': service.id,
                    'name': service.name,
                    'base_price': float(service.base_price),
                    'description': service.description,
                    'avg_duration': int(service.avg_duration),
                    'status': 'active'
                } for service in services]
            }), 200

        elif request.method == 'POST':
            data = request.get_json()
            print(f"DEBUG - Create service request data: {data}")
            
            # Validate required fields
            required_fields = ['name', 'base_price', 'description', 'avg_duration']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required fields'
                }), 400

            # Validate data types and values
            if not isinstance(data['name'], str) or len(data['name']) == 0:
                return jsonify({'status': 'error', 'message': 'Invalid name'}), 400
            
            try:
                base_price = float(data['base_price'])
                if base_price <= 0:
                    raise ValueError
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid base price'}), 400

            if not isinstance(data['description'], str):
                return jsonify({'status': 'error', 'message': 'Invalid description'}), 400

            try:
                avg_duration = int(data['avg_duration'])
                if avg_duration <= 0:
                    raise ValueError
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid average duration'}), 400

            new_service = Service(
                name=data['name'],
                base_price=base_price,
                description=data['description'],
                avg_duration=avg_duration,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_service)
            db.session.commit()
            print(f"DEBUG - Service created with ID: {new_service.id}")

            return jsonify({
                'status': 'success',
                'message': 'Service created successfully',
                'data': {
                    'id': new_service.id,
                    'name': new_service.name,
                    'base_price': float(new_service.base_price),
                    'description': new_service.description,
                    'avg_duration': int(new_service.avg_duration),
                    'status': 'active'
                }
            }), 201

    except Exception as e:
        print(f"DEBUG - Error in admin services endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@routes_bp.route('/admin/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()  # Add JWT requirement
@admin_required
def service_detail(service_id):
    try:
        print(f"DEBUG - Admin service detail endpoint called: {request.method}, ID: {service_id}")
        
        service = Service.query.get_or_404(service_id)
        print(f"DEBUG - Found service: {service.name}")

        if request.method == 'GET':
            return jsonify({
                'status': 'success',
                'data': {
                    'id': service.id,
                    'name': service.name,
                    'base_price': float(service.base_price),
                    'description': service.description,
                    'avg_duration': int(service.avg_duration),
                    'status': service.status
                }
            }), 200

        elif request.method == 'PUT':
            data = request.get_json()
            print(f"DEBUG - Update service request data: {data}")

            if 'name' in data:
                service.name = data['name']
            if 'base_price' in data:
                service.base_price = float(data['base_price'])
            if 'description' in data:
                service.description = data['description']
            if 'avg_duration' in data:
                service.avg_duration = int(data['avg_duration'])
            if 'status' in data:
                service.status = data['status']

            service.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"DEBUG - Service {service_id} updated successfully")

            return jsonify({
                'status': 'success',
                'message': 'Service updated successfully',
                'data': {
                    'id': service.id,
                    'name': service.name,
                    'base_price': float(service.base_price),
                    'description': service.description,
                    'avg_duration': int(service.avg_duration),
                    'status': service.status
                }
            }), 200

        elif request.method == 'DELETE':
            print(f"DEBUG - Attempting to delete service {service_id}")
            
            # First check if service is associated with any active service requests
            active_requests = ServiceRequest.query.filter_by(
                service_id=service_id
            ).filter(
                ServiceRequest.status.in_(['requested', 'assigned'])
            ).first()
            
            if active_requests:
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot delete service: it has active service requests'
                }), 422
            
            # Delete the service
            db.session.delete(service)
            db.session.commit()
            print(f"DEBUG - Service {service_id} deleted successfully")
            
            return jsonify({
                'status': 'success',
                'message': 'Service deleted successfully'
            }), 200

    except Exception as e:
        print(f"DEBUG - Error in admin service detail endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Professional routes
@routes_bp.route('/professional/profile', methods=['GET', 'PUT'])
@professional_required
def manage_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if request.method == 'GET':
        return jsonify(user.to_dict()), 200
        
    if request.method == 'PUT':
        data = request.get_json()
        
        if 'email' in data:
            user.email = data['email']
            
        # Update other fields as needed
        
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

# Customer routes
@routes_bp.route('/customer/profile', methods=['GET', 'PUT'])
@customer_required
def customer_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if request.method == 'GET':
        return jsonify(user.to_dict()), 200
        
    if request.method == 'PUT':
        data = request.get_json()
        
        if 'email' in data:
            user.email = data['email']
            
        # Update other fields as needed
        
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

# Service Request Routes for Customers
@routes_bp.route('/customer/service-requests', methods=['GET', 'POST'])
@customer_required
def customer_service_requests():
    current_user_id = get_jwt_identity()
    
    # GET - List all service requests for the customer
    if request.method == 'GET':
        requests = ServiceRequest.query.filter_by(customer_id=current_user_id).all()
        return jsonify([{
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name if req.service else 'Unknown',
            'pro_id': req.pro_id,
            'professional_name': req.professional.username if req.professional else None,
            'status': req.status,
            'request_date': req.request_date.isoformat(),
            'completion_date': req.completion_date.isoformat() if req.completion_date else None
        } for req in requests]), 200
    
    # POST - Create a new service request
    if request.method == 'POST':
        data = request.get_json()
        service_id = data.get('service_id')
        
        # Check if service exists and is active
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Check if service is active
        if service.status != 'active':
            return jsonify({
                'error': 'This service is currently unavailable for new bookings'
            }), 400
            
        new_request = ServiceRequest(
            service_id=service_id,
            customer_id=current_user_id,
            status='requested',
            notes=data.get('notes', '')
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Service request created successfully',
            'request_id': new_request.id
        }), 201

@routes_bp.route('/customer/service-requests/<int:request_id>', methods=['GET', 'PUT'])
@customer_required
def customer_service_request_detail(request_id):
    current_user_id = get_jwt_identity()
    
    # Check if the request exists and belongs to the customer
    service_request = ServiceRequest.query.filter_by(
        id=request_id, 
        customer_id=current_user_id
    ).first()
    
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404
    
    # GET - Get service request details
    if request.method == 'GET':
        return jsonify({
            'id': service_request.id,
            'service_id': service_request.service_id,
            'service_name': service_request.service.name if service_request.service else 'Unknown',
            'pro_id': service_request.pro_id,
            'professional_name': service_request.professional.username if service_request.professional else None,
            'status': service_request.status,
            'request_date': service_request.request_date.isoformat(),
            'completion_date': service_request.completion_date.isoformat() if service_request.completion_date else None,
            'notes': service_request.notes
        }), 200
    
    # PUT - Update (cancel or modify) service request
    if request.method == 'PUT':
        data = request.get_json()
        
        # Only allow updates if the status is 'requested'
        if service_request.status not in ['requested', 'assigned']:
            return jsonify({
                'error': 'Cannot modify a service request that is already in progress or completed'
            }), 400
        
        # Handle cancellation
        if data.get('status') == 'cancelled':
            service_request.status = 'cancelled'
        
        # Update service if provided and status is still 'requested'
        if data.get('service_id') and service_request.status == 'requested':
            service_request.service_id = data.get('service_id')
            
        db.session.commit()
        
        return jsonify({
            'message': 'Service request updated successfully'
        }), 200

# Service Request Routes for Professionals
@routes_bp.route('/professional/service-requests', methods=['GET'])
@professional_required
def professional_service_requests():
    current_user_id = get_jwt_identity()
    
    # Get all open requests (requested) and requests assigned to this professional
    available_requests = ServiceRequest.query.filter_by(status='requested').all()
    assigned_requests = ServiceRequest.query.filter_by(
        pro_id=current_user_id
    ).all()
    
    # Combine and deduplicate
    all_requests = {}
    for req in available_requests + assigned_requests:
        if req.id not in all_requests:
            all_requests[req.id] = {
                'id': req.id,
                'service_id': req.service_id,
                'service_name': req.service.name if req.service else 'Unknown',
                'customer_id': req.customer_id,
                'customer_name': req.customer.username if req.customer else 'Unknown',
                'status': req.status,
                'request_date': req.request_date.isoformat(),
                'completion_date': req.completion_date.isoformat() if req.completion_date else None,
                'is_assigned_to_me': req.pro_id == current_user_id
            }
    
    return jsonify(list(all_requests.values())), 200

@routes_bp.route('/professional/service-requests/<int:request_id>', methods=['GET', 'PUT'])
@professional_required
def professional_service_request_detail(request_id):
    current_user_id = get_jwt_identity()
    
    # Find the service request
    service_request = ServiceRequest.query.get(request_id)
    
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404
    
    # GET - Get service request details
    if request.method == 'GET':
        return jsonify({
            'id': service_request.id,
            'service_id': service_request.service_id,
            'service_name': service_request.service.name if service_request.service else 'Unknown',
            'customer_id': service_request.customer_id,
            'customer_name': service_request.customer.username if service_request.customer else 'Unknown',
            'status': service_request.status,
            'request_date': service_request.request_date.isoformat(),
            'completion_date': service_request.completion_date.isoformat() if service_request.completion_date else None,
            'is_assigned_to_me': service_request.pro_id == current_user_id,
            'notes': service_request.notes
        }), 200
    
    # PUT - Update status (accept, reject, complete)
    if request.method == 'PUT':
        data = request.get_json()
        action = data.get('action')
        
        # Handle different actions
        if action == 'accept' and service_request.status == 'requested':
            service_request.status = 'assigned'
            service_request.pro_id = current_user_id
        elif action == 'reject' and service_request.pro_id == current_user_id:
            service_request.status = 'requested'
            service_request.pro_id = None
        elif action == 'complete' and service_request.pro_id == current_user_id and service_request.status == 'assigned':
            service_request.status = 'completed'
            service_request.completion_date = datetime.utcnow()
        else:
            return jsonify({'error': 'Invalid action for the current status'}), 400
            
        db.session.commit()
        
        return jsonify({
            'message': f'Service request {action}ed successfully'
        }), 200

# Public routes - no authentication required
@routes_bp.route('/services', methods=['GET'])
def get_services():
    # Get query parameters for search/filter
    name = request.args.get('name')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # By default, only show active services for public endpoints
    # Admin users can override this with include_inactive parameter
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Start with base query
    query = Service.query
    
    # Apply filters based on parameters
    if name:
        query = query.filter(Service.name.ilike(f'%{name}%'))
    if min_price is not None:
        query = query.filter(Service.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Service.base_price <= max_price)
    
    # Filter inactive services unless explicitly requested
    if not include_inactive:
        query = query.filter(Service.status == 'active')
    
    services = query.all()
    
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'base_price': service.base_price,
        'description': service.description,
        'avg_duration': service.avg_duration,
        'status': service.status
    } for service in services]), 200

@routes_bp.route('/services/search', methods=['GET'])
def search_services():
    # Get query parameters for search/filter
    name = request.args.get('name')
    pin_code = request.args.get('pin_code')
    
    # Start with base query for services
    query = Service.query
    
    # Apply filters based on parameters
    if name:
        query = query.filter(Service.name.ilike(f'%{name}%'))
    
    services = query.all()
    
    # If pin code is provided, find professionals in that area
    if pin_code:
        result = []
        for service in services:
            # Find professionals for this service type in the area
            professionals = ServiceProfessional.query.filter(
                ServiceProfessional.service_type_id == service.id,
                ServiceProfessional.is_approved == True,
                ServiceProfessional.is_active == True
            ).join(Customer, Customer.id == ServiceProfessional.id).filter(
                Customer.pin_code == pin_code
            ).all()
            
            if professionals:
                service_data = {
                    'id': service.id,
                    'name': service.name,
                    'base_price': service.base_price,
                    'description': service.description,
                    'avg_duration': service.avg_duration,
                    'available_professionals': len(professionals)
                }
                result.append(service_data)
        return jsonify(result), 200
    
    # If no pin code, return all services
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'base_price': service.base_price,
        'description': service.description,
        'avg_duration': service.avg_duration
    } for service in services]), 200

# Get professional profile with reviews
@routes_bp.route('/professionals/<int:professional_id>', methods=['GET'])
def get_professional_profile(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    
    if not professional:
        return jsonify({'error': 'Professional not found'}), 404
        
    if not professional.is_approved or not professional.is_active:
        return jsonify({'error': 'This professional is not currently available'}), 404
    
    # Get reviews for this professional
    completed_requests = ServiceRequest.query.filter_by(
        pro_id=professional_id,
        status='completed'
    ).all()
    
    reviews_list = []
    for request in completed_requests:
        review = Review.query.filter_by(request_id=request.id).first()
        if review:
            reviews_list.append({
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat(),
                'service_name': request.service.name if request.service else 'Unknown Service'
            })
    
    # Create response with professional data and reviews
    result = professional.to_dict()
    result['reviews'] = reviews_list
    
    return jsonify(result), 200

# Add search functionality for professionals
@routes_bp.route('/admin/search-professionals', methods=['GET'])
@admin_required
def search_professionals():
    try:
        # Get query parameters
        username = request.args.get('username')
        approval_status = request.args.get('approved')
        active_status = request.args.get('active')
        
        # Start with base query for professionals
        query = ServiceProfessional.query
        
        # Apply filters
        if username:
            query = query.filter(ServiceProfessional.username.ilike(f'%{username}%'))
        if approval_status is not None:
            is_approved = approval_status.lower() == 'true'
            query = query.filter(ServiceProfessional.is_approved == is_approved)
        if active_status is not None:
            is_active = active_status.lower() == 'true'
            query = query.filter(ServiceProfessional.is_active == is_active)
        
        professionals = query.all()
        
        return jsonify([pro.to_dict() for pro in professionals]), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

# Add search functionality for customers
@routes_bp.route('/admin/search-customers', methods=['GET'])
@admin_required
def search_customers():
    try:
        # Get query parameters
        username = request.args.get('username')
        active_status = request.args.get('active')
        
        # Start with base query for customers
        query = Customer.query
        
        # Apply filters
        if username:
            query = query.filter(Customer.username.ilike(f'%{username}%'))
        if active_status is not None:
            is_active = active_status.lower() == 'true'
            query = query.filter(Customer.is_active == is_active)
        
        customers = query.all()
        
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

# Service History and Reviews for Customers
@routes_bp.route('/customer/service-history', methods=['GET'])
@customer_required
def customer_service_history():
    current_user_id = get_jwt_identity()
    
    # Get all service requests for this customer with their review status
    requests = db.session.query(ServiceRequest, Review).\
        outerjoin(Review, Review.request_id == ServiceRequest.id).\
        filter(ServiceRequest.customer_id == current_user_id).all() 
    
    result = []
    for req, review in requests:
        request_data = {
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name if req.service else 'Unknown',
            'pro_id': req.pro_id,
            'professional_name': req.professional.username if req.professional else None,
            'status': req.status,
            'request_date': req.request_date.isoformat(),
            'completion_date': req.completion_date.isoformat() if req.completion_date else None,
            'has_review': review is not None
        }
        result.append(request_data)
    
    return jsonify(result), 200

@routes_bp.route('/customer/service-requests/<int:request_id>/review', methods=['GET', 'POST'])
@customer_required
def customer_request_review(request_id):
    current_user_id = get_jwt_identity()
        
    # Check if the request exists and belongs to the customer
    service_request = ServiceRequest.query.filter_by(
        id=request_id, 
        customer_id=current_user_id
    ).first()
        
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404
        
    if service_request.status != 'completed':
        return jsonify({'error': 'Cannot review a service that is not completed'}), 400
        
    # GET - Fetch review for this request
    if request.method == 'GET':
        review = Review.query.filter_by(request_id=request_id).first()
                
        if not review:
            return jsonify({'error': 'No review found for this request'}), 404
                    
        return jsonify({
            'id': review.id,
            'request_id': review.request_id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat() if review.created_at else None
        }), 200
        
    # POST - Create a new review
    if request.method == 'POST':
        # Check if a review already exists
        existing_review = Review.query.filter_by(request_id=request_id).first()
        if existing_review:
            return jsonify({'error': 'A review already exists for this request'}), 400
                
        data = request.get_json()
        rating = data.get('rating')
                
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be a number between 1 and 5'}), 400
                
        new_review = Review(
            request_id=request_id,
            rating=rating,
            comment=data.get('comment', '')
        )
                
        db.session.add(new_review)
        db.session.commit()
                                
        return jsonify({'message': 'Review submitted successfully'}), 201

# Update service completion with review system
@routes_bp.route('/customer/service-requests/<int:request_id>/complete', methods=['PUT'])
@customer_required
def complete_service_request(request_id):
    current_user_id = get_jwt_identity()
    service_request = ServiceRequest.query.filter_by(
        id=request_id,
        customer_id=current_user_id,
        status='assigned'
    ).first()
    
    if not service_request:
        return jsonify({'error': 'Service request not found or cannot be completed'}), 404
    
    # Mark request as completed
    service_request.status = 'completed'
    service_request.completion_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Service request marked as completed'}), 200

# Update the review submission to update professional's average rating
@routes_bp.route('/customer/service-requests/<int:request_id>/review', methods=['POST'])
@customer_required
def submit_review(request_id):
    current_user_id = get_jwt_identity()
    
    # Check if the request exists and belongs to the customer
    service_request = ServiceRequest.query.filter_by(
        id=request_id, 
        customer_id=current_user_id,
        status='completed'
    ).first()
    
    if not service_request:
        return jsonify({'error': 'Service request not found or not completed'}), 404
    
    # Check if a review already exists
    existing_review = Review.query.filter_by(request_id=request_id).first()
    if existing_review:
        return jsonify({'error': 'A review already exists for this request'}), 400
    
    data = request.get_json()
    rating = data.get('rating')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be a number between 1 and 5'}), 400
    
    # Create the review
    new_review = Review(
        request_id=request_id,
        rating=rating,
        comment=data.get('comment', '')
    )
    
    db.session.add(new_review)
    
    # Update professional's average rating
    professional = ServiceProfessional.query.get(service_request.pro_id)
    if professional:
        # Calculate new average
        new_total_reviews = professional.total_reviews + 1
        new_avg = ((professional.average_rating * professional.total_reviews) + rating) / new_total_reviews
        
        professional.average_rating = new_avg
        professional.total_reviews = new_total_reviews
    
    db.session.commit()
    
    return jsonify({'message': 'Review submitted successfully'}), 201

# Professional statistics
@routes_bp.route('/professional/stats', methods=['GET'])
@professional_required
def professional_stats():
    current_user_id = get_jwt_identity()
        
    # Count completed requests
    completed_count = ServiceRequest.query.filter_by(
        pro_id=current_user_id, 
        status='completed'
    ).count()
    
    # Count active requests
    active_count = ServiceRequest.query.filter_by(
        pro_id=current_user_id, 
        status='assigned'
    ).count()
    
    # Calculate average rating
    reviews = db.session.query(Review).join(ServiceRequest, ServiceRequest.id == Review.request_id).filter(
        ServiceRequest.pro_id == current_user_id
    ).all()
    total_ratings = sum(review.rating for review in reviews) if reviews else 0
    avg_rating = round(total_ratings / len(reviews), 1) if reviews else 0
    
    # Calculate total earnings (placeholder - would need actual payment data in real system)
    total_earnings = 0
    completed_requests = ServiceRequest.query.filter_by(
        pro_id=current_user_id, 
        status='completed'
    ).all()
    for req in completed_requests:
        if req.service:
            total_earnings += req.service.base_price
    
    return jsonify({
        'completed': completed_count,
        'active': active_count,
        'rating': avg_rating,
        'totalEarnings': f'${total_earnings:.2f}'
    }), 200

# Customer statistics
@routes_bp.route('/customer/service-stats', methods=['GET'])
@customer_required
def customer_service_stats():
    current_user_id = get_jwt_identity()
        
    # Get counts of different request statuses
    total_requests = ServiceRequest.query.filter_by(customer_id=current_user_id).count()
    completed_requests = ServiceRequest.query.filter_by(customer_id=current_user_id, status='completed').count()
    pending_requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == current_user_id,
        ServiceRequest.status.in_(['requested', 'assigned'])
    ).count()
    
    # Calculate total spent
    total_spent = 0
    completed_requests_data = ServiceRequest.query.filter_by(
        customer_id=current_user_id, 
        status='completed'
    ).all()
    for req in completed_requests_data:
        if req.service:
            total_spent += req.service.base_price
    
    return jsonify({
        'totalRequests': total_requests,
        'completedRequests': completed_requests,
        'pendingRequests': pending_requests,
        'totalSpent': total_spent
    }), 200

# Admin analytics
@routes_bp.route('/admin/analytics/revenue', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_analytics():
    try:
        # Calculate total revenue from completed service requests
        total_revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed'
        ).scalar() or 0.0

        # Calculate revenue growth (comparing current month to previous month)
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        
        current_month_revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed',
            ServiceRequest.completion_date >= current_month
        ).scalar() or 0.0

        last_month_revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed',
            ServiceRequest.completion_date >= last_month,
            ServiceRequest.completion_date < current_month
        ).scalar() or 0.0

        revenue_growth = 0
        if last_month_revenue > 0:
            revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100

        return jsonify({
            'total_revenue': total_revenue,
            'revenue_growth': revenue_growth
        })
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/services', methods=['GET'])
@jwt_required()
@admin_required
def get_services_stats():
    try:
        total_active_services = Service.query.filter_by(is_active=True).count()
        
        # Calculate service growth
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        
        new_services = Service.query.filter(
            Service.created_at >= current_month
        ).count()
        
        old_services = Service.query.filter(
            Service.created_at >= last_month,
            Service.created_at < current_month
        ).count()

        service_growth = 0
        if old_services > 0:
            service_growth = ((new_services - old_services) / old_services) * 100

        return jsonify({
            'total_active_services': total_active_services,
            'service_growth': service_growth
        })
    except Exception as e:
        return jsonify({'msg': str(e)}), 422

# User statistics
@routes_bp.route('/admin/users/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_users_stats():
    try:
        # Count professionals (excluding admins)
        total_professionals = User.query.filter_by(role='professional').count()
        
        # Count customers (excluding admins)
        total_customers = User.query.filter_by(role='customer').count()
        
        # Calculate user growth by role (comparing current month to previous month)
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        
        # Professional growth
        new_professionals = User.query.filter(
            User.created_at >= current_month,
            User.role == 'professional'
        ).count()
        
        old_professionals = User.query.filter(
            User.created_at >= last_month,
            User.created_at < current_month,
            User.role == 'professional'
        ).count()

        professional_growth = 0
        if old_professionals > 0:
            professional_growth = ((new_professionals - old_professionals) / old_professionals) * 100

        # Customer growth
        new_customers = User.query.filter(
            User.created_at >= current_month,
            User.role == 'customer'
        ).count()
        
        old_customers = User.query.filter(
            User.created_at >= last_month,
            User.created_at < current_month,
            User.role == 'customer'
        ).count()

        customer_growth = 0
        if old_customers > 0:
            customer_growth = ((new_customers - old_customers) / old_customers) * 100

        return jsonify({
            'total_professionals': total_professionals,
            'professional_growth': professional_growth,
            'total_customers': total_customers,
            'customer_growth': customer_growth
        }), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 422
