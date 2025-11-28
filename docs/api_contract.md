# API Contract - Bus AgentUB

Complete API reference for frontend integration.

**Production API:** `https://web-production-9625a.up.railway.app`  
**Interactive Docs:** `https://web-production-9625a.up.railway.app/docs`

---

## Authentication & User Management

| Endpoint | Method | Auth | Purpose | Request | Response | Validation |
|----------|--------|------|---------|---------|----------|------------|
| `/auth/register` | POST | No | Register user | `{name, phone, password, nid, role}` | `{access_token, user: {id, name, phone, role}}` | phone: +880XXXXXXXXXX (14 chars)<br>password: min 8 chars<br>nid: exactly 13 digits<br>role: passenger/supervisor/owner |
| `/auth/login` | POST | No | Login | `{phone, password}` | `{access_token, user: {id, name, phone, role}}` | Returns JWT valid for 7 days |
| `/auth/profile` | GET | Yes | Get profile | - | `{id, name, phone, role, is_active, created_at, updated_at}` | - |
| `/auth/profile` | PUT | Yes | Update profile | `{name}` | `{id, name, phone, role, ...}` | - |

---

## Bus Management

| Endpoint | Method | Auth | Purpose | Request | Response | Validation |
|----------|--------|------|---------|---------|----------|------------|
| `/buses` | GET | No | Search buses | Query: `?route_from=&route_to=&date=` | `[{id, bus_number, route_from, route_to, departure_time, bus_type, fare, available_seats, is_active}]` | Public endpoint |
| `/buses` | POST | Owner | Create bus | `{bus_number, route_from, route_to, departure_time, bus_type, fare, seat_capacity, supervisor_id}` | `{id, bus_number, ..., supervisor: {id, name, phone}}` | bus_number: max 20 chars<br>bus_type: "AC", "Non-AC", "AC Sleeper"<br>supervisor must belong to owner |
| `/buses/{id}` | GET | Auth | Get details | - | `{id, bus_number, route_from, route_to, ..., supervisor: {...}, boarding_points: [...], current_lat, current_lng}` | Full bus details |
| `/buses/{id}` | PUT | Owner/Supervisor | Update bus | `{fare?, bus_type?, ...}` | Updated bus object | - |
| `/buses/{id}` | DELETE | Owner | Soft delete | - | `{message, bus_id}` | Sets is_active=false |
| `/buses/{id}/stops` | POST | Owner/Supervisor | Add boarding point | `{name, lat, lng, sequence_order}` | `{id, bus_id, name, lat, lng, sequence_order, created_at}` | - |
| `/buses/{id}/stops` | GET | Auth | List stops | - | `[{id, bus_id, name, lat, lng, sequence_order}]` | - |

---

## Booking Workflow

| Endpoint | Method | Auth | Purpose | Request | Response | Notes |
|----------|--------|------|---------|---------|----------|-------|
| `/booking/request` | POST | Passenger | Create request | `{bus_id}` | `{booking_id, status: "pending", message}` | Creates pending booking |
| `/booking/requests` | GET | Supervisor | View pending | Query: `?bus_id=` | `[{id, bus_id, status, request_time}]` | No passenger details until accepted |
| `/booking/accept` | POST | Supervisor | Accept booking | Body: `{booking_id}` | `{booking_id, status: "accepted", passenger details...}` | **booking_id in body, not URL** |
| `/booking/reject` | POST | Supervisor | Reject booking | Body: `{booking_id}` | `{booking_id, status: "rejected"}` | **booking_id in body, not URL** |
| `/booking/cancel` | POST | Passenger | Cancel booking | Body: `{booking_id}` | `{booking_id, status: "cancelled"}` | **booking_id in body, not URL** |
| `/booking/ticket/confirm` | POST | Passenger | Confirm ticket | `{booking_id, seat_numbers, boarding_point_id}` | `{id, booking_id, seat_numbers, boarding_point, total_fare, status}` | After booking accepted |
| `/booking/tickets/mine` | GET | Passenger | Get my tickets | Query: `?status=` | `[{id, booking_id, bus details, seat_numbers, boarding_point, total_fare}]` | - |
| `/booking/ticket/cancel` | POST | Passenger | Cancel ticket | `{ticket_id}` | `{ticket_id, status: "cancelled"}` | - |

---

## Owner Dashboard

| Endpoint | Method | Auth | Purpose | Request | Response |
|----------|--------|------|---------|---------|----------|
| `/owner/dashboard` | GET | Owner | Stats overview | - | `{total_buses, active_trips, total_bookings, confirmed_bookings, pending_bookings, total_revenue, today_revenue, dashboard_date}` |
| `/owner/register-supervisor` | POST | Owner | Add supervisor | `{name, phone, password, nid, role: "supervisor"}` | `{message, supervisor: {id, name, phone}}` |
| `/owner/supervisors` | GET | Owner | List supervisors | - | `[{id, name, phone, is_active, assigned_buses: [...]}]` |
| `/owner/buses` | GET | Owner | List buses | - | `[{id, bus_number, route_from, route_to, supervisor, ...}]` |
| `/owner/bookings` | GET | Owner | View bookings | - | `[{booking details...}]` |
| `/owner/tickets` | GET | Owner | Sales report | Query: `?from=&to=` | `{total_revenue, total_tickets_sold, date_range, breakdown_by_bus, report_generated_at}` |

---

## Location Services

| Endpoint | Method | Auth | Purpose | Request | Response | Notes |
|----------|--------|------|---------|---------|----------|-------|
| `/location/bus/{id}/update` | POST | Supervisor | Update GPS | **Query params:** `?lat=23.81&lng=90.41` | `{message, bus_id, location: {lat, lng}, timestamp}` | **Use query params, not body** |
| `/location/bus/{id}` | GET | Auth | Get location | - | `{bus_id, current_lat, current_lng, last_update}` | - |
| `/location/bus/{id}/eta/{boarding_point_id}` | GET | Auth | Calculate ETA | - | `{distance_km, duration_minutes, eta}` | - |
| `/location/boarding-points/{id}/nearby` | GET | Public | Nearby places | Query: `?radius=1000&type=restaurant` | `{boarding_point_id, boarding_point_name, nearby_places: [{name, lat, lng, type, distance_m}]}` | Uses OpenStreetMap |
| `/location/geocode` | POST | Public | Address → coords | `{address}` | `{address, lat, lng, display_name, address_details}` | Uses Nominatim |
| `/location/route/{bus_id}` | GET | Auth | Get route | - | `{bus_id, route_from, route_to, boarding_points: [...]}` | - |

---

## WebSocket Real-Time

| Endpoint | Protocol | Auth | Purpose | Connection | Message Format |
|----------|----------|------|---------|------------|----------------|
| `/ws/location/{bus_id}` | WebSocket | Yes | Live location | `wss://...?token=JWT_TOKEN` | `{type: "location_update", bus_id, location: {lat, lng, timestamp}}` |
| `/ws/booking` | WebSocket | Yes | Booking updates | `wss://...?token=JWT_TOKEN` | `{type: "booking_accepted/rejected", booking_id, ...}` |

---

## Important Notes

### Authentication
- **Token Type:** JWT Bearer token
- **Expiry:** 7 days
- **Header Format:** `Authorization: Bearer <token>`
- **Error Response:** `401 Unauthorized` if missing/invalid

### Validation Rules
- **Phone:** Must be `+880` followed by 11 digits (total 14 chars)
- **Password:** Minimum 8 characters
- **NID:** Exactly 13 digits
- **Bus Number:** Maximum 20 characters
- **Bus Type:** Only "AC", "Non-AC", or "AC Sleeper"

### Parameter Formats
- **Booking operations** (accept/reject/cancel): Send `booking_id` in request **body**, not URL path
- **Location update**: Send coordinates as **query parameters**, not body
- **Dates:** ISO 8601 format (`2025-12-25T10:00:00`)

### Privacy & Security
- ✅ Supervisors cannot self-register (must be created by owner)
- ✅ Each supervisor belongs to one owner
- ✅ Passenger details hidden until booking accepted
- ✅ NID never exposed in API responses
- ✅ Role-based access control enforced

### Error Responses

**Standard Error:**
```json
{
  "detail": "Error message"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "test123"
    }
  ]
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Server error

---

## Quick Start Example

### 1. Register User
```bash
curl -X POST "https://web-production-9625a.up.railway.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+8801712345678",
    "password": "secure123",
    "nid": "1234567890123",
    "role": "passenger"
  }'
```

### 2. Search Buses
```bash
curl "https://web-production-9625a.up.railway.app/buses?route_from=Dhaka&route_to=Chittagong"
```

### 3. Create Booking
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/request" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bus_id": 1}'
```

### 4. Accept Booking (Supervisor)
```bash
curl -X POST "https://web-production-9625a.up.railway.app/booking/accept" \
  -H "Authorization: Bearer SUPERVISOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": 1}'
```

---

**Last Updated:** November 28, 2025  
**API Version:** 1.0  
**Database:** PostgreSQL 16 on Railway
