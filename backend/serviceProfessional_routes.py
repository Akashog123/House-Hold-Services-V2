from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import professional_required
from .models import db, User, ServiceProfessional, ServiceRequest, Review
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/professional/profile', methods=['GET', 'PUT'])
@professional_required
def professional_profile():
    """Get or update professional's profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if request.method == 'GET':
        logger.debug(f"Professional {current_user_id} requesting profile")
        return jsonify(user.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        logger.debug(f"Professional {current_user_id} updating profile with data: {data}")
        
        if 'email' in data:
            user.email = data['email']
            
        # Update other fields as needed
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'description' in data:
            professional = ServiceProfessional.query.get(current_user_id)
            if professional:
                professional.description = data['description']
        
        db.session.commit()
        logger.info(f"Professional {current_user_id} profile updated")
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

@professional_bp.route('/professional/service-requests', methods=['GET'])
@professional_required
def professional_service_requests():
    """Get service requests available to or assigned to this professional"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Professional {current_user_id} requesting service requests")
    
    # Get the professional's service type ID
    professional = ServiceProfessional.query.get(current_user_id)
    # Get open requests that match the professional's service type
    # AND are specifically assigned to this professional
    available_requests = ServiceRequest.query.filter(
        ServiceRequest.service_id == professional.service_type_id,
        (ServiceRequest.pro_id == current_user_id)
    ).all()
    
    logger.debug(f"Found {len(available_requests)} available requests.")
    
    # Combine and deduplicate
    all_requests = {}
    for req in available_requests:
        if (req.id not in all_requests):
            all_requests[req.id] = {
                'id': req.id,
                'service_id': req.service_id,
                'service_name': req.service.name if req.service else 'Unknown',
                'customer_id': req.customer_id,
                'customer_name': req.customer.username if req.customer else 'Unknown',
                'status': req.status,
                'notes': req.notes if req.notes else None,
                'request_date': req.request_date.isoformat(),
                'completion_date': req.completion_date.isoformat() if req.completion_date else None,
                'completed_on': req.completed_on.isoformat() if req.completed_on else None,
                'assigned_date': req.assigned_date.isoformat() if req.assigned_date else None,
                'cancelled_on': req.cancelled_on.isoformat() if req.cancelled_on else None,
                'cancelled_by': req.cancelled_by if req.cancelled_by else None
            }
    
    return jsonify(list(all_requests.values())), 200

@professional_bp.route('/professional/service-requests/<int:request_id>', methods=['GET', 'PUT'])
@professional_required
def professional_service_request_detail(request_id):
    """Get or update a specific service request for a professional"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Professional {current_user_id} accessing request {request_id}")
    
    # Find the service request
    service_request = ServiceRequest.query.filter_by(
        id=request_id, pro_id=current_user_id).first()
    if not service_request:
        logger.warning(f"Service request {request_id} not found")
        return jsonify({'error': 'Service request not found'}), 404
    
    # GET - Get service request details
    if request.method == 'GET':
        logger.debug(f"Professional {current_user_id} getting details for request {request_id}")
        return jsonify({
            'id': service_request.id,
            'service_id': service_request.service_id,
            'service_name': service_request.service.name if service_request.service else 'Unknown',
            'customer_id': service_request.customer_id,
            'customer_name': service_request.customer.username if service_request.customer else 'Unknown',
            'status': service_request.status,
            'customer_address': service_request.customer.address if service_request.customer.address else None,
            'customer_email': service_request.customer.email if service_request.customer.email else None,
            'customer_phone_number': service_request.customer.phone_number if service_request.customer.phone_number else None,
            'request_date': service_request.request_date.isoformat(),
            'completion_date': service_request.completion_date.isoformat() if service_request.completion_date else None,
            'assigned_date': service_request.assigned_date.isoformat() if service_request.assigned_date else None,
            'completed_on': service_request.completed_on.isoformat() if service_request.completed_on else None,
            'notes': service_request.notes,
            'cancelled_on': service_request.cancelled_on.isoformat() if service_request.cancelled_on else None,
            'cancelled_by': service_request.cancelled_by if service_request.cancelled_by else None
        }), 200
    
    # PUT - Update status (accept, reject, complete)
    if request.method == 'PUT':
        data = request.get_json()
        logger.debug(f"Professional {current_user_id} performing action '{data.get('action')}' on request {request_id}")
        logger.debug(f"proid {service_request.pro_id} current_user_id {current_user_id}")
        
        action = data.get('action')
        # Handle different actions
        if ((action == 'accept') and (service_request.status == 'requested')):
            service_request.status = 'assigned'
            service_request.assigned_date = datetime.utcnow()
            service_request.pro_id = current_user_id
            logger.info(f"Professional {current_user_id} accepted request {request_id}")
        elif (action == 'reject'):    
            service_request.status = 'cancelled'
            service_request.cancelled_by = 'professional'
            service_request.cancelled_on = datetime.utcnow()
            logger.info(f"Professional {current_user_id} cancelled request {request_id}")
        elif ((action == 'complete') and (service_request.status == 'assigned')):
            service_request.status = 'completed'
            service_request.completed_on = datetime.utcnow()
            logger.info(f"Professional {current_user_id} completed request {request_id}")
        else:
            # Add more detailed logging for debugging
            logger.warning(f"Invalid action '{action}' for request {request_id} in status {service_request.status}. pro_id={service_request.pro_id}, current_user_id={current_user_id}")
            return jsonify({'error': 'Invalid action for the current status'}), 400
        
        db.session.commit()
        return jsonify({'message': f'Service request {action}ed successfully'}), 200

@professional_bp.route('/professional/stats', methods=['GET'])
@professional_required
def professional_stats():
    """Get statistics for a professional's dashboard"""
    current_user_id = get_jwt_identity()
    logger.debug(f"Professional {current_user_id} requesting statistics")
    
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
    
    logger.debug(f"Professional {current_user_id} stats: completed={completed_count}, active={active_count}, rating={avg_rating}, earnings=${total_earnings:.2f}")
    return jsonify({
        'completed': completed_count,
        'active': active_count,
        'rating': avg_rating,
        'totalEarnings': f'${total_earnings:.2f}'
    }), 200

@professional_bp.route('/professional/status/<int:user_id>', methods=['GET'])
def check_professional_status(user_id):
    """Check the approval status of a professional"""
    try:
        logger.debug(f"Checking status of professional {user_id}")
        professional = ServiceProfessional.query.get(user_id)
        
        if not professional:
            logger.warning(f"Professional ID {user_id} not found")
            return jsonify({'error': 'Professional not found'}), 404
        
        logger.debug(f"Professional {user_id} status: approved={professional.is_approved}")
        return jsonify({
            'id': professional.id,
            'username': professional.username,
            'is_approved': professional.is_approved,
            'rejection_reason': professional.rejection_reason if hasattr(professional, 'rejection_reason') else None
        }), 200
    except Exception as e:
        logger.error(f"Error checking professional status: {str(e)}")
        return jsonify({'error': str(e)}), 500
