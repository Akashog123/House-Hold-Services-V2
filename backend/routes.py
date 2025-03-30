from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import admin_required, professional_required, customer_required
from .models import db, User, ServiceProfessional, Customer, Service, ServiceRequest, Review, Document
from datetime import datetime
from sqlalchemy import func
from datetime import timedelta
import os
import logging
from werkzeug.utils import secure_filename
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

routes_bp = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'service-images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#=======================================================================
# ADMIN ROUTES
#=======================================================================

@routes_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users except admin users"""
    try:
        logger.debug("Admin requesting all users")
        users = User.query.filter(User.role != 'admin').all()
        logger.debug(f"Found {len(users)} non-admin users")
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/professionals', methods=['GET'])
@admin_required
def get_professionals():
    """Get all professional users with optional filters"""
    try:
        # Get query parameters
        approval_status = request.args.get('approved')
        active_status = request.args.get('active')
        include_verification = request.args.get('include_verification', 'false').lower() == 'true'
        
        logger.debug(f"Admin requesting professionals with filters: approved={approval_status}, active={active_status}, include_verification={include_verification}")
        
        # Start with base query for all professionals
        query = ServiceProfessional.query
        
        # Apply filters if provided
        if approval_status is not None:
            is_approved = approval_status.lower() == 'true'
            query = query.filter(ServiceProfessional.is_approved == is_approved)
        
        if active_status is not None:
            is_active = active_status.lower() == 'true'
            query = query.filter(ServiceProfessional.is_active == is_active)
        
        professionals = query.all()
        logger.debug(f"Found {len(professionals)} professionals matching criteria")
        
        # If verification info is requested, include it
        if include_verification:
            result = []
            for pro in professionals:
                pro_data = pro.to_dict()
                
                # Get documents for verification status
                docs = Document.query.filter_by(professional_id=pro.id).all()
                pro_data['documents_count'] = len(docs)
                
                # Initialize document verification status
                doc_types = {'idProof': False, 'addressProof': False, 'qualification': False}
                
                # Check verification status for each document
                for doc in docs:
                    if doc.document_type in doc_types:
                        doc_types[doc.document_type] = doc.verified
                
                # Set overall verification status
                pro_data['documents_verified'] = all(doc_types.values()) and len(docs) >= 3
                pro_data['documents_status'] = doc_types
                
                # Get service name if available
                if pro.service_type_id:
                    service = Service.query.get(pro.service_type_id)
                    pro_data['service_name'] = service.name if service else None
                
                result.append(pro_data)
            
            return jsonify(result), 200
        else:
            # Just return basic professional info without verification details
            return jsonify([pro.to_dict() for pro in professionals]), 200
    except Exception as e:
        logger.error(f"Error getting professionals: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/professionals/details', methods=['GET'])
@admin_required
def get_professionals_details():
    """Get detailed information about professionals including approval status and documents"""
    try:
        logger.debug("Admin requesting detailed professional information")
        professionals = ServiceProfessional.query.all()
        logger.debug(f"Found {len(professionals)} professionals to process")
        
        result = []
        for pro in professionals:
            # Get documents for this professional
            documents = Document.query.filter_by(professional_id=pro.id).all()
            
            pro_data = pro.to_dict()
            pro_data['documents_count'] = len(documents)
            pro_data['documents_verified'] = all(doc.verified for doc in documents) if documents else False
            
            # Get service name
            if pro.service_type_id:
                service = Service.query.get(pro.service_type_id)
                pro_data['service_name'] = service.name if service else None
            
            result.append(pro_data)
        
        logger.debug(f"Returning {len(result)} professional records with details")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting professional details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/admin/customers', methods=['GET'])
@admin_required
def get_customers():
    """Get all customer users"""
    try:
        logger.debug("Admin requesting all customers")
        customers = Customer.query.all()
        logger.debug(f"Found {len(customers)} customers")
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/approve/<int:user_id>', methods=['PUT'])
@admin_required
def approve_user(user_id):
    """Approve a user account"""
    try:
        logger.debug(f"Admin approving user ID: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User ID {user_id} not found for approval")
            return jsonify({'error': 'User not found'}), 404
            
        # For professionals, check if all required documents are verified
        if user.role == 'professional':
            # Find all documents for this professional
            documents = Document.query.filter_by(professional_id=user_id).all()
            
            # Check if the professional has uploaded all required documents
            required_doc_types = ['idProof', 'addressProof', 'qualification']
            uploaded_doc_types = [doc.document_type for doc in documents]
            
            # Check for missing documents
            missing_docs = [doc_type for doc_type in required_doc_types if doc_type not in uploaded_doc_types]
            
            if missing_docs:
                logger.warning(f"Professional is missing required documents: {missing_docs}")
                return jsonify({
                    'error': 'Cannot approve professional with missing required documents',
                    'missing_documents': missing_docs
                }), 400
            
            # Check if all uploaded documents are verified
            verified_status = {}
            for doc_type in required_doc_types:
                matching_docs = [doc for doc in documents if doc.document_type == doc_type]
                if not matching_docs or not matching_docs[0].verified:
                    verified_status[doc_type] = False
                else:
                    verified_status[doc_type] = True
            
            unverified_docs = [doc_type for doc_type, verified in verified_status.items() if not verified]
            if unverified_docs:
                logger.warning(f"Professional has unverified documents: {unverified_docs}")
                return jsonify({
                    'error': 'Cannot approve professional with unverified documents',
                    'unverified_documents': unverified_docs
                }), 400
        
        # Update user approval status
        user.is_approved = True
        
        # Clear any rejection reason if it exists
        professional = ServiceProfessional.query.get(user_id)
        if professional and hasattr(professional, 'rejection_reason'):
            professional.rejection_reason = None
        
        db.session.commit()
        logger.info(f"User ID {user_id} ({user.username}) approved successfully")
        
        return jsonify({'message': 'User approved successfully', 'user': user.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving user {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/reject/<int:user_id>', methods=['PUT'])
@admin_required
def reject_user(user_id):
    """Reject a user account with optional reason"""
    try:
        logger.debug(f"Admin rejecting user ID: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User ID {user_id} not found for rejection")
            return jsonify({'error': 'User not found'}), 404
        
        # Update user approval status
        user.is_approved = False
        
        # If it's a professional and a rejection reason is provided, store it
        if user.role == 'professional':
            data = request.get_json() or {}
            rejection_reason = data.get('rejection_reason')
            
            if rejection_reason:
                logger.debug(f"Rejection reason provided: {rejection_reason}")
                professional = ServiceProfessional.query.get(user_id)
                if professional:
                    professional.rejection_reason = rejection_reason
        
        db.session.commit()
        logger.info(f"User ID {user_id} ({user.username}) rejected successfully")
        
        return jsonify({'message': 'User rejected successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting user {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/admin/block/<int:user_id>', methods=['PUT'])
@admin_required
def block_user(user_id):
    """Block (deactivate) a user account"""
    try:
        logger.debug(f"Admin blocking user ID: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User ID {user_id} not found for blocking")
            return jsonify({'error': 'User not found'}), 404
            
        user.is_active = False
        db.session.commit()
        logger.info(f"User ID {user_id} ({user.username}) blocked successfully")
        
        return jsonify({'message': 'User blocked successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error blocking user {user_id}: {str(e)}")
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/unblock/<int:user_id>', methods=['PUT'])
@admin_required
def unblock_user(user_id):
    """Unblock (reactivate) a user account"""
    try:
        logger.debug(f"Admin unblocking user ID: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User ID {user_id} not found for unblocking")
            return jsonify({'error': 'User not found'}), 404
            
        user.is_active = True
        db.session.commit()
        logger.info(f"User ID {user_id} ({user.username}) unblocked successfully")
        
        return jsonify({'message': 'User unblocked successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error unblocking user {user_id}: {str(e)}")
        return jsonify({'msg': str(e)}), 422

@routes_bp.route('/admin/search-professionals', methods=['GET'])
@admin_required
def search_professionals():
    """Search professionals with filters"""
    try:
        # Get query parameters
        username = request.args.get('username')
        approval_status = request.args.get('approved')
        active_status = request.args.get('active')
        include_verification = request.args.get('include_verification', 'false').lower() == 'true'
        
        logger.debug(f"Admin searching professionals with filters: username={username}, approved={approval_status}, active={active_status}, include_verification={include_verification}")
        
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
        logger.debug(f"Found {len(professionals)} professionals matching criteria")
        
        result = []
        for pro in professionals:
            pro_data = pro.to_dict()
            
            # If requested, include document verification status
            if include_verification:
                # Count documents
                docs = Document.query.filter_by(professional_id=pro.id).all()
                pro_data['documents_count'] = len(docs)
                
                # Initialize document verification status
                doc_types = {'idProof': False, 'addressProof': False, 'qualification': False}
                
                # Check verification status for each document
                for doc in docs:
                    if doc.document_type in doc_types:
                        doc_types[doc.document_type] = doc.verified
                
                # Set overall verification status to true only if all required documents are verified
                pro_data['documents_verified'] = all(doc_types.values()) and len(docs) >= 3
                
                # Add individual document status
                pro_data['documents_status'] = doc_types
                
                logger.debug(f"Professional {pro.id} documents_verified={pro_data['documents_verified']}, status={doc_types}")
            
            result.append(pro_data)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error searching professionals: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/search-customers', methods=['GET'])
@admin_required
def search_customers():
    """Search customers with filters"""
    try:
        # Get query parameters
        username = request.args.get('username')
        active_status = request.args.get('active')
        
        logger.debug(f"Admin searching customers with filters: username={username}, active={active_status}")
        
        # Start with base query for customers
        query = Customer.query
        
        # Apply filters
        if username:
            query = query.filter(Customer.username.ilike(f'%{username}%'))
        if active_status is not None:
            is_active = active_status.lower() == 'true'
            query = query.filter(Customer.is_active == is_active)
        
        customers = query.all()
        logger.debug(f"Found {len(customers)} customers matching criteria")
        
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/users/<int:user_id>/documents', methods=['GET'])
@admin_required
def get_user_documents(user_id):
    """Get all documents for a specific user (professional)"""
    try:
        logger.debug(f"Admin requesting documents for user ID: {user_id}")
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"User ID {user_id} not found when requesting documents")
            return jsonify({'error': 'User not found'}), 404
        
        # Check if it's a professional
        if user.role != 'professional':
            logger.warning(f"User ID {user_id} is not a professional")
            return jsonify({'error': 'User is not a professional'}), 400
        
        # Get documents
        documents = Document.query.filter_by(professional_id=user_id).all()
        logger.debug(f"Found {len(documents)} documents for professional ID {user_id}")
        
        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        logger.error(f"Error getting documents for user {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/admin/documents/<int:document_id>/verify', methods=['PUT'])
@admin_required
def verify_document(document_id):
    """Verify or unverify a document"""
    try:
        logger.debug(f"Admin toggling verification for document ID: {document_id}")
        # Check if document exists
        document = Document.query.get(document_id)
        if not document:
            logger.warning(f"Document ID {document_id} not found")
            return jsonify({'error': 'Document not found'}), 404
        
        # Get request data
        data = request.get_json()
        verified = data.get('verified', True)
        
        # Update document verification status
        document.verified = verified
        logger.debug(f"Setting document {document_id} verification status to {verified}")
        
        # Get the professional
        professional = ServiceProfessional.query.get(document.professional_id)
        if professional:
            if verified:
                # If verifying, check if all documents are now verified
                all_docs = Document.query.filter_by(professional_id=professional.id).all()
                all_verified = all(doc.verified for doc in all_docs)
                
                if all_verified:
                    logger.info(f"All documents verified for professional ID {professional.id}")
                    professional.documents_verified = True
                else:
                    # Some documents still unverified
                    logger.info(f"Not all documents verified for professional ID {professional.id}")
                    professional.documents_verified = False
            else:
                # If unverifying, immediately set documents_verified to False
                logger.info(f"Document {document_id} unverified, setting professional {professional.id} documents_verified to False")
                professional.documents_verified = False
        
        db.session.commit()
        
        # Return updated document along with verification status
        return jsonify({
            'message': f'Document {verified and "verified" or "unverified"} successfully',
            'document': document.to_dict(),
            'all_verified': professional.documents_verified if professional else False
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating document verification {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

#=======================================================================
# ADMIN SERVICES MANAGEMENT
#=======================================================================

@routes_bp.route('/admin/services', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_services():
    """Manage services - list all or create new"""
    try:
        logger.debug(f"Admin services endpoint called: {request.method}")
        
        if request.method == 'GET':
            services = Service.query.all()
            logger.debug(f"Found {len(services)} services")
            # Return services directly without nesting under 'data'
            return jsonify([{
                'id': service.id,
                'name': service.name,
                'base_price': float(service.base_price),
                'description': service.description,
                'avg_duration': int(service.avg_duration),
                'status': service.status,
                'image_path': service.image_path
            } for service in services]), 200

        elif request.method == 'POST':
            # Check if multipart form data (file upload)
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle form data with possible file upload
                data = request.form
                logger.debug(f"Create service request form data: {data}")
            else:
                # Handle JSON data
                data = request.get_json()
                logger.debug(f"Create service request JSON data: {data}")
            
            # Validate required fields
            required_fields = ['name', 'base_price', 'description', 'avg_duration']
            if not all(field in data for field in required_fields):
                logger.warning("Missing required fields in service creation")
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required fields'
                }), 400

            # Validate data types and values
            if not data['name'] or len(data['name'].strip()) == 0:
                return jsonify({'status': 'error', 'message': 'Invalid name'}), 400
            
            try:
                base_price = float(data['base_price'])
                if base_price <= 0:
                    raise ValueError
            except ValueError:
                logger.warning(f"Invalid base price: {data.get('base_price')}")
                return jsonify({'status': 'error', 'message': 'Invalid base price'}), 400

            if not data['description']:
                return jsonify({'status': 'error', 'message': 'Invalid description'}), 400
            
            try:
                avg_duration = int(data['avg_duration'])
                if avg_duration <= 0:
                    raise ValueError
            except ValueError:
                logger.warning(f"Invalid avg_duration: {data.get('avg_duration')}")
                return jsonify({'status': 'error', 'message': 'Invalid average duration'}), 400

            # Handle image upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        # Make sure UPLOAD_FOLDER exists
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        
                        # Generate unique filename
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4()}_{filename}"
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        file.save(file_path)
                        # Save relative path to database
                        image_path = f"/static/service-images/{unique_filename}"
                        logger.info(f"Service image saved at: {image_path}")
                    except Exception as e:
                        logger.error(f"Error saving image: {str(e)}")
                        return jsonify({'status': 'error', 'message': f'Error saving image: {str(e)}'}), 500

            new_service = Service(
                name=data['name'],
                base_price=base_price,
                description=data['description'],
                avg_duration=avg_duration,
                status='active',  # Default to active
                image_path=image_path,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_service)
            db.session.commit()
            logger.info(f"Service created with ID: {new_service.id}, Name: {new_service.name}")
            
            # Return service data directly
            return jsonify({
                'id': new_service.id,
                'name': new_service.name,
                'base_price': float(new_service.base_price),
                'description': new_service.description,
                'avg_duration': int(new_service.avg_duration),
                'status': new_service.status,
                'image_path': new_service.image_path
            }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in admin services endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@routes_bp.route('/admin/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required
def service_detail(service_id):
    """Get, update or delete a specific service"""
    try:
        logger.debug(f"Admin service detail endpoint called: {request.method}, ID: {service_id}")
        service = Service.query.get_or_404(service_id)
        logger.debug(f"Found service: {service.name}")

        if request.method == 'GET':
            # Return service data directly
            return jsonify({
                'id': service.id, 
                'name': service.name,
                'base_price': float(service.base_price),
                'description': service.description,
                'avg_duration': int(service.avg_duration),
                'status': service.status,
                'image_path': service.image_path
            }), 200

        elif request.method == 'PUT':
            # Check if multipart form data (file upload)
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle file upload
                data = request.form
                logger.debug(f"Update service request form data: {data}")
                
                # Handle image upload if present
                if 'image' in request.files:
                    file = request.files['image']
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            # Make sure UPLOAD_FOLDER exists
                            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                            
                            # Delete old image if it exists
                            if service.image_path:
                                old_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                          service.image_path.lstrip('/'))
                                if os.path.exists(old_image_path):
                                    os.remove(old_image_path)
                                    logger.info(f"Deleted old service image: {old_image_path}")
                            
                            # Generate unique filename
                            filename = secure_filename(file.filename)
                            unique_filename = f"{uuid.uuid4()}_{filename}"
                            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                            file.save(file_path)
                            # Save relative path to database
                            service.image_path = f"/static/service-images/{unique_filename}"
                            logger.info(f"New service image saved at: {service.image_path}")
                        except Exception as e:
                            logger.error(f"Error handling image upload: {str(e)}")
                            return jsonify({'status': 'error', 'message': f'Error uploading image: {str(e)}'}), 500
                
                # Check if image should be removed
                if data.get('remove_image') == 'true' and service.image_path:
                    try:
                        # Delete the image file
                        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                              service.image_path.lstrip('/'))
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            logger.info(f"Deleted service image: {image_path}")
                        # Clear the image path
                        service.image_path = None
                    except Exception as e:
                        logger.error(f"Error removing image: {str(e)}")
            else:
                # Handle JSON data
                data = request.get_json()
                logger.debug(f"Update service request JSON data: {data}")
            
            # Update service fields
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
            if 'image_path' in data:
                service.image_path = data['image_path']

            service.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Service {service_id} updated successfully")
            
            # Return updated service data
            return jsonify({
                'id': service.id,
                'name': service.name,
                'base_price': float(service.base_price),
                'description': service.description,
                'avg_duration': int(service.avg_duration),
                'status': service.status,
                'image_path': service.image_path
            }), 200

        elif request.method == 'DELETE':
            logger.debug(f"Attempting to delete service {service_id}")
            
            # First check if service is associated with any active service requests
            active_requests = ServiceRequest.query.filter_by(
                service_id=service_id
            ).filter(
                ServiceRequest.status.in_(['requested', 'assigned'])
            ).first()
            
            if active_requests:
                logger.warning(f"Cannot delete service {service_id}: it has active requests")
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot delete service: it has active service requests'
                }), 422
            
            # Delete image if exists
            if service.image_path:
                try:
                    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                              service.image_path.lstrip('/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f"Deleted service image: {image_path}")
                except Exception as e:
                    logger.error(f"Failed to delete service image: {e}")
            
            # Delete the service
            db.session.delete(service)
            db.session.commit()
            logger.info(f"Service {service_id} deleted successfully")
            
            return jsonify({
                'status': 'success',
                'message': 'Service deleted successfully'
            }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in admin service detail endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@routes_bp.route('/admin/analytics/revenue', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_analytics():
    """Get revenue analytics for admin dashboard"""
    try:
        logger.debug("Admin requesting revenue analytics")
        # Calculate total revenue from completed service requests
        total_revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed'
        ).scalar() or 0.0
        
        # Calculate revenue growth (comparing current month to previous month)
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)  # First day of previous month
        
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
        
        logger.debug(f"Revenue analytics: total={total_revenue}, current month={current_month_revenue}, previous month={last_month_revenue}, growth={revenue_growth}%")
        return jsonify({
            'total_revenue': total_revenue,
            'current_month_revenue': current_month_revenue,
            'last_month_revenue': last_month_revenue,
            'revenue_growth': revenue_growth
        }), 200
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/services/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_services_stats():
    """Get service statistics for admin dashboard"""
    try:
        logger.debug("Admin requesting services statistics")
        total_active_services = Service.query.filter_by(status='active').count()
        
        # Calculate service growth
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)  # First day of previous month
        
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
        
        logger.debug(f"Service stats: active={total_active_services}, new this month={new_services}, previous month={old_services}, growth={service_growth}%")
        return jsonify({
            'total_active_services': total_active_services,
            'new_services_this_month': new_services,
            'services_last_month': old_services,
            'service_growth': service_growth
        }), 200
    except Exception as e:
        logger.error(f"Error getting service statistics: {str(e)}")
        return jsonify({'error': str(e)}), 422

@routes_bp.route('/admin/users/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_users_stats():
    """Get user statistics for admin dashboard"""
    try:
        logger.debug("Admin requesting user statistics")
        # Count professionals (excluding admins)
        total_professionals = User.query.filter_by(role='professional').count()
        
        # Count customers (excluding admins)
        total_customers = User.query.filter_by(role='customer').count()
        
        # Calculate user growth by role (comparing current month to previous month)
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)  # First day of previous month
        
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
        
        logger.debug(f"User stats: professionals={total_professionals} (growth={professional_growth}%), customers={total_customers} (growth={customer_growth}%)")
        return jsonify({
            'total_professionals': total_professionals,
            'professional_growth': professional_growth,
            'total_customers': total_customers,
            'customer_growth': customer_growth
        }), 200
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return jsonify({'error': str(e)}), 422

#=======================================================================
# PROFESSIONAL ROUTES
#=======================================================================
@routes_bp.route('/professional/profile', methods=['GET', 'PUT'])
@professional_required
def manage_profile():
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

@routes_bp.route('/professional/service-requests', methods=['GET'])
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

@routes_bp.route('/professional/service-requests/<int:request_id>', methods=['GET', 'PUT'])
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
        elif ((action == 'reject') and (service_request.status == 'assigned')):    
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

@routes_bp.route('/professional/stats', methods=['GET'])
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

@routes_bp.route('/professional/status/<int:user_id>', methods=['GET'])
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

#=======================================================================
# CUSTOMER ROUTES
#=======================================================================
@routes_bp.route('/customer/profile', methods=['GET', 'PUT'])
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

@routes_bp.route('/customer/service-requests', methods=['GET', 'POST'])
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

@routes_bp.route('/customer/service-requests/<int:request_id>', methods=['GET', 'PUT'])
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
        if service_request.status not in ['requested', 'assigned', 'inprogress']:
            logger.warning(f"Cannot modify request {request_id} in status {service_request.status}")
            return jsonify({
                'error': 'Cannot modify a service request that is already in progress or completed'
            }), 400
        
        # Handle cancellation
        if data.get('status') == 'cancelled':
            service_request.status = 'cancelled'
            service_request.cancelled_on = datetime.utcnow()
            service_request.cancelled_by = 'customer'
            logger.info(f"Customer {current_user_id} cancelled request {request_id}")
        
        # Update service if provided and status is still 'requested'
        if data.get('service_id') and service_request.status == 'requested':
            service_request.service_id = data.get('service_id')
            logger.info(f"Customer {current_user_id} changed service for request {request_id} to {data.get('service_id')}")
        
        db.session.commit()
        return jsonify({'message': 'Service request updated successfully'}), 200

@routes_bp.route('/customer/service-history', methods=['GET'])
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

@routes_bp.route('/customer/service-requests/<int:request_id>/review', methods=['GET', 'POST'])
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

@routes_bp.route('/customer/service-stats', methods=['GET'])
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

#=======================================================================
# PUBLIC ROUTES (No authentication required)
#=======================================================================

@routes_bp.route('/services', methods=['GET'])
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

@routes_bp.route('/services/available', methods=['GET'])
def get_available_services():
    """Get all active services that professionals can register for"""
    try:
        logger.debug("Getting available services for registration")
        services = Service.query.filter_by(status='active').all()
        logger.debug(f"Found {len(services)} active services")
        return jsonify([{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'avg_duration': service.avg_duration,
            'image_path': service.image_path
        } for service in services]), 200
    except Exception as e:
        logger.error(f"Error getting available services: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/services/status', methods=['GET'])
def check_service_status():
    """Check which services are available for registration"""
    try:
        logger.debug("Checking service availability status")
        active_services = Service.query.filter_by(status='active').count()
        total_services = Service.query.count()
        logger.debug(f"Service status: {active_services}/{total_services} services active")
        return jsonify({
            'active_services': active_services,
            'total_services': total_services,
            'status': 'ok' if active_services > 0 else 'no_services'
        }), 200
    except Exception as e:
        logger.error(f"Error checking service status: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@routes_bp.route('/services/search', methods=['GET'])
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

@routes_bp.route('/professionals/<int:professional_id>', methods=['GET'])
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
    ).all()
    
    reviews_list = []
    for request in completed_requests:
        review = Review.query.filter_by(request_id=request.id).first()
        if review:
            reviews_list.append({
                'rating': review.rating,
                'comment': review.comment,
                'customer_name': review.request.customer.full_name if review.request.customer else 'Unknown Customer',
                'created_at': review.created_at.isoformat(),
                'service_name': request.service.name if request.service else 'Unknown Service'
            })
    
    # Create response with professional data and reviews
    result = professional.to_dict()
    result['reviews'] = reviews_list
    logger.debug(f"Found {len(reviews_list)} reviews for professional {professional_id}")
    
    return jsonify(result), 200

@routes_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document_file(document_id):
    """Get a document file by ID (requires authentication)"""
    try:
        logger.debug(f"Getting document file for document ID: {document_id}")
        # Get the document
        document = Document.query.get(document_id)
        if not document:
            logger.warning(f"Document {document_id} not found")
            return jsonify({'error': 'Document not found'}), 404
        
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check permissions - only owner or admin can view documents
        if current_user.role != 'admin' and document.professional_id != current_user_id:
            logger.warning(f"User {current_user_id} attempted to access document {document_id} without permission")
            return jsonify({'error': 'You do not have permission to view this document'}), 403
        
        # Check if file exists
        if not os.path.exists(document.file_path):
            logger.warning(f"Document file not found at path: {document.file_path}")
            return jsonify({'error': 'Document file not found'}), 404
        
        # Get file extension
        file_extension = document.filename.split('.')[-1].lower()
        # Set appropriate MIME type
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        mime_type = mime_types.get(file_extension, 'application/octet-stream')
        
        logger.debug(f"Serving document {document_id} as {mime_type} (inline)")
        # Return the file with inline content disposition to open in browser
        response = send_file(document.file_path, mimetype=mime_type, as_attachment=False)
        response.headers['Content-Disposition'] = f'inline; filename="{document.filename}"'
        return response
    except Exception as e:
        logger.error(f"Error getting document file {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/services/<int:service_id>/professionals', methods=['GET'])
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