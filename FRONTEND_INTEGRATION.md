# Bus AgentUB - Frontend Integration Guide

## 🚀 Production API Information

**Base URL:** `https://web-production-9625a.up.railway.app`

**API Documentation:** `https://web-production-9625a.up.railway.app/docs`

**Alternative Docs:** `https://web-production-9625a.up.railway.app/redoc`

**Status:** ✅ Live and operational

---

## 📡 API Endpoints Overview

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/profile` - Get current user profile (requires auth)
- `PUT /auth/profile` - Update profile (requires auth)

### Buses (`/buses`)
- `GET /buses` - Search available buses (public)
- `POST /buses` - Add new bus (Owner only)
- `GET /buses/{id}` - Get bus details
- `PUT /buses/{id}` - Update bus (Owner/Supervisor)
- `DELETE /buses/{id}` - Delete bus (Owner only)
- `POST /buses/{id}/stops` - Add boarding point
- `GET /buses/{id}/stops` - Get boarding points

### Bookings (`/booking`)
- `POST /booking/request` - Request booking (Passenger)
- `GET /booking/requests` - View pending requests (Supervisor)
- `POST /booking/accept` - Accept booking (Supervisor)
- `POST /booking/reject` - Reject booking (Supervisor)
- `POST /booking/cancel` - Cancel booking (Passenger)
- `POST /booking/ticket/confirm` - Confirm ticket details (Passenger)
- `GET /booking/tickets/mine` - Get my tickets (Passenger)
- `POST /booking/ticket/cancel` - Cancel ticket (Passenger)

### Owner Dashboard (`/owner`)
- `GET /owner/dashboard` - Dashboard overview
- `POST /owner/register-supervisor` - Register new supervisor
- `GET /owner/supervisors` - List supervisors
- `GET /owner/buses` - List all buses
- `GET /owner/bookings` - Owner bookings view
- `GET /owner/tickets` - Ticket sales report
- `GET /owner/revenue-summary` - Revenue summary

### Location Services (`/location`)
- `POST /location/bus/{id}/update` - Update bus GPS location
- `GET /location/bus/{id}` - Get current bus location
- `GET /location/bus/{id}/eta/{boarding_point_id}` - Calculate ETA
- `GET /location/boarding-points/{id}/nearby` - Find nearby places
- `POST /location/geocode` - Convert address to coordinates
- `GET /location/route/{bus_id}` - Get bus route with stops

### WebSocket Real-Time (`/ws`)
- `WebSocket /ws/location/{bus_id}` - Real-time bus location updates
- `WebSocket /ws/booking` - Real-time booking notifications

---

## 🔐 Authentication

### How to Authenticate

1. **Register or Login** to get JWT token:
```javascript
const response = await fetch('https://web-production-9625a.up.railway.app/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+8801234567890',
    password: 'yourpassword'
  })
});

const data = await response.json();
const token = data.access_token;
```

2. **Use token in subsequent requests**:
```javascript
const response = await fetch('https://web-production-9625a.up.railway.app/buses/1', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Token Details
- **Type:** JWT (JSON Web Token)
- **Expiry:** 7 days
- **Format:** `Bearer <token>`
- **Header:** `Authorization: Bearer eyJhbGc...`

---

## 🌐 CORS Configuration

**Allowed Origins:** All localhost ports are allowed for development
- `http://localhost:3000`
- `http://localhost:5000`
- `http://localhost:8080`
- Any `http://localhost:*` port

**Note:** No CORS issues during development!

---

## 📱 User Roles

### Passenger
- Search and book buses
- View tickets
- Cancel bookings
- Track bus location (after booking accepted)

### Supervisor
- View booking requests
- Accept/reject bookings
- Update bus details
- Update bus location
- Cannot self-register (must be registered by owner)

### Owner
- Manage buses (CRUD)
- Register and manage supervisors
- View dashboard and reports
- Revenue analytics

---

## 🗺 Location Features

### Maps Integration
**Backend uses:** OpenStreetMap (Nominatim, OSRM, Overpass API)

**Available Features:**
- ✅ Geocoding (address ↔ coordinates)
- ✅ Route calculation with ETA
- ✅ Real-time bus tracking
- ✅ Nearby places (restaurants, landmarks)
- ✅ Turn-by-turn directions

**Frontend can use:**
- OpenStreetMap (Leaflet)
- Google Maps
- Mapbox
- Any map provider

---

## 🔌 WebSocket Usage

### Connect to Bus Location Updates
```javascript
const token = "your-jwt-token";
const busId = 1;
const ws = new WebSocket(
  `wss://web-production-9625a.up.railway.app/ws/location/${busId}?token=${token}`
);

ws.onopen = () => {
  console.log('Connected to bus location updates');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Location update:', data);
  // Update map marker position
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Message Format
```json
{
  "type": "location_update",
  "bus_id": 1,
  "location": {
    "lat": 23.8103,
    "lng": 90.4125,
    "timestamp": "2025-11-23T08:30:00"
  }
}
```

---

## 📝 Example Requests

### Register User
```bash
curl -X POST "https://web-production-9625a.up.railway.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+8801712345678",
    "password": "securepass123",
    "nid": "1234567890123",
    "role": "passenger"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "phone": "+8801712345678",
    "role": "passenger"
  }
}
```

### Search Buses
```bash
curl "https://web-production-9625a.up.railway.app/buses?route_from=Dhaka&route_to=Chittagong"
```

### Create Booking Request
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/request" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_id": 1
  }'
```

**Response:**
```json
{
  "booking_id": 1,
  "status": "pending",
  "message": "Booking request sent successfully"
}
```

### Accept Booking (Supervisor)
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/accept" \
  -H "Authorization: Bearer SUPERVISOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1
  }'
```

### Confirm Ticket (Passenger)
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/ticket/confirm" \
  -H "Authorization: Bearer PASSENGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "seat_numbers": "A1, A2",
    "boarding_point_id": 1
  }'
```

### Update Bus Location (Supervisor)
```bash
curl -X POST "https://web-production-9625a.up.railway.app/location/bus/1/update?lat=23.8103&lng=90.4125" \
  -H "Authorization: Bearer SUPERVISOR_TOKEN"
```

---

## 🧪 Testing

### Interactive API Testing
Visit: `https://web-production-9625a.up.railway.app/docs`

Features:
- Try all endpoints directly in browser
- See request/response schemas
- Test authentication
- No Postman needed!

---

## ⚠ Important Notes

### Privacy & Security
- ✅ Passenger details hidden until booking accepted
- ✅ NID never exposed in API responses
- ✅ JWT tokens expire after 7 days
- ✅ Role-based access control enforced
- ✅ Supervisors must be registered by owners (cannot self-register)
- ✅ Each supervisor belongs to exactly one owner

### Data Validation
- **Phone:** Must be international format (`+880...`), 14 characters total
- **Password:** Minimum 8 characters
- **NID:** Exactly 13 digits
- **Bus Number:** Maximum 20 characters
- **Seats:** Cannot exceed bus capacity
- All required fields validated

### Booking Workflow
1. Passenger creates booking request (`POST /booking/request`)
2. Supervisor views pending requests (`GET /booking/requests`)
3. Supervisor accepts booking (`POST /booking/accept` with `booking_id` in body)
4. Passenger confirms ticket details (`POST /booking/ticket/confirm`)
5. Passenger can view confirmed tickets (`GET /booking/tickets/mine`)

### Parameter Formats

**Booking Operations (accept/reject/cancel):**
- Send `booking_id` in request body, NOT in URL path
- Example: `POST /booking/accept` with body `{"booking_id": 1}`

**Location Update:**
- Send coordinates as query parameters
- Example: `POST /location/bus/1/update?lat=23.81&lng=90.41`

### Error Responses
Standard format:
```json
{
  "detail": "Error message here"
}
```

Validation errors format:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters"
    }
  ]
}
```

Common HTTP codes:
- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Server error

---

## 🐛 Troubleshooting

### CORS Issues
- Make sure using `http://localhost:*` for development
- Check browser console for errors
- All localhost ports are allowed

### Authentication Issues
- Verify token format: `Bearer <token>`
- Check token expiry (7 days)
- Ensure correct Authorization header

### WebSocket Issues
- Use `wss://` not `ws://` (secure WebSocket)
- Include token in URL query parameter
- Check if booking is accepted (for passengers)

### Common Mistakes
- Using `/bookings/*` instead of `/booking/*` (singular!)
- Sending `booking_id` in URL instead of request body for accept/reject/cancel
- Sending location coordinates in body instead of query parameters
- Password less than 8 characters
- Bus number longer than 20 characters

---

## 📞 Support

For API issues or questions:
1. Check the interactive docs at `/docs`
2. Review this integration guide
3. Contact backend team

**Backend Status:** ✅ Production ready and tested
**Last Updated:** November 28, 2025
