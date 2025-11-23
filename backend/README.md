# Bus AgentUB Backend API

A comprehensive FastAPI-based backend for the Bus AgentUB booking system with real-time tracking and Google Maps integration.

## 🚀 Features

- **User Management**: Registration, authentication, and role-based access (Passenger, Supervisor, Owner)
- **Bus Management**: Create, update, and manage buses with routes and schedules
- **Booking System**: Complete booking flow from request to ticket confirmation
- **Real-time Updates**: WebSocket support for live booking status and bus location updates
- **Google Maps Integration**: Location services, ETA calculation, and route planning
- **Owner Dashboard**: Comprehensive analytics and management tools
- **Security**: JWT authentication with role-based permissions

## 📋 Prerequisites

- Python 3.8+
- SQLite (for development) or PostgreSQL (for production)
- Google Maps API key (optional, for enhanced location features)

## 🛠️ Installation

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   # Database
   DATABASE_URL=sqlite:///./bus_booking.db
   
   # JWT Authentication
   SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_DAYS=7
   
   # Application
   APP_NAME=Bus AgentUB API
   DEBUG=True
   
   # CORS (for frontend)
   CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
   
   # Google Maps API (optional)
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

5. **Initialize the database**
   ```bash
   python -m app.database.init_db
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔐 Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Sample Login Credentials (after database initialization)

- **Owner**: `01700000001` / `password123`
- **Supervisor**: `01700000002` / `password123`
- **Passenger**: `01700000003` / `password123`

## 🏗️ API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Bus Management
- `GET /buses` - Search buses (public)
- `POST /buses` - Create bus (Owner only)
- `GET /buses/{id}` - Get bus details
- `PUT /buses/{id}` - Update bus
- `DELETE /buses/{id}` - Delete bus (Owner only)
- `POST /buses/{id}/stops` - Add boarding point
- `GET /buses/{id}/stops` - Get boarding points

### Booking Management
- `POST /booking/request` - Send booking request (Passenger)
- `GET /booking/requests` - View booking requests (Supervisor)
- `POST /booking/accept` - Accept booking (Supervisor)
- `POST /booking/reject` - Reject booking (Supervisor)
- `POST /booking/cancel` - Cancel booking
- `POST /booking/ticket/confirm` - Confirm ticket details
- `GET /booking/tickets/mine` - Get my tickets
- `POST /booking/ticket/cancel` - Cancel ticket

### Location Services
- `POST /location/bus/{id}/update` - Update bus location (Supervisor)
- `GET /location/bus/{id}` - Get bus location
- `GET /location/bus/{id}/eta/{boarding_point_id}` - Get ETA to boarding point
- `GET /location/boarding-points/{id}/nearby` - Find nearby places
- `POST /location/geocode` - Convert address to coordinates
- `GET /location/route/{id}` - Get bus route details

### Owner Dashboard
- `GET /owner/dashboard` - Dashboard overview
- `GET /owner/buses` - List all buses
- `GET /owner/tickets` - Ticket sales report
- `GET /owner/supervisors` - Get all supervisors
- `GET /owner/bookings` - Get all bookings
- `GET /owner/revenue-summary` - Revenue summary

### WebSocket Endpoints
- `WS /ws/booking` - Real-time booking updates
- `WS /ws/location/{bus_id}` - Real-time bus location updates

## 🔄 Booking Flow

1. **Search Buses**: Passengers search for available buses
2. **Send Request**: Passenger sends booking request
3. **Supervisor Review**: Supervisor sees pending requests
4. **Accept/Reject**: Supervisor accepts or rejects request
5. **Ticket Confirmation**: Passenger selects boarding point and seat count
6. **Real-time Updates**: Live location tracking and notifications

## 🗄️ Database Schema

The system uses the following main entities:

- **Users**: Passengers, Supervisors, and Owners
- **Buses**: Bus information with routes and schedules
- **Boarding Points**: Bus stops with GPS coordinates
- **Bookings**: Booking requests and status tracking
- **Tickets**: Confirmed tickets with payment details

## 🌍 Google Maps Integration

The system integrates with Google Maps API for:

- **Distance Calculation**: Calculate distances between points
- **ETA Calculation**: Estimate arrival times
- **Route Planning**: Get detailed route directions
- **Geocoding**: Convert addresses to coordinates
- **Nearby Places**: Find nearby amenities

Set the `GOOGLE_MAPS_API_KEY` environment variable to enable these features.

## 🔧 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 🚀 Production Deployment

1. **Use PostgreSQL instead of SQLite**
2. **Set strong SECRET_KEY**
3. **Configure proper CORS origins**
4. **Set up proper logging**
5. **Use environment variables for all secrets**
6. **Enable HTTPS**
7. **Set up proper monitoring**

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./bus_booking.db` |
| `SECRET_KEY` | JWT secret key | Random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Token expiration days | `7` |
| `APP_NAME` | Application name | `Bus AgentUB API` |
| `DEBUG` | Debug mode | `True` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | `""` |
