from flask import Blueprint, jsonify, request
from .models import db, Service, ServiceProfessional, ServiceRequest, Review
import logging
from .extensions import cache

logger = logging.getLogger(__name__)
public_bp = Blueprint('public', __name__)
    
@public_bp.route('/services', methods=['GET'])
def get_services():
    """Get all available services with optional filters"""
    # Get query parameters for search/filter
    name = request.args.get('name')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    logger.debug(f"Public service search: name={name}, min_price={min_price}, max_price={max_price}")
    
    # By default, only show active services for public endpoints
    # Admin users can override this with include_inactive parameter
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Start with base query for services
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
    logger.debug(f"Found {len(services)} services matching criteria")
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'base_price': service.base_price,
        'description': service.description,
        'avg_duration': service.avg_duration,
        'status': service.status,
        'image_path': service.image_path
    } for service in services]), 200

@public_bp.route('/services/search', methods=['GET'])
def search_services():
    """Search services with optional location filter"""
    # Get query parameters for search/filter
    name = request.args.get('name')
    pin_code = request.args.get('pin_code')
    
    logger.debug(f"Public service search: name={name}, pin_code={pin_code}")
    
    # Start with base query for services
    query = Service.query.filter_by(status='active')
    
    # Apply filters based on parameters
    if name:
        query = query.filter(Service.name.ilike(f'%{name}%'))
    
    services = query.all()
    logger.debug(f"Found {len(services)} active services")
    
    # If pin code is provided, find professionals in that area
    if pin_code:
        result = []
        for service in services:
            # Find professionals for this service type in the area
            professionals = ServiceProfessional.query.filter(
                ServiceProfessional.service_type_id == service.id,
                ServiceProfessional.is_approved == True,
                ServiceProfessional.is_active == True,
                ServiceProfessional.pin_code == pin_code
                ).all()
            
            if professionals:
                service_data = {
                    'id': service.id,
                    'name': service.name,
                    'base_price': service.base_price,
                    'description': service.description,
                    'avg_duration': service.avg_duration,
                    'image_path': service.image_path,
                    'available_professionals': len(professionals)
                }
                result.append(service_data)
        logger.debug(f"Found {len(result)} services with professionals in pin code {pin_code}")
        return jsonify(result), 200
    
    # If no pin code, return all active services
    logger.debug("Returning all active services")
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'base_price': service.base_price,
        'description': service.description,
        'avg_duration': service.avg_duration
    } for service in services]), 200

@public_bp.route('/professionals/<int:professional_id>', methods=['GET'])
def get_professional_profile(professional_id):
    """Get a professional's public profile with reviews"""
    logger.debug(f"Getting public profile for professional {professional_id}")
    professional = ServiceProfessional.query.get(professional_id)
    
    if not professional:
        logger.warning(f"Professional {professional_id} not found")
        return jsonify({'error': 'Professional not found'}), 404
    
    if not professional.is_approved or not professional.is_active:
        logger.warning(f"Professional {professional_id} is not approved or not active")
        return jsonify({'error': 'This professional is not currently available'}), 404
    
    # Get reviews for this professional
    completed_requests = ServiceRequest.query.filter_by(
    pro_id=professional_id,
    status='completed'
    ).options(db.joinedload(ServiceRequest.reviews)).all()

    
    reviews_list = []
    for request in completed_requests:
        for review in request.reviews:
            reviews_list.append({
                'rating': review.rating,
                'comment': review.comment,
                'customer_name': request.customer.full_name if request.customer else 'Unknown Customer',
                'created_at': review.created_at.isoformat(),
                'service_name': request.service.name if request.service else 'Unknown Service'
            })
    
    # Create response with professional data and reviews
    result = professional.to_dict()
    result['reviews'] = reviews_list
    logger.debug(f"Found {len(reviews_list)} reviews for professional {professional_id}")
    
    return jsonify(result), 200

@public_bp.route('/services/<int:service_id>/professionals', methods=['GET'])
def get_service_professionals(service_id):
    """Get professionals available for a specific service"""
    try:
        logger.debug(f"Getting professionals for service ID: {service_id}")
        service = Service.query.get(service_id)
        
        if not service:
            logger.warning(f"Service {service_id} not found")
            return jsonify({'error': 'Service not found'}), 404
            
        # Get all active, approved professionals for this service
        professionals = ServiceProfessional.query.filter_by(
            service_type_id=service_id,
            is_approved=True,
            is_active=True
        ).all()
        
        logger.debug(f"Found {len(professionals)} professionals for service {service_id}")
        
        result = []
        for pro in professionals:
            pro_data = pro.to_dict()
            # Include additional info about the professional's experience
            pro_data['experience'] = f"{pro.experience_years} years experience" if pro.experience_years else "New Professional"
            result.append(pro_data)
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting professionals for service {service_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@public_bp.route('/services/popular', methods=['GET'])
@cache.cached(timeout=300)
def get_popular_services():
    """Get popular services based on highly-rated reviews"""
    try:
        logger.debug("Fetching popular services (cache miss)")
        top_reviews = db.session.query(
            Review, ServiceRequest
        ).join(
            ServiceRequest, ServiceRequest.id == Review.request_id
        ).filter(
            Review.rating >= 4
        ).order_by(
            Review.rating.desc()
        ).limit(5).all()
        result = []
        for review, request in top_reviews:
            review_data = {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'customer_name': request.customer.full_name if request.customer else 'Unknown Customer',
                'service_name': request.service.name if request.service else 'Unknown Service'
            }
            result.append(review_data)
        
        logger.debug(f"Returning {len(result)} popular services")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting popular services: {str(e)}")
        return jsonify({'error': str(e)}), 500