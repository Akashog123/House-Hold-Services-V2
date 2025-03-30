from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators import admin_required
from .models import db, User, ServiceProfessional, Document, Service, ServiceRequest, Customer, Review
from datetime import datetime
from sqlalchemy import func
from datetime import timedelta
import os
import logging
from werkzeug.utils import secure_filename
import uuid
from celery.result import AsyncResult

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'service-images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/professionals', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/professionals/details', methods=['GET'])
@jwt_required()
@admin_required
def get_professionals_details():
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

@admin_bp.route('/admin/customers', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/approve/<int:user_id>', methods=['PUT'])
@jwt_required()
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

@admin_bp.route('/admin/reject/<int:user_id>', methods=['PUT'])
@jwt_required()
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

@admin_bp.route('/admin/block/<int:user_id>', methods=['PUT'])
@jwt_required()
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

@admin_bp.route('/admin/unblock/<int:user_id>', methods=['PUT'])
@jwt_required()
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

@admin_bp.route('/admin/search-professionals', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/search-customers', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/users/<int:user_id>/documents', methods=['GET'])
@jwt_required()
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

@admin_bp.route('/admin/documents/<int:document_id>/verify', methods=['PUT'])
@jwt_required()
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

@admin_bp.route('/admin/services', methods=['GET', 'POST'])
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

@admin_bp.route('/admin/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required
def service_detail(service_id):
    """Get, update or delete a specific service"""
    try:
        logger.debug(f"Admin service detail endpoint called: {request.method}, ID: {service_id}")
        service = Service.query.get_or_404(service_id)
        logger.debug(f"Found service: {service.name}")

        if request.method == 'GET':
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
                data = request.form
                logger.debug(f"Update service request form data: {data}")

                if 'image' in request.files:
                    file = request.files['image']
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                            if service.image_path:
                                old_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                          service.image_path.lstrip('/'))
                                if os.path.exists(old_image_path):
                                    os.remove(old_image_path)
                                    logger.info(f"Deleted old service image: {old_image_path}")

                            filename = secure_filename(file.filename)
                            unique_filename = f"{uuid.uuid4()}_{filename}"
                            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                            file.save(file_path)
                            service.image_path = f"/static/service-images/{unique_filename}"
                            logger.info(f"New service image saved at: {service.image_path}")
                        except Exception as e:
                            logger.error(f"Error handling image upload: {str(e)}")
                            return jsonify({'status': 'error', 'message': f'Error uploading image: {str(e)}'}), 500
                
                if data.get('remove_image') == 'true' and service.image_path:
                    try:
                        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                              service.image_path.lstrip('/'))
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            logger.info(f"Deleted service image: {image_path}")
                        service.image_path = None
                    except Exception as e:
                        logger.error(f"Error removing image: {str(e)}")
            else:
                data = request.get_json()
                logger.debug(f"Update service request JSON data: {data}")
  
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
 
            if service.image_path:
                try:
                    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                              service.image_path.lstrip('/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f"Deleted service image: {image_path}")
                except Exception as e:
                    logger.error(f"Failed to delete service image: {e}")

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

@admin_bp.route('/admin/analytics/revenue', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_analytics():
    """Get revenue analytics for admin dashboard"""
    try:
        logger.debug("Admin requesting revenue analytics")
        total_revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed'
        ).scalar() or 0.0

        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)
        
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

@admin_bp.route('/admin/services/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_services_stats():
    """Get service statistics for admin dashboard"""
    try:
        logger.debug("Admin requesting services statistics")
        total_active_services = Service.query.filter_by(status='active').count()
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)
        
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

@admin_bp.route('/admin/users/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_users_stats():
    """Get user statistics for admin dashboard"""
    try:
        logger.debug("Admin requesting user statistics")
        total_professionals = User.query.filter(User.user_type == 'professional').count()
        total_customers = User.query.filter(User.user_type == 'customer').count()
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        last_month = last_month.replace(day=1)

        new_professionals = User.query.filter(
            User.created_at >= current_month,
            User.user_type == 'professional'
        ).count()
        
        old_professionals = User.query.filter(
            User.created_at >= last_month,
            User.created_at < current_month,
            User.user_type == 'professional'
        ).count()
        
        professional_growth = 0
        if old_professionals > 0:
            professional_growth = ((new_professionals - old_professionals) / old_professionals) * 100

        new_customers = User.query.filter(
            User.created_at >= current_month,
            User.user_type == 'customer'
        ).count()
        
        old_customers = User.query.filter(
            User.created_at >= last_month,
            User.created_at < current_month,
            User.user_type == 'customer'
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

@admin_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_document_file(document_id):
    """Get a document file by ID (requires authentication)"""
    try:
        logger.debug(f"Getting document file for document ID: {document_id}")
        document = Document.query.get(document_id)
        if not document:
            logger.warning(f"Document {document_id} not found")
            return jsonify({'error': 'Document not found'}), 404
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin' and document.professional_id != current_user_id:
            logger.warning(f"User {current_user_id} attempted to access document {document_id} without permission")
            return jsonify({'error': 'You do not have permission to view this document'}), 403
        
        if not os.path.exists(document.file_path):
            logger.warning(f"Document file not found at path: {document.file_path}")
            return jsonify({'error': 'Document file not found'}), 404
        file_extension = document.filename.split('.')[-1].lower()

        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        mime_type = mime_types.get(file_extension, 'application/octet-stream')
        
        logger.debug(f"Serving document {document_id} as {mime_type} (inline)")
        response = send_file(document.file_path, mimetype=mime_type, as_attachment=False)
        response.headers['Content-Disposition'] = f'inline; filename="{document.filename}"'
        return response
    except Exception as e:
        logger.error(f"Error getting document file {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/export-service-requests', methods=['GET'])
@jwt_required()
@admin_required
def export_service_requests():
    """Trigger CSV export for completed service requests and alert admin"""
    try:
        from backend.celery.tasks import export_service_requests_csv
        task = export_service_requests_csv.delay()
        result = AsyncResult(task.id)
        if result.ready:
            return jsonify({'message': 'CSV export task completed'}), 200
        logger.info(f"CSV export task triggered with ID: {task.id}")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/analytics/revenue/<string:timeframe>', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_analytics_timeframe(timeframe):
    """Get revenue analytics for given timeframe (week, month or year)"""
    try:
        from datetime import timedelta
        now = datetime.utcnow()
        if timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)
        elif timeframe == 'year':
            start_date = now - timedelta(days=365)
        else:
            return jsonify({'error': 'Invalid timeframe'}), 400

        revenue = db.session.query(
            func.sum(Service.base_price)
        ).join(ServiceRequest).filter(
            ServiceRequest.status == 'completed',
            ServiceRequest.completion_date >= start_date
        ).scalar() or 0.0
        return jsonify({
            'timeframe': timeframe,
            'revenue': revenue,
            'labels': [f"Since {start_date.date()}"],
            'data': [revenue]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 422

@admin_bp.route('/admin/analytics/user-growth', methods=['GET'])
@jwt_required()
@admin_required
def get_user_growth_analytics():
    """Return basic user growth analytics"""
    try:
        total_customers = User.query.filter_by(user_type='customer').count()
        total_professionals = User.query.filter_by(user_type='professional').count()
        # Dummy data for labels and growth over time
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        customerData = [int(total_customers/4)] * 4
        professionalData = [int(total_professionals/4)] * 4

        return jsonify({
            'labels': labels,
            'customerData': customerData,
            'professionalData': professionalData
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 422

@admin_bp.route('/admin/analytics/services-usage', methods=['GET'])
@jwt_required()
@admin_required
def get_services_usage_analytics():
    """Return basic services usage analytics"""
    try:
        services = Service.query.all()
        labels = []
        data = []
        for service in services:
            labels.append(service.name)
            c = ServiceRequest.query.filter(
                ServiceRequest.service_id == service.id,
                ServiceRequest.status=='completed'
            ).count()
            data.append(c)
        return jsonify({
            'labels': labels,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 422

@admin_bp.route('/admin/professionals/<int:professional_id>/reviews', methods=['GET'])
@jwt_required()
@admin_required
def get_professional_reviews(professional_id):
    """Fetch reviews and average rating for a professional with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        # Join Review with ServiceRequest filtering by pro_id
        query = Review.query.join(ServiceRequest, Review.request_id == ServiceRequest.id
                    ).filter(ServiceRequest.pro_id == professional_id)
        total_reviews = query.count()
        average_rating = query.with_entities(func.avg(Review.rating)).scalar() or 0.0
        reviews = query.order_by(Review.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
        reviews_list = [{
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in reviews]
        return jsonify({
            'averageRating': average_rating,
            'totalReviews': total_reviews,
            'reviews': reviews_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500