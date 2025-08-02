# Accounts API Documentation

This document describes the authentication and user management API endpoints for the Brokerage Platform.

## Overview

The accounts system provides:
- User registration and authentication
- Profile management
- Password management
- Admin user management
- Token-based authentication

## API Endpoints

### Authentication

#### Register User
- **URL**: `POST /api/accounts/register/`
- **Description**: Register a new user account
- **Request Body**:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "builder",
    "phone_number": "+1234567890",
    "company_name": "Doe Construction",
    "license_number": "LIC123456",
    "website": "https://doeconstruction.com",
    "profile": {
        "address": "123 Main St",
        "city": "Toronto",
        "state": "ON",
        "zip_code": "M5V 3A8",
        "country": "Canada",
        "business_description": "Professional construction services",
        "years_in_business": 10
    }
}
```
- **Response**:
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "user_type": "builder",
        "phone_number": "+1234567890",
        "company_name": "Doe Construction",
        "license_number": "LIC123456",
        "website": "https://doeconstruction.com",
        "is_verified": false,
        "is_active": true,
        "profile": {...},
        "created_at": "2024-01-01T00:00:00Z"
    },
    "token": "your-auth-token-here"
}
```

#### Login
- **URL**: `POST /api/accounts/login/`
- **Description**: Authenticate user and get token
- **Request Body**:
```json
{
    "email": "john@example.com",
    "password": "securepassword123"
}
```
- **Response**:
```json
{
    "message": "Login successful",
    "user": {...},
    "token": "your-auth-token-here"
}
```

#### Logout
- **URL**: `POST /api/accounts/logout/`
- **Description**: Logout user and invalidate token
- **Headers**: `Authorization: Token your-auth-token-here`
- **Response**:
```json
{
    "message": "Logout successful"
}
```

### User Profile

#### Get Current User
- **URL**: `GET /api/accounts/current-user/`
- **Description**: Get current authenticated user
- **Headers**: `Authorization: Token your-auth-token-here`
- **Response**:
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "user_type": "builder",
    "phone_number": "+1234567890",
    "company_name": "Doe Construction",
    "license_number": "LIC123456",
    "website": "https://doeconstruction.com",
    "is_verified": false,
    "is_active": true,
    "profile": {...},
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get/Update Profile
- **URL**: `GET/PUT/PATCH /api/accounts/profile/`
- **Description**: Get or update current user profile
- **Headers**: `Authorization: Token your-auth-token-here`
- **Request Body** (for updates):
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "company_name": "Doe Construction",
    "license_number": "LIC123456",
    "website": "https://doeconstruction.com",
    "profile": {
        "address": "123 Main St",
        "city": "Toronto",
        "state": "ON",
        "zip_code": "M5V 3A8",
        "country": "Canada",
        "business_description": "Professional construction services",
        "years_in_business": 10,
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "email_notifications": true,
        "sms_notifications": false
    }
}
```

### Password Management

#### Change Password
- **URL**: `POST /api/accounts/password/change/`
- **Description**: Change user password
- **Headers**: `Authorization: Token your-auth-token-here`
- **Request Body**:
```json
{
    "old_password": "currentpassword",
    "new_password": "newsecurepassword123",
    "new_password_confirm": "newsecurepassword123"
}
```
- **Response**:
```json
{
    "message": "Password changed successfully",
    "token": "new-auth-token-here"
}
```

#### Request Password Reset
- **URL**: `POST /api/accounts/password/reset/`
- **Description**: Request password reset email
- **Request Body**:
```json
{
    "email": "john@example.com"
}
```
- **Response**:
```json
{
    "message": "Password reset email sent successfully"
}
```

#### Confirm Password Reset
- **URL**: `POST /api/accounts/password/reset/confirm/`
- **Description**: Confirm password reset with token
- **Request Body**:
```json
{
    "token": "reset-token-here",
    "new_password": "newsecurepassword123",
    "new_password_confirm": "newsecurepassword123"
}
```
- **Response**:
```json
{
    "message": "Password reset successfully"
}
```

### Admin User Management (Admin Only)

#### List Users
- **URL**: `GET /api/accounts/users/`
- **Description**: List all users (admin only)
- **Headers**: `Authorization: Token admin-token-here`
- **Query Parameters**:
  - `user_type`: Filter by user type (builder, agent, admin)
  - `is_verified`: Filter by verification status
  - `is_active`: Filter by active status
  - `search`: Search in username, email, name, company
- **Response**:
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "user_type": "builder",
            "company_name": "Doe Construction",
            "is_verified": false,
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get User Details
- **URL**: `GET /api/accounts/users/{id}/`
- **Description**: Get specific user details (admin only)
- **Headers**: `Authorization: Token admin-token-here`

#### Update User
- **URL**: `PUT/PATCH /api/accounts/users/{id}/`
- **Description**: Update specific user (admin only)
- **Headers**: `Authorization: Token admin-token-here`

#### Delete User
- **URL**: `DELETE /api/accounts/users/{id}/`
- **Description**: Delete specific user (admin only)
- **Headers**: `Authorization: Token admin-token-here`

#### Verify User
- **URL**: `POST /api/accounts/users/{id}/verify/`
- **Description**: Verify a user account (admin only)
- **Headers**: `Authorization: Token admin-token-here`
- **Response**:
```json
{
    "message": "User verified successfully"
}
```

#### Deactivate User
- **URL**: `POST /api/accounts/users/{id}/deactivate/`
- **Description**: Deactivate a user account (admin only)
- **Headers**: `Authorization: Token admin-token-here`
- **Response**:
```json
{
    "message": "User deactivated successfully"
}
```

#### Activate User
- **URL**: `POST /api/accounts/users/{id}/activate/`
- **Description**: Activate a user account (admin only)
- **Headers**: `Authorization: Token admin-token-here`
- **Response**:
```json
{
    "message": "User activated successfully"
}
```

## Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your-auth-token-here
```

## User Types

- `builder`: Real estate builders/developers
- `agent`: Real estate agents
- `admin`: System administrators

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
    "error": "Error message here"
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## File Uploads

For profile images and other file uploads, use `multipart/form-data` content type.

## Rate Limiting

API endpoints are subject to rate limiting to prevent abuse.

## Security Notes

- Passwords are hashed using Django's secure password hashing
- Tokens should be kept secure and not shared
- HTTPS is recommended for production use
- Email verification is required for full account access 