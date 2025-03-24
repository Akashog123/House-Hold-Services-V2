# HouseCare API Documentation

This document provides comprehensive documentation for the HouseCare backend API, which can be used to implement the Vue.js frontend.

## API Base URL

All API endpoints are relative to the base URL: `http://localhost:5000/`

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the `Authorization` header with the format: `Bearer <token>`

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required | 
|--------|----------|-------------|--------------|
| POST | `/auth/login` | User login | No |
| POST | `/auth/register` | Register new user | No |
| GET | `/auth/profile` | Get current user profile | Yes |
| POST | `/auth/refresh` | Refresh authentication token | Yes |

#### Login Request Example
```json
{
  "userInput": "your_username_or_email",
  "password": "your_password"
}
```

#### Login Response Example
```json
{
  "token": "eyJ0eXAiOiJKV...",
  "user": {
    "id": 1,
    "username": "username",
    "email": "user@example.com",
    "role": "customer",
    "is_approved": true,
    "is_active": true
  }
}
```

#### Professional Registration Request Example (Multipart Form Data)

Form fields:
- `username`: "pro_user"
- `email`: "pro@example.com"
- `password`: "secure_password"
- `role`: "professional"
- `fullName`: "John Smith"
- `phoneNumber`: "555-123-4567"
- `serviceTypeId`: "1"
- `description`: "Experienced plumber with 10 years in residential repairs"
- `experienceYears`: "10"
- `idProof`: (file upload)
- `addressProof`: (file upload)
- `qualification`: (file upload, optional)

#### Professional Registration Request Example (JSON)
```json
{
  "username": "pro_user",
  "email": "pro@example.com",
  "password": "secure_password",
  "role": "professional",
  "fullName": "John Smith",
  "phoneNumber": "555-123-4567",
  "serviceTypeId": 1,
  "description": "Experienced plumber with 10 years in residential repairs",
  "experienceYears": 10
}
```

#### Customer Registration Request Example (Multipart Form Data)

Form fields:
- `username`: "customer_user"
- `email`: "customer@example.com"
- `password`: "secure_password"
- `role`: "customer"
- `fullName`: "Jane Doe"
- `phoneNumber`: "555-123-4567"
- `address`: "123 Main St, Apt 4B"
- `pinCode`: "12345"

#### Customer Registration Request Example (JSON)
```json
{
  "username": "customer_user",
  "email": "customer@example.com",
  "password": "secure_password",
  "role": "customer",
  "fullName": "Jane Doe",
  "address": "123 Main St, Apt 4B",
  "pinCode": "12345",
  "phoneNumber": "555-123-4567"
}
```

#### Registration Response Example
```json
{
  "message": "User registered successfully",
  "approval_required": false,
  "user_id": 1,
  "role": "customer"
}
```

## Admin Routes

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/admin/users` | Get all users | Admin |
| GET | `/admin/professionals` | Get all professionals | Admin |
| GET | `/admin/professionals/details` | Get detailed info about professionals | Admin |
| GET | `/admin/customers` | Get all customers | Admin |
| PUT | `/admin/approve/{user_id}` | Approve a user | Admin |
| PUT | `/admin/reject/{user_id}` | Reject a user | Admin |
| PUT | `/admin/block/{user_id}` | Block a user | Admin |
| PUT | `/admin/unblock/{user_id}` | Unblock a user | Admin |
| GET | `/admin/search-professionals` | Search professionals | Admin |
| GET | `/admin/search-customers` | Search customers | Admin |
| GET | `/admin/users/{user_id}/documents` | Get user documents | Admin |
| PUT | `/admin/documents/{document_id}/verify` | Verify a document | Admin |

#### Professionals Details Response Example
```json
[
  {
    "id": 1,
    "username": "pro_user",
    "email": "pro@example.com",
    "full_name": "John Smith",
    "phone_number": "555-123-4567",
    "service_type_id": 1,
    "service_name": "Plumbing",
    "is_approved": true,
    "is_active": true,
    "documents_count": 3,
    "documents_verified": true,
    "average_rating": 4.8,
    "total_reviews": 12
  }
]
```

#### Search Professionals Query Parameters
- `username`: Filter by username (partial match)
- `approved`: Filter by approval status (true/false)
- `active`: Filter by active status (true/false)

#### Search Customers Query Parameters
- `username`: Filter by username (partial match)
- `active`: Filter by active status (true/false)

#### Verify Document Request
```json
{
  "verified": true
}
```

### Service Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/admin/services` | Get all services | Admin |
| POST | `/admin/services` | Create a new service | Admin |
| GET | `/admin/services/{service_id}` | Get service details | Admin |
| PUT | `/admin/services/{service_id}` | Update a service | Admin |
| DELETE | `/admin/services/{service_id}` | Delete a service | Admin |

#### Create Service Request Example
```json
{
  "name": "House Cleaning",
  "base_price": 75.00,
  "description": "Complete house cleaning service",
  "avg_duration": 120
}
```

#### Create/Update Service Response Example
```json
{
  "id": 1,
  "name": "House Cleaning",
  "base_price": 75.00,
  "description": "Complete house cleaning service",
  "avg_duration": 120,
  "status": "active"
}
```

#### Delete Service Response Example
```json
{
  "status": "success",
  "message": "Service deleted successfully"
}
```

### Admin Analytics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/admin/analytics/revenue` | Get revenue analytics | Admin |
| GET | `/admin/services/stats` | Get service statistics | Admin |
| GET | `/admin/users/stats` | Get user statistics | Admin |

#### Revenue Analytics Response Example
```json
{
  "total_revenue": 15750.0,
  "current_month_revenue": 3500.0,
  "last_month_revenue": 2800.0,
  "revenue_growth": 25.0
}
```

#### Services Stats Response Example
```json
{
  "total_active_services": 12,
  "new_services_this_month": 3,
  "services_last_month": 2,
  "service_growth": 50.0
}
```

#### User Stats Response Example
```json
{
  "total_professionals": 25,
  "professional_growth": 20.0,
  "total_customers": 150,
  "customer_growth": 15.0
}
```

## Professional Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/professional/profile` | Get professional's profile | Professional |
| PUT | `/professional/profile` | Update professional's profile | Professional |
| GET | `/professional/service-requests` | Get available/assigned service requests | Professional |
| GET | `/professional/service-requests/{request_id}` | Get service request details | Professional |
| PUT | `/professional/service-requests/{request_id}` | Update service request status | Professional |
| GET | `/professional/stats` | Get professional statistics | Professional |

#### Update Profile Request Example
```json
{
  "email": "new.email@example.com",
  "phone_number": "555-987-6543",
  "description": "Updated professional description with new skills"
}
```

#### Service Requests Response Example
```json
[
  {
    "id": 1,
    "service_id": 2,
    "service_name": "House Cleaning",
    "customer_id": 5,
    "customer_name": "customer_user",
    "status": "requested",
    "request_date": "2023-05-20T14:30:00",
    "completion_date": null,
    "is_assigned_to_me": false
  }
]
```

#### Update Request Status Request Example
```json
{
  "action": "accept"
}
```

#### Professional Stats Response Example
```json
{
  "completed": 15,
  "active": 3,
  "rating": 4.8,
  "totalEarnings": "$1,425.00"
}
```

## Customer Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/customer/profile` | Get customer's profile | Customer |
| PUT | `/customer/profile` | Update customer's profile | Customer |
| GET | `/customer/service-requests` | Get all customer's service requests | Customer |
| POST | `/customer/service-requests` | Create a new service request | Customer |
| GET | `/customer/service-requests/{request_id}` | Get service request details | Customer |
| PUT | `/customer/service-requests/{request_id}` | Update/cancel service request | Customer |
| PUT | `/customer/service-requests/{request_id}/complete` | Mark service as completed | Customer |
| GET | `/customer/service-history` | Get service history | Customer |
| GET | `/customer/service-requests/{request_id}/review` | Get review for a service | Customer |
| POST | `/customer/service-requests/{request_id}/review` | Submit review for a service | Customer |
| GET | `/customer/service-stats` | Get service statistics | Customer |

#### Update Profile Request Example
```json
{
  "email": "new.email@example.com",
  "phone_number": "555-987-6543",
  "address": "456 Park Ave, Suite 789",
  "pin_code": "54321"
}
```

#### Create Service Request Request Example
```json
{
  "service_id": 1,
  "notes": "Please clean the whole house including bathroom"
}
```

#### Create Service Request Response Example
```json
{
  "message": "Service request created successfully",
  "request_id": 12
}
```

#### Update/Cancel Service Request Example
```json
{
  "status": "cancelled"
}
```

#### Submit Review Request Example
```json
{
  "rating": 5,
  "comment": "Excellent service, very thorough cleaning!"
}
```

#### Customer Stats Response Example
```json
{
  "totalRequests": 8,
  "completedRequests": 5,
  "pendingRequests": 2,
  "totalSpent": 575.0
}
```

## Public Routes (No Authentication Required)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/services` | Get all active services | No |
| GET | `/services/available` | Get services available for registration | No |
| GET | `/services/status` | Check service availability status | No |
| GET | `/services/search` | Search services with location filter | No |
| GET | `/professionals/{professional_id}` | Get professional profile with reviews | No |

#### Service Search Query Parameters
- `name`: Filter by service name (partial match)
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price
- `pin_code`: Filter by location pin code (for finding professionals)

#### Services Status Response Example
```json
{
  "active_services": 8,
  "total_services": 12,
  "status": "ok"
}
```

#### Search Services Response (with pin_code) Example
```json
[
  {
    "id": 1,
    "name": "House Cleaning",
    "base_price": 75.00,
    "description": "Complete house cleaning service",
    "avg_duration": 120,
    "available_professionals": 3
  }
]
```

#### Professional Profile Response Example
```json
{
  "id": 1,
  "username": "pro_user",
  "email": "pro@example.com",
  "full_name": "John Smith",
  "phone_number": "555-123-4567",
  "service_type_id": 1,
  "is_approved": true,
  "is_active": true,
  "description": "Experienced plumber with 10 years in residential repairs",
  "experience_years": 10,
  "average_rating": 4.8,
  "total_reviews": 12,
  "reviews": [
    {
      "rating": 5,
      "comment": "Excellent work fixing my bathroom sink!",
      "created_at": "2023-05-20T14:30:00",
      "service_name": "Plumbing"
    }
  ]
}
```

## Document Access

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/documents/{document_id}` | Get document file | Yes (Owner or Admin) |

## Error Handling

All endpoints return appropriate HTTP status codes:

- 200: Success
- 201: Created successfully
- 400: Bad request/validation error
- 401: Unauthorized
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 422: Unprocessable entity
- 500: Server error

#### Error Response Example
```json
{
  "error": "User not found"
}
```

## Data Models

### User
- id: Integer (Primary Key)
- username: String (Unique)
- email: String (Unique)
- password_hash: String
- role: String ('admin', 'professional', 'customer')
- is_approved: Boolean
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime

### ServiceProfessional (extends User)
- All User fields
- full_name: String
- phone_number: String
- description: Text
- service_type_id: Integer (Foreign Key to Service)
- experience_years: Integer
- average_rating: Float
- total_reviews: Integer
- documents_verified: Boolean

### Customer (extends User)
- All User fields
- full_name: String
- phone_number: String
- address: String
- pin_code: String

### Service
- id: Integer (Primary Key)
- name: String
- base_price: Float
- description: Text
- avg_duration: Integer (minutes)
- status: String ('active', 'inactive')
- created_at: DateTime
- updated_at: DateTime

### ServiceRequest
- id: Integer (Primary Key)
- service_id: Integer (Foreign Key)
- customer_id: Integer (Foreign Key)
- pro_id: Integer (Foreign Key, nullable)
- status: String ('requested', 'assigned', 'completed', 'cancelled')
- notes: Text (nullable)
- request_date: DateTime
- completion_date: DateTime (nullable)

### Review
- id: Integer (Primary Key)
- request_id: Integer (Foreign Key)
- rating: Integer
- comment: Text
- created_at: DateTime

### Document
- id: Integer (Primary Key)
- professional_id: Integer (Foreign Key)
- document_type: String
- filename: String
- file_path: String
- verified: Boolean
- uploaded_at: DateTime