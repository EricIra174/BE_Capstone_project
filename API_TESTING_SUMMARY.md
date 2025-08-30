# API Testing Summary - Event Management API

## 🧪 Quick Testing Reference

This document provides a step-by-step testing guide for all API endpoints.

## 📋 Pre-Testing Setup

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Base URL:** `http://127.0.0.1:8000/api/v1/`

## 🔐 Authentication Flow Testing

### Step 1: User Registration
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
}
```
**Expected:** 201 Created

### Step 2: Get JWT Token
```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass123"
}
```
**Expected:** 200 OK with access token

**Save the access token for all subsequent requests!**

## 🎯 Core Functionality Testing

### Event Management

#### Create Event
```http
POST /api/v1/events/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Test Event",
    "description": "Test Description",
    "date_time": "2025-12-01T10:00:00Z",
    "location": "Test Location",
    "capacity": 50
}
```
**Expected:** 201 Created

#### List Events
```http
GET /api/v1/events/
Authorization: Bearer <access_token>
```
**Expected:** 200 OK with paginated results

#### Get Single Event
```http
GET /api/v1/events/1/
Authorization: Bearer <access_token>
```
**Expected:** 200 OK with event details

#### Update Event
```http
PUT /api/v1/events/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Updated Event",
    "description": "Updated Description",
    "date_time": "2025-12-01T11:00:00Z",
    "location": "Updated Location",
    "capacity": 75
}
```
**Expected:** 200 OK with updated event

#### Delete Event (Soft Delete)
```http
DELETE /api/v1/events/1/
Authorization: Bearer <access_token>
```
**Expected:** 204 No Content

### Event Registration

#### Register for Event
```http
POST /api/v1/events/1/register/
Authorization: Bearer <access_token>
```
**Expected:** 201 Created (successful) or 202 Accepted (waitlist)

### User-Specific Endpoints

#### User's Organized Events
```http
GET /api/v1/users/me/events/organized/
Authorization: Bearer <access_token>
```
**Expected:** 200 OK with user's organized events

#### User's Registered Events
```http
GET /api/v1/users/me/events/registered/
Authorization: Bearer <access_token>
```
**Expected:** 200 OK with user's registered events

## 🔍 Advanced Features Testing

### Filtering & Search

#### Upcoming Events Only
```http
GET /api/v1/events/?upcoming=true
Authorization: Bearer <access_token>
```

#### Search by Title/Location
```http
GET /api/v1/events/?search=conference
Authorization: Bearer <access_token>
```

#### Filter by Organizer
```http
GET /api/v1/events/?organizer=testuser
Authorization: Bearer <access_token>
```

#### Combined Filters
```http
GET /api/v1/events/?upcoming=true&search=tech&organizer=testuser
Authorization: Bearer <access_token>
```

### Token Management

#### Refresh Token
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "<refresh_token>"
}
```
**Expected:** 200 OK with new access token

## 🧪 Test Scenarios

### 1. User Isolation Test
- Create user A and user B
- User A creates an event
- User B tries to update/delete User A's event
- **Expected:** 403 Forbidden or 404 Not Found

### 2. Past Date Prevention
- Try to create event with past date
- **Expected:** 400 Bad Request with validation error

### 3. Capacity Management
- Create event with capacity 2
- Register 2 users
- Try to register 3rd user
- **Expected:** 202 Accepted (added to waitlist)

### 4. Duplicate Registration
- User tries to register for same event twice
- **Expected:** 400 Bad Request with "already registered" error

### 5. Search & Filtering
- Create multiple events with different titles/locations
- Test search functionality
- **Expected:** Filtered results based on query

## ✅ Success Criteria

All tests should return:
- **Proper HTTP status codes** (200, 201, 204, 400, 401, 403, 404)
- **Correct response format** (JSON with expected fields)
- **Proper error messages** for validation failures
- **Permission enforcement** (users can only modify own events)
- **Data consistency** (created data matches input)

## 🚨 Common Issues & Solutions

### 401 Unauthorized
- Check Authorization header format: `Bearer <token>`
- Ensure token is valid and not expired
- Use refresh endpoint if token expired

### 400 Bad Request
- Check JSON format and required fields
- Ensure date is in future (ISO format)
- Verify capacity is positive integer

### 403 Forbidden
- User trying to modify another user's event
- Check if user is authenticated

### 404 Not Found
- Event ID doesn't exist
- Check URL format and event ID

## 🎉 Testing Complete!

Once all endpoints return expected responses, your API is ready for:
- **Production deployment**
- **Frontend integration**
- **Real-world usage**

**Happy testing! 🚀** 