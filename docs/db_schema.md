# Database Schema – Bus AgentUB

Complete database structure and relationships.

---

## 1. Users

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
|-------|------|---------|-------------------|-------------------|
| `id` | SERIAL PK | Unique user ID | — | `{id}` or `{user_id}` |
| `name` | VARCHAR(100) | User's full name | Input on registration/profile update | Returned in profile/tickets |
| `phone` | VARCHAR(14) UNIQUE | Login credential | Input on registration/login (`+880XXXXXXXXXX`) | Returned in profile |
| `password_hash` | VARCHAR(255) | Encrypted password | Sent as `password` → hashed by backend | ❌ Never returned |
| `nid` | VARCHAR(13) | National ID (13 digits) | Input on signup | ❌ Never returned (privacy) |
| `role` | ENUM | User type | Sent in registration: `passenger`, `supervisor`, `owner` | Returned in profile<br> Login returns `assigned_buses` array for supervisors |
| `owner_id` | INT FK → users(id) | Supervisor's owner | Set by backend when owner registers supervisor | Backend only |
| `is_active` | BOOLEAN | Account enabled | — | Returned in some endpoints |
| `created_at` | TIMESTAMP | Registration time | — | Returned in profile |
| `updated_at` | TIMESTAMP | Last modification | — | Returned in profile |

**Enum Values:**
- `role`: `passenger`, `supervisor`, `owner`

**Constraints:**
- `phone` must be unique
- `supervisor` role must have `owner_id` (cannot be null)
- `owner` and `passenger` roles have null `owner_id`

**NEW Access Patterns:**
- Supervisors receive `assigned_buses` array on login
- Supervisors see assigned buses in profile endpoint
- Query: `SELECT * FROM buses WHERE supervisor_id = user.id`

---

## 2. Buses

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
|-------|------|---------|-------------------|-------------------|
| `id` | SERIAL PK | Bus ID | — | `{id}` or `{bus_id}` |
| `bus_number` | VARCHAR(20) UNIQUE | Bus identifier/plate | Input when owner adds bus (max 20 chars) | Returned in search & details |
| `route_from` | VARCHAR(100) | Starting point | Input on bus add | Returned in search & details |
| `route_to` | VARCHAR(100) | Ending point | Input on bus add | Returned in search & details |
| `departure_time` | TIMESTAMP | Departure time | Input on bus add (ISO 8601) | Returned in search & details |
| `bus_type` | ENUM | Bus category | Input: `AC`, `Non-AC`, `AC Sleeper` | Returned in search & details |
| `fare` | DECIMAL(10,2) | Price per seat | Input on bus add | Returned as string in API |
| `seat_capacity` | INT | Total seats | Input on bus add | Returned in bus details |
| `available_seats` | INT | Seats remaining | Auto-managed by triggers/code | Returned in search |
| `owner_id` | INT FK → users(id) | Bus owner | Auto-set from authenticated owner | Backend only |
| `supervisor_id` | INT FK → users(id) | Assigned supervisor | Input when creating bus | Returned as supervisor object<br> Included in supervisor login response |
| `current_lat` | DECIMAL(10,8) | Live GPS latitude | Updated by supervisor via API | Returned in location endpoints |
| `current_lng` | DECIMAL(11,8) | Live GPS longitude | Updated by supervisor via API | Returned in location endpoints |
| `last_location_update` | TIMESTAMP | Last GPS ping | Auto-set on location update | Returned in location endpoints |
| `is_active` | BOOLEAN | Bus enabled/deleted | — | Soft delete flag |
| `created_at` | TIMESTAMP | Bus creation time | — | Returned in details |
| `updated_at` | TIMESTAMP | Last modification | — | Returned in details |

**Enum Values:**
- `bus_type`: `AC`, `Non-AC`, `AC Sleeper`

**Constraints:**
- `bus_number` must be unique and max 20 characters
- `supervisor_id` must reference a user with role = `supervisor`
- `supervisor.owner_id` must equal `bus.owner_id` (supervisor must belong to the bus owner)

---

## 3. Boarding Points

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
|-------|------|---------|-------------------|-------------------|
| `id` | SERIAL PK | Boarding point ID | — | `{id}` |
| `bus_id` | INT FK → buses(id) | Parent bus | Set from bus context | Returned in boarding point list |
| `name` | VARCHAR(100) | Stop name | Supervisor/owner adds | Returned to passengers after booking accepted |
| `lat` | DECIMAL(10,8) | GPS latitude | Supervisor/owner adds | Returned for map display |
| `lng` | DECIMAL(11,8) | GPS longitude | Supervisor/owner adds | Returned for map display |
| `sequence_order` | INT | Boarding sequence | Supervisor/owner sets | Returned in ordered list |
| `created_at` | TIMESTAMP | Creation time | — | Returned in some endpoints |

**Constraints:**
- Multiple boarding points per bus allowed
- `sequence_order` determines the order stops appear to passengers

---

## 4. Bookings

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
|-------|------|---------|-------------------|-------------------|
| `id` | SERIAL PK | Booking ID | — | `{id}` or `{booking_id}` |
| `passenger_id` | INT FK → users(id) | Who requested | Auto from authenticated passenger | Shown to supervisor **only after acceptance** |
| `bus_id` | INT FK → buses(id) | Which bus | Passenger sends in booking request | Returned in booking object |
| `status` | ENUM | Booking state | Auto default `pending`, updated by actions | Returned in all booking responses |
| `request_time` | TIMESTAMP | When requested | Auto-set on creation | Returned in booking list |
| `accepted_time` | TIMESTAMP | When accepted | Auto-set on acceptance | Backend tracking |
| `rejected_time` | TIMESTAMP | When rejected | Auto-set on rejection | Backend tracking |
| `cancelled_time` | TIMESTAMP | When cancelled | Auto-set on cancellation | Backend tracking |
| `rejection_reason` | TEXT | Why rejected | Optional supervisor input | Returned if exists |
| `cancellation_reason` | TEXT | Why cancelled | Optional passenger/supervisor input | Returned if exists |
| `created_at` | TIMESTAMP | Record creation | — | Backend only |
| `updated_at` | TIMESTAMP | Last modification | — | Backend only |

**Enum Values:**
- `status`: `pending`, `accepted`, `rejected`, `cancelled`

**State Transitions:**
```
pending → accepted → (ticket creation)
pending → rejected
pending → cancelled
accepted → cancelled
```

**Privacy Rule:**
- Supervisor sees only booking existence when status = `pending`
- Supervisor sees passenger details only when status = `accepted`

**New Access Patterns:**

**GET /booking/{booking_id}:**
- Returns single booking by ID
- Includes joined bus data
- Used for status polling by passengers
- Query: `SELECT * FROM bookings WHERE id = ? AND passenger_id = ?`

**GET /booking/my-requests:**
- Returns all bookings for current passenger
- Ordered by `request_time DESC` (newest first)
- Includes all statuses: pending, accepted, confirmed, rejected, cancelled
- Query: `SELECT * FROM bookings WHERE passenger_id = ? ORDER BY request_time DESC`

---

## 5. Tickets

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
|-------|------|---------|-------------------|-------------------|
| `id` | SERIAL PK | Ticket ID | — | `{id}` or `{ticket_id}` |
| `booking_id` | INT FK → bookings(id) | Parent booking | Passenger sends after acceptance | Backend only (joined data returned) |
| `boarding_point_id` | INT FK → boarding_points(id) | Where to board | Passenger selects from list | Returned as boarding_point object |
| `seat_numbers` | VARCHAR(100) | Seats selected | Passenger sends (e.g., "A1, A2") | Returned in ticket |
| `fare_per_seat` | DECIMAL(10,2) | Price per seat | Auto-copied from bus.fare at time of booking | Returned in ticket |
| `total_fare` | DECIMAL(10,2) | Total cost | Auto-calculated: seats × fare_per_seat | Returned in ticket |
| `status` | ENUM | Ticket state | Auto default `confirmed` | Returned in ticket |
| `created_at` | TIMESTAMP | Ticket issue time | — | Returned as purchase date |
| `completed_at` | TIMESTAMP | Journey completed | Auto-set after journey | Backend tracking |
| `cancelled_at` | TIMESTAMP | If cancelled | Auto-set on cancellation | Backend tracking |
| `updated_at` | TIMESTAMP | Last modification | — | Backend only |

**Enum Values:**
- `status`: `confirmed`, `completed`, `cancelled`

**Business Logic:**
- Ticket can only be created if booking status = `accepted`
- Creating a ticket decrements `buses.available_seats`
- Cancelling a ticket increments `buses.available_seats`

---

## Relationships Diagram

```
users (owner)
  ├── buses (owner_id FK)
  │     ├── supervisor (supervisor_id FK → users)
  │     ├── boarding_points (bus_id FK)
  │     └── bookings (bus_id FK)
  │           ├── passenger (passenger_id FK → users)
  │           └── tickets (booking_id FK)
  │                 └── boarding_point (boarding_point_id FK → boarding_points)
  └── supervisors (owner_id FK → users)
```

---

## Data Flow

### 1. User Registration
```
Frontend → POST /auth/register → users table
- Hashes password
- Creates user record
- Returns JWT token
```

### 2. Bus Creation (Owner)
```
Frontend → POST /buses → buses table
- Validates supervisor belongs to owner
- Creates bus record
- Links supervisor_id
```

### 3. Boarding Point Creation
```
Frontend → POST /buses/{id}/stops → boarding_points table
- Validates bus ownership
- Creates boarding point
- Orders by sequence_order
```

### 4. Booking Flow
```
Passenger → POST /booking/request → bookings table (status: pending)
          ↓
Supervisor → GET /booking/requests → sees request (no passenger details)
          ↓
Supervisor → POST /booking/accept → updates status to 'accepted'
          ↓
Passenger → POST /booking/ticket/confirm → tickets table
          ↓
          → Updates buses.available_seats (-seats_booked)
```

### 5. Live Location
```
Supervisor → POST /location/bus/{id}/update?lat=X&lng=Y
          ↓
Updates buses.current_lat, current_lng, last_location_update
          ↓
Passengers receive via WebSocket /ws/location/{bus_id}
```

### 6. Status Polling
```
Passenger → POST /booking/request → booking created
          ↓
Passenger → Polls GET /booking/{id} every few seconds
          ↓
          → Detects status change from 'pending' to 'accepted'
          ↓
Passenger → Proceeds to POST /booking/ticket/confirm
```

**Alternative:** Passenger uses GET /booking/my-requests to see all bookings at once

### 7. Supervisor Login Flow
```
Supervisor → POST /auth/login
          ↓
Backend → Queries buses WHERE supervisor_id = user.id
          ↓
Returns: {access_token, user: {...}, assigned_buses: [{bus_id, bus_number, ...}]}
```

---

## Indexes

**Performance optimization indexes:**
- `users.phone` (UNIQUE) - Fast login lookup
- `users.role` - Role-based queries
- `buses.owner_id` - Owner's buses lookup
- `buses.supervisor_id` - Supervisor's assigned buses
- `buses.departure_time` - Date-based searches
- `buses.route_from, route_to` - Route searches
- `bookings.passenger_id` - Passenger's bookings (enhanced for my-requests)
- `bookings.bus_id` - Bus bookings
- `bookings.status` - Status filtering
- `tickets.booking_id` - Ticket lookup
- `boarding_points.bus_id` - Bus stops lookup

---

## Constraints & Validation

### Database Level
- All foreign keys have `ON DELETE CASCADE` or `ON DELETE SET NULL` as appropriate
- `UNIQUE` constraints on `users.phone`, `buses.bus_number`
- `CHECK` constraints on ENUMs
- `NOT NULL` on required fields

### Application Level (FastAPI)
- Phone: Must match `+880XXXXXXXXXX` pattern (14 chars)
- Password: Minimum 8 characters
- NID: Exactly 13 digits
- Bus number: Maximum 20 characters
- Supervisor ownership: supervisor.owner_id must equal bus.owner_id

---  
**Database:** PostgreSQL 16  
