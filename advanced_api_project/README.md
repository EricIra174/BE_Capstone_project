# Event Management API

A RESTful API for managing events, user registrations, and authentication built with Django REST Framework and JWT authentication.

## Features

- **User Authentication**: JWT-based authentication with token refresh
- **Event Management**: Create, read, update, and delete events
- **Event Registration**: Users can register for events with capacity control
- **Advanced Filtering & Search**: Filter events by date, capacity, and more
- **Documentation**: Interactive API documentation with Swagger/ReDoc
- **Pagination**: Results are paginated for better performance
- **Validation**: Comprehensive input validation and error handling

## API Endpoints

### Authentication

#### Register User
- **URL**: `POST /api/auth/register/`
- **Description**: Register a new user
- **Request Body**: 
  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "securepassword123"
  }
  ```

#### Get JWT Token
- **URL**: `POST /api/auth/token/`
- **Description**: Get access and refresh tokens
- **Request Body**: 
  ```json
  {
    "username": "user1",
    "password": "securepassword123"
  }
  ```

### Events

#### List/Create Events
- **URL**: `GET/POST /api/events/`
- **Description**: List all events or create a new one
- **Query Params**:
  - `upcoming=true`: Filter upcoming events
  - `search=term`: Search in title, description, location
  - `date_time__gte=2025-09-01`: Events on or after date
  - `ordering=-date_time`: Order by date (use - for descending)

#### Event Details
- **URL**: `GET/PUT/PATCH/DELETE /api/events/{id}/`
- **Description**: View, update, or delete an event
- **Permissions**: Only the event organizer can update/delete

#### Register for Event
- **URL**: `POST /api/events/{id}/register/`
- **Description**: Register the current user for an event
- **URL**: `DELETE /api/events/{id}/register/`
- **Description**: Unregister from an event

#### My Events
- **URL**: `GET /api/events/my-events/`
- **Query Params**:
  - `type=attending`: Get events user is attending (default)
  - `type=organized`: Get events user has created

## API Documentation

Interactive API documentation is available at:
- Swagger UI: [/swagger/](http://localhost:8000/swagger/)
- ReDoc: [/redoc/](http://localhost:8000/redoc/)

## Authentication

This API uses JWT authentication. To authenticate your requests:

1. Get an access token by making a POST request to `/api/auth/token/` with your username and password
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer your_access_token_here
   ```

## Examples

### Create an Event
```http
POST /api/events/
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date_time": "2025-10-15T09:00:00Z",
  "location": "Convention Center, City",
  "capacity": 500
}
```

### Register for an Event
```http
POST /api/events/1/register/
Authorization: Bearer your_access_token
```

### List Upcoming Events
```http
GET /api/events/?upcoming=true&ordering=date_time
```
## Getting Started

### Prerequisites

- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+
- SQLite (included with Python)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EricIra174/Alx_DjangoLearnLab.git
   cd advanced_api_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Testing the API

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Open the Swagger UI at: http://localhost:8000/swagger/

3. Use the "Authorize" button to set your JWT token

4. Explore and test the API endpoints directly from the browser

## Project Structure

```
advanced_api_project/
├── api/
│   ├── migrations/     # Database migrations
│   ├── __init__.py
│   ├── admin.py       # Admin interface configuration
│   ├── apps.py        # App configuration
│   ├── models.py      # Database models
│   ├── serializers.py # Serializers for API
│   ├── tests/         # Test cases
│   ├── urls.py        # URL routing
│   └── views.py       # View functions and classes
├── advanced_api_project/
│   ├── __init__.py
│   ├── asgi.py        # ASGI configuration
│   ├── settings.py    # Project settings
│   ├── urls.py        # Main URL configuration
│   └── wsgi.py        # WSGI configuration
├── manage.py          # Django management script
└── requirements.txt   # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django REST Framework
- djangorestframework-simplejwt for JWT Authentication
- drf-yasg for API documentation
