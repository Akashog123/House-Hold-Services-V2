from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import customer_required
from .models import db, User, Customer, ServiceProfessional, ServiceRequest, Service, Review
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer/profile', methods=['GET', 'PUT'])
@customer_required
def customer_profile():
    """Get or update a customer's profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if request.method == 'GET':
        logger.debug(f"Customer {current_user_id} requesting profile")
        return jsonify(user.to_dict()), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        logger.debug(f"Customer {current_user_id} updating profile with data: {data}")
        
        if 'email' in data:
            user.email = data['email']
            
        # Update other fields as needed
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'address' in data:
            customer = Customer.query.get(current_user_id)
            if customer:
                customer.address = data['address']
        
        db.session.commit()
        logger.info(f"Customer {current_user_id} profile updated")
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

@customer_bp.route('/customer/service-requests', methods=['GET', 'POST'])
@customer_required
def customer_service_requests():
    """Get or create service requests for a customer"""
    current_user_id = get_jwt_identity()
    
    # GET - List all service requests for the customer
    if request.method == 'GET':
        logger.debug(f"Customer {current_user_id} requesting service requests")
        requests = ServiceRequest.query.filter_by(customer_id=current_user_id).all()
        logger.debug(f"Found {len(requests)} requests for customer {current_user_id}")
        return jsonify([{
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name if req.service else 'Unknown',
            'pro_id': req.pro_id,
            'professional_name': req.professional.username if req.professional else None,
            'status': req.status,
            'notes': req.notes if req.notes else None,
            'service_price': req.service.base_price,
            'service_duration': req.service.avg_duration,
            'request_date': req.request_date.isoformat(),
            'assigned_date': req.assigned_date.isoformat() if req.assigned_date else None,
            'completed_on': req.completed_on.isoformat() if req.completed_on else None,
            'cancelled_on': req.cancelled_on.isoformat() if req.cancelled_on else None,
            'cancelled_by': req.cancelled_by if req.cancelled_by else None,
            'completion_date': req.completion_date.isoformat() if req.completion_date else None
        } for req in requests]), 200
    
    # POST - Create a new service request
    if request.method == 'POST':
        data = request.get_json()
        service_id = data.get('service_id')
        professional_id = data.get('professional_id')
        completion_date = data.get('completion_date')
        logger.debug(f"Customer {current_user_id} creating service request for service {service_id} with professional {professional_id}, completion date: {completion_date}")
        
        # Check if service exists and is active
        service = Service.query.get(service_id)
        if not service:
            logger.warning(f"Service {service_id} not found")
            return jsonify({'error': 'Service not found'}), 404
        
        if service.status != 'active':
            logger.warning(f"Service {service_id} is not active")
            return jsonify({
                'error': 'This service is currently unavailable for new bookings'
            }), 400
            
        new_request = ServiceRequest(
            service_id=service_id,
            customer_id=current_user_id,
            status='requested',
            notes=data.get('notes', ''),
            request_date=datetime.utcnow(),
            completion_date=datetime.fromisoformat(completion_date) if completion_date else None
        )
        
        # If a professional was selected, assign the request to that professional
        # but keep status as 'requested' so they can accept/reject
        if professional_id:
            # Validate the professional exists and is approved/active
            professional = ServiceProfessional.query.filter_by(
                id=professional_id,
                is_approved=True,
                is_active=True
            ).first()
            
            if professional:
                # Verify the professional handles this service type
                if professional.service_type_id == service_id:
                    new_request.pro_id = professional_id
                    logger.info(f"Request assigned to professional {professional_id} with 'requested' status")
                else:
                    logger.warning(f"Professional {professional_id} does not provide service {service_id}")
            else:
                logger.warning(f"Selected professional {professional_id} not found or not approved/active")
        
        db.session.add(new_request)
        db.session.commit()
        logger.info(f"Customer {current_user_id} created service request {new_request.id} for service {service_id}")
        return jsonify({
            'message': 'Service request created successfully',
            'request_id': new_request.id
        }), 201

@customer_bp.route('/customer/service-requests/<int:request_id>', methods=['GET', 'PUT'])
@customer_required
def customer_service_request_detail(request_id):
    """Get or update a specific service request for a customer"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Customer {current_user_id} accessing request {request_id}")
    
    # Check if the request exists and belongs to the customer
    service_request = ServiceRequest.query.filter_by(
        id=request_id, 
        customer_id=current_user_id
    ).first()
    
    if not service_request:
        logger.warning(f"Service request {request_id} not found for customer {current_user_id}")
        return jsonify({'error': 'Service request not found'}), 404
    
    # GET - Get service request details
    if request.method == 'GET':
        logger.debug(f"Customer {current_user_id} getting details for request {request_id}")
        return jsonify({
            'id': service_request.id,
            'service_id': service_request.service_id,
            'service_name': service_request.service.name if service_request.service else 'Unknown',
            'pro_id': service_request.pro_id,
            'professional_name': service_request.professional.username if service_request.professional else None,
            'professional_phone': service_request.professional.phone_number if service_request.professional else None,
            'professional_email': service_request.professional.email if service_request.professional else None,
            'status': service_request.status,
            'service_price': service_request.service.base_price,
            'service_duration': service_request.service.avg_duration,
            'request_date': service_request.request_date.isoformat(),
            'assigned_date': service_request.assigned_date.isoformat() if service_request.assigned_date else None,
            'completed_on': service_request.completed_on.isoformat() if service_request.completed_on else None,
            'cancelled_on': service_request.cancelled_on.isoformat() if service_request.cancelled_on else None,
            'cancelled_by': service_request.cancelled_by if service_request.cancelled_by else None,
            'completion_date': service_request.completion_date.isoformat() if service_request.completion_date else None,
            'notes': service_request.notes
        }), 200
    
    # PUT - Update (cancel or modify) service request
    if request.method == 'PUT':
        data = request.get_json()
        logger.debug(f"Customer {current_user_id} updating request {request_id} with data: {data}")
        
        # Only allow updates if the status is 'requested', 'assigned', or 'inprogress'
        if service_request.status not in ['requested', 'assigned', 'inprogress', 'completed']:
            logger.warning(f"Cannot modify request {request_id} in status {service_request.status}")
            return jsonify({
                'error': 'Cannot modify a service request that is already completed or cancelled'
            }), 400
        
        # Handle cancellation
        if data.get('status') == 'cancelled':
            service_request.status = 'cancelled'
            service_request.cancelled_on = datetime.utcnow()
            service_request.cancelled_by = 'customer'
            logger.info(f"Customer {current_user_id} cancelled request {request_id}")
        
        # Handle status change to completed
        elif data.get('status') == 'completed' and service_request.status != 'completed':
            service_request.status = 'completed'
            service_request.completed_on = datetime.utcnow()
            logger.info(f"Customer {current_user_id} marked request {request_id} as completed")
        
        # Handle status change from completed to assigned
        elif data.get('status') == 'assigned' and service_request.status == 'completed':
            service_request.status = 'assigned'
            service_request.completed_on = None
            logger.info(f"Customer {current_user_id} changed request {request_id} status from completed to assigned")
        
        # Update service if provided and status is still 'requested'
        if data.get('service_id') and service_request.status == 'requested':
            service_request.service_id = data.get('service_id')
            logger.info(f"Customer {current_user_id} changed service for request {request_id} to {data.get('service_id')}")
        
        # Update notes if provided
        if 'notes' in data:
            service_request.notes = data.get('notes')
            logger.info(f"Customer {current_user_id} updated notes for request {request_id}")
        
        # Update completion date if provided
        if 'completion_date' in data:
            try:
                completion_date = data.get('completion_date')
                service_request.completion_date = datetime.fromisoformat(completion_date) if completion_date else None
                logger.info(f"Customer {current_user_id} updated completion date for request {request_id}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid completion date format: {data.get('completion_date')}")
                return jsonify({'error': 'Invalid date format for completion date'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Service request updated successfully'}), 200

@customer_bp.route('/customer/service-requests/<int:request_id>/review', methods=['GET', 'POST'])
@customer_required
def customer_request_review(request_id):
    """Get or submit a review for a completed service request"""
    current_user_id = get_jwt_identity()
    
    # Check if the request exists and belongs to the customer
    service_request = ServiceRequest.query.filter_by(
        id=request_id, 
        customer_id=current_user_id
    ).first()
    
    if not service_request:
        logger.warning(f"Service request {request_id} not found for customer {current_user_id}")
        return jsonify({'error': 'Service request not found'}), 404
    
    if service_request.status != 'completed':
        logger.warning(f"Cannot review request {request_id} with status {service_request.status}")
        return jsonify({'error': 'Cannot review a service that is not completed'}), 400
    
    # GET - Fetch review for this request
    if request.method == 'GET':
        logger.debug(f"Customer {current_user_id} getting review for request {request_id}")
        review = Review.query.filter_by(request_id=request_id).first()
                
        if not review:
            logger.debug(f"No review found for request {request_id}")
            return jsonify({'error': 'No review found for this request'}), 404
        
        logger.debug(f"Found review for request {request_id}: rating={review.rating}")
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
            logger.warning(f"Review already exists for request {request_id}")
            return jsonify({'error': 'A review already exists for this request'}), 400
        
        data = request.get_json()
        rating = data.get('rating')
        logger.debug(f"Customer {current_user_id} submitting review for request {request_id} with rating {rating}")
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            logger.warning(f"Invalid rating {rating} for review")
            return jsonify({'error': 'Rating must be a number between 1 and 5'}), 400
                
        new_review = Review(
            request_id=request_id,
            rating=rating,
            comment=data.get('comment', ''),
            created_at=datetime.utcnow()
        )
                
        db.session.add(new_review)
        db.session.commit()
        
        # Update professional's average rating
        professional = ServiceProfessional.query.get(service_request.pro_id)
        if professional:
            # Calculate new average:
            new_total_reviews = professional.total_reviews + 1
            new_avg = ((professional.average_rating * professional.total_reviews) + rating) / new_total_reviews
            professional.average_rating = new_avg
            professional.total_reviews = new_total_reviews
            logger.debug(f"Updated professional {professional.id} rating to {new_avg} ({new_total_reviews} reviews)")
        
        db.session.commit()
        logger.info(f"Customer {current_user_id} submitted review for request {request_id}")
                                
        return jsonify({'message': 'Review submitted successfully'}), 201
    
@customer_bp.route('/customer/service-stats', methods=['GET'])
@customer_required
def customer_service_stats():
    """Get service statistics for a customer's dashboard"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Customer {current_user_id} requesting service statistics")
    
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
    
    logger.debug(f"Customer {current_user_id} stats: total={total_requests}, completed={completed_requests}, pending={pending_requests}, spent=${total_spent}")
    return jsonify({
        'totalRequests': total_requests,
        'completedRequests': completed_requests,
        'pendingRequests': pending_requests,
        'totalSpent': total_spent
    }), 200

@customer_bp.route('/customer/service-history', methods=['GET'])
@customer_required
def customer_service_history():
    """Get service history for a customer including review status"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Customer {current_user_id} requesting service history")
    # Get all service requests for this customer with their review status
    requests = db.session.query(ServiceRequest, Review).\
        outerjoin(Review, Review.request_id == ServiceRequest.id).\
        filter(ServiceRequest.customer_id == current_user_id).all()
    
    logger.debug(f"Found {len(requests)} service requests in history for customer {current_user_id}")
    
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
