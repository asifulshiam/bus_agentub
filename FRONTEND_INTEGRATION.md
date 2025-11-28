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

## 📝 Example Requests (UPDATED)

### Register User (Passenger or Owner Only)

**✅ Allowed Roles:** `passenger`, `owner`

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

**❌ Blocked: Supervisor Registration**

```bash
# This will return 403 Forbidden
curl -X POST "https://web-production-9625a.up.railway.app/auth/register" \
  -d '{"role": "supervisor", ...}'

# Response:
{
  "detail": "Supervisors cannot self-register. Contact your bus company owner."
}
```

---

### Register Supervisor (Owner Only)

**✅ Correct Way to Create Supervisor:**

```bash
curl -X POST "https://web-production-9625a.up.railway.app/owner/register-supervisor" \
  -H "Authorization: Bearer OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Supervisor",
    "phone": "+8801888888888",
    "password": "supervisor_password",
    "nid": "9876543210987",
    "role": "supervisor"
  }'
```

**Response:**
```json
{
  "id": 2,
  "name": "John Supervisor",
  "phone": "+8801888888888",
  "role": "supervisor",
  "owner_id": 1,
  "is_active": true,
  "created_at": "2025-11-27T10:00:00"
}
```

---

### List Supervisors (Owner Only)

**Security Feature:** Only returns supervisors YOU hired

```bash
curl "https://web-production-9625a.up.railway.app/owner/supervisors" \
  -H "Authorization: Bearer OWNER_TOKEN"
```

**Response:**
```json
[
  {
    "id": 2,
    "name": "John Supervisor",
    "phone": "+8801888888888",
    "role": "supervisor",
    "owner_id": 1,
    "is_active": true,
    "assigned_buses": [
      {"id": 1, "bus_number": "DB-AC-001"}
    ]
  }
]
```

**Note:** If another owner has supervisors, you WON'T see them.

---

### Create Bus with Supervisor Assignment

**Validation:** Can only assign supervisors YOU own

```bash
curl -X POST "https://web-production-9625a.up.railway.app/buses" \
  -H "Authorization: Bearer OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_number": "DB-AC-001",
    "route_from": "Dhaka",
    "route_to": "Chittagong",
    "departure_time": "2025-12-01T08:00:00",
    "bus_type": "AC",
    "fare": 1200,
    "seat_capacity": 40,
    "supervisor_id": 2
  }'
```

**Success Response (supervisor belongs to you):**
```json
{
  "id": 1,
  "bus_number": "DB-AC-001",
  "supervisor_id": 2,
  ...
}
```

**Error Response (supervisor belongs to another owner):**
```json
{
  "detail": "Cannot assign supervisor not hired by you"
}
```

---

## 🔒 Security Features (NEW)

### Supervisor Ownership System

**Problem Solved:** Prevents owners from seeing/assigning each other's supervisors

**How It Works:**

1. **Registration:**
   - Supervisors CANNOT self-register via `/auth/register`
   - Only owners can create supervisors via `/owner/register-supervisor`
   - Supervisor automatically linked with `owner_id`

2. **Listing:**
   - `GET /owner/supervisors` filters by `owner_id = current_user.id`
   - You only see YOUR supervisors

3. **Assignment:**
   - When creating/updating buses, backend validates supervisor ownership
   - Cannot assign supervisors from other owners

4. **Privacy:**
   - Competing bus companies can't see each other's staff
   - Each company operates independently

**Real-World Example:**
- Company A (Owner 1) has Supervisors 2, 3
- Company B (Owner 4) has Supervisor 5
- Owner 1 cannot assign Supervisor 5 to their buses
- Owner 4 cannot see Supervisors 2, 3 in their list

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
