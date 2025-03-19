# HouseCare API Documentation

This document provides comprehensive documentation for the HouseCare backend API, which can be used to implement the Vue.js frontend.

## API Base URL

All API endpoints are relative to the base URL: `http://localhost:5000/`

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the `Authorization` header with the format:

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required | 
|--------|----------|-------------|--------------|
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/register` | Register new user | No |
| GET | `/api/auth/profile` | Get current user profile | Yes |

#### Login Request Example
```json
{
  "username": "your_username",
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
    "role": "customer",
    "is_approved": true,
    "is_active": true,
    "created_at": "2023-05-20T14:30:00"
  }
}
```

#### Professional Registration Request Example
```json
{
  "username": "pro_user",
  "password": "secure_password",
  "role": "professional",
  "full_name": "John Smith",
  "description": "Experienced plumber with 10 years in residential repairs",
  "service_type_id": 1,
  "experience_years": 10
}
```

#### Customer Registration Request Example
```json
{
  "username": "customer_user",
  "password": "secure_password",
  "role": "customer",
  "full_name": "Jane Doe",
  "address": "123 Main St, Apt 4B",
  "pin_code": "12345",
  "phone_number": "555-123-4567"
}
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": {}, // Response data object
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description"
}
```

## User Management (Admin Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/admin/users` | Get all users | Admin |
| GET | `/api/admin/professionals` | Get all professionals | Admin |
| GET | `/api/admin/customers` | Get all customers | Admin |
| PUT | `/api/admin/approve/{user_id}` | Approve a user | Admin |
| PUT | `/api/admin/reject/{user_id}` | Reject a user | Admin |
| PUT | `/api/admin/block/{user_id}` | Block a user | Admin |
| PUT | `/api/admin/unblock/{user_id}` | Unblock a user | Admin |
| GET | `/api/admin/search-professionals` | Search professionals | Admin |
| GET | `/api/admin/search-customers` | Search customers | Admin |

### Search Professionals Query Parameters

- `username`: Filter by username (partial match)
- `approved`: Filter by approval status (true/false)
- `active`: Filter by active status (true/false)

### Search Customers Query Parameters

- `username`: Filter by username (partial match)
- `active`: Filter by active status (true/false)

## Service Management (Admin Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/admin/services` | Get all services | Admin |
| POST | `/api/admin/services` | Create a new service | Admin |
| GET | `/api/admin/services/{service_id}` | Get service details | Admin |
| PUT | `/api/admin/services/{service_id}` | Update a service | Admin |
| DELETE | `/api/admin/services/{service_id}` | Delete a service | Admin |

### Get All Services Response Example
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "House Cleaning",
      "base_price": 75.00,
      "description": "Complete house cleaning service",
      "avg_duration": 120
    }
  ]
}
```

### Create Service Request Example
```json
{
  "name": "House Cleaning",
  "base_price": 75.00,
  "description": "Complete house cleaning service",
  "avg_duration": 120
}
```

### Create Service Response Example
```json
{
  "status": "success",
  "message": "Service created successfully",
  "data": {
    "id": 1,
    "name": "House Cleaning",
    "base_price": 75.00,
    "description": "Complete house cleaning service",
    "avg_duration": 120
  }
}
```

### Update Service Response Example
```json
{
  "status": "success",
  "message": "Service updated successfully",
  "data": {
    "id": 1,
    "name": "House Cleaning",
    "base_price": 75.00,
    "description": "Complete house cleaning service",
    "avg_duration": 120
  }
}
```

### Delete Service Response Example
```json
{
  "status": "success",
  "message": "Service deleted successfully"
}
```

## Services (Public)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/services` | Get available services | No |
| GET | `/api/services/search` | Search services by name and location | No |
| GET | `/api/professionals/{professional_id}` | Get professional profile with reviews | No |

### Service Search Query Parameters

- `name`: Filter by service name (partial match)
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price
- `pin_code`: Filter by location pin code

## Customer Service Requests

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/customer/service-requests` | Get all customer requests | Customer |
| POST | `/api/customer/service-requests` | Create a service request | Customer |
| GET | `/api/customer/service-requests/{request_id}` | Get request details | Customer |
| PUT | `/api/customer/service-requests/{request_id}` | Update a request | Customer |
| PUT | `/api/customer/service-requests/{request_id}/complete` | Mark service as completed | Customer |
| GET | `/api/customer/service-history` | Get service history | Customer |
| GET | `/api/customer/service-stats` | Get service statistics | Customer |

#### Create Service Request Example
```json
{
  "service_id": 1,
  "notes": "Please clean the whole house including bathroom"
}
```

#### Update Service Request Example
```json
{
  "status": "cancelled"
}
```

## Service Reviews

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/customer/service-requests/{request_id}/review` | Get review for a service | Customer |
| POST | `/api/customer/service-requests/{request_id}/review` | Create review for a service | Customer |

#### Create Review Request Example
```json
{
  "rating": 5,
  "comment": "Excellent service, very thorough cleaning!"
}
```

## Professional Service Requests

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/professional/service-requests` | Get available service requests | Professional |
| GET | `/api/professional/service-requests/{request_id}` | Get request details | Professional |
| PUT | `/api/professional/service-requests/{request_id}` | Update request status | Professional |
| GET | `/api/professional/stats` | Get professional statistics | Professional |


#### Update Request Status Example
```json
{
  "action": "accept"  // or "reject", "complete"
}
```

#### Data Models

## User
- id: Integer (Primary Key)
- username: String (Unique)
- password_hash: String
- is_approved: Boolean
- is_active: Boolean
- created_at: DateTime
- user_type: String ('admin', 'professional', 'customer')

## Service Professional (extends User)
- All User fields
- full_name: String
- description: Text
- service_type_id: Integer (Foreign Key to Service)
- experience_years: Integer
- average_rating: Float
- total_reviews: Integer

## Customer (extends User)
- All User fields
- full_name: String
- address: String
- pin_code: String
- phone_number: String

## Service
- id: Integer (Primary Key)
- name: String
- base_price: Float
- description: Text
- avg_duration: Integer (minutes)

## ServiceRequest
- id: Integer (Primary Key)
- service_id: Integer (Foreign Key)
- customer_id: Integer (Foreign Key)
- pro_id: Integer (Foreign Key, nullable)
- status: String ('requested', 'assigned', 'completed', 'cancelled')
- request_date: DateTime
- completion_date: DateTime (nullable)
- notes: Text (nullable)

## Review
- id: Integer (Primary Key)
- request_id: Integer (Foreign Key)
- rating: Integer
- comment: Text
- created_at: DateTime

#### Status Codes
- 200: Success
- 201: Created successfully
- 400: Bad request/validation error
- 401: Unauthorized
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 500: Server error

#### Error Response Example
```json
{
  "error": "User not found"
}
```