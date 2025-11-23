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
- `POST /booking/cancel` - Cancel booking
- `POST /booking/ticket/confirm` - Confirm ticket details
- `GET /booking/tickets/mine` - Get my tickets
- `POST /booking/ticket/cancel` - Cancel ticket

### Owner Dashboard (`/owner`)
- `GET /owner/dashboard` - Dashboard overview
- `GET /owner/buses` - List all buses
- `GET /owner/tickets` - Ticket sales report
- `GET /owner/revenue-summary` - Revenue summary
- `GET /owner/supervisors` - List supervisors
- `GET /owner/bookings` - Owner bookings view

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

### Owner
- Manage buses (CRUD)
- View dashboard and reports
- Manage supervisors
- Revenue analytics

---

## 🗺️ Location Features

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

### Search Buses
```bash
curl "https://web-production-9625a.up.railway.app/buses?route_from=Dhaka&route_to=Chittagong"
```

### Request Booking
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/request" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_id": 1,
    "boarding_point_id": 1,
    "seats_requested": 2
  }'
```

---

## 🧪 Testing

### Test Account (Production)
- **Phone:** `+8801999999999`
- **Password:** `testpass123`
- **Role:** Owner
- **Note:** Use for testing only, create your own accounts for real data

### Interactive API Testing
Visit: `https://web-production-9625a.up.railway.app/docs`

Features:
- Try all endpoints directly in browser
- See request/response schemas
- Test authentication
- No Postman needed!

---

## ⚠️ Important Notes

### Privacy & Security
- ✅ Passenger details hidden until booking accepted
- ✅ NID never exposed in API responses
- ✅ JWT tokens expire after 7 days
- ✅ Role-based access control enforced

### Data Validation
- Phone: Must be international format (`+880...`)
- NID: 13 digits (validated on backend)
- Seats: Cannot exceed bus capacity
- All required fields validated

### Error Responses
Standard format:
```json
{
  "detail": "Error message here"
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

---

**Backend Status:** ✅ Production ready
