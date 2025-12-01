# DB → API Response Mapping

How database tables map to API JSON responses.

---

## 1. User Module

### GET /auth/profile

**Response JSON**
```json
{
  "id": 1,
  "name": "Karim Ahmed",
  "phone": "+8801711111111",
  "role": "passenger",
  "is_active": true,
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T10:00:00"
}
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | users | id | Primary key |
| name | users | name | Full name |
| phone | users | phone | International format (+880...) |
| role | users | role | Enum: passenger/supervisor/owner |
| is_active | users | is_active | Account status |
| created_at | users | created_at | Registration timestamp |
| updated_at | users | updated_at | Last profile update |

### POST /auth/login

**Response JSON (Supervisor)**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 24,
    "name": "Rahim Uddin",
    "phone": "+8801710000001",
    "role": "supervisor"
  },
  "assigned_buses": [
    {
      "bus_id": 2,
      "bus_number": "AC-30266",
      "route_from": "Dhaka",
      "route_to": "Chittagong",
      "departure_time": "2025-12-10T08:00:00"
    }
  ]
}
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| assigned_buses | buses | id, bus_number, route_from, route_to, departure_time | WHERE supervisor_id = current_user.id |

**Note:** `assigned_buses` only included if user role is "supervisor"

### GET /auth/profile

**Response JSON (Supervisor)**
```json
{
  "id": 24,
  "name": "Rahim Uddin",
  "phone": "+8801710000001",
  "role": "supervisor",
  "is_active": true,
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T10:00:00",
  "assigned_buses": [
    {
      "bus_id": 2,
      "bus_number": "AC-30266",
      "route_from": "Dhaka",
      "route_to": "Chittagong",
      "departure_time": "2025-12-10T08:00:00"
    }
  ]
}
```

**Note:** `assigned_buses` field added for supervisors in v6.1

---

## 2. Bus Module

### GET /buses (search results)

**Response JSON**
```json
[
  {
    "id": 2,
    "bus_number": "AC-30266",
    "route_from": "Dhaka",
    "route_to": "Chittagong",
    "departure_time": "2025-12-10T08:00:00",
    "bus_type": "AC",
    "fare": "800.00",
    "is_active": true
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | buses | id | Primary key |
| bus_number | buses | bus_number | Max 20 characters |
| route_from | buses | route_from | Start point |
| route_to | buses | route_to | End point |
| departure_time | buses | departure_time | ISO 8601 timestamp |
| bus_type | buses | bus_type | Enum: AC/Non-AC/AC Sleeper |
| fare | buses | fare | Decimal as string |
| is_active | buses | is_active | Soft delete flag |

**Note:** `available_seats` field is excluded from public search results for privacy. Only visible to owners/supervisors in detailed views.

### GET /buses/{id} (full details)

**Response JSON**
```json
{
  "id": 2,
  "bus_number": "AC-30266",
  "route_from": "Dhaka",
  "route_to": "Chittagong",
  "departure_time": "2025-12-10T08:00:00",
  "bus_type": "AC",
  "fare": "800.00",
  "seat_capacity": 40,
  "available_seats": 36,
  "owner_id": 23,
  "supervisor": {
    "id": 24,
    "name": "Rahim Uddin",
    "phone": "+8801710000001"
  },
  "boarding_points": [
    {
      "id": 4,
      "bus_id": 2,
      "name": "Mohakhali Terminal",
      "lat": "23.77990000",
      "lng": "90.40830000",
      "sequence_order": 1,
      "created_at": "2025-11-28T10:00:00"
    }
  ],
  "current_lat": "23.8103",
  "current_lng": "90.4125",
  "last_location_update": "2025-11-28T11:30:00",
  "is_active": true,
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T10:00:00"
}
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | buses | id | PK |
| bus_number | buses | bus_number | Unique identifier |
| seat_capacity | buses | seat_capacity | Total seats |
| owner_id | buses | owner_id | FK to users |
| supervisor | users | id, name, phone | Joined from supervisor_id FK |
| boarding_points | boarding_points | * | Array of stops, ordered by sequence_order |
| current_lat | buses | current_lat | Updated by supervisor |
| current_lng | buses | current_lng | Updated by supervisor |
| last_location_update | buses | last_location_update | GPS timestamp |

---

## 3. Booking Module

### GET /booking/requests

**Response JSON**
```json
[
  {
    "id": 1,
    "bus_id": 2,
    "status": "pending",
    "request_time": "2025-11-28T10:00:00"
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | bookings | id | Booking ID |
| bus_id | bookings | bus_id | FK to buses |
| status | bookings | status | pending/accepted/rejected/cancelled |
| request_time | bookings | request_time | When booking requested |

**Note:** Passenger details (passenger_id, name, phone) only included after acceptance.

### GET /booking/{booking_id}

**Response JSON**
```json
{
  "id": 1,
  "passenger_id": 5,
  "bus_id": 2,
  "bus": {
    "id": 2,
    "bus_number": "AC-30266",
    "route_from": "Dhaka",
    "route_to": "Chittagong",
    "departure_time": "2025-12-10T08:00:00",
    "fare": "800.00"
  },
  "status": "accepted",
  "request_time": "2025-11-28T10:00:00",
  "accepted_time": "2025-11-28T10:15:00"
}
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | bookings | id | Booking ID |
| passenger_id | bookings | passenger_id | FK to users |
| bus_id | bookings | bus_id | FK to buses |
| bus.* | buses | * | Joined data |
| status | bookings | status | Current booking status |
| request_time | bookings | request_time | When requested |
| accepted_time | bookings | accepted_time | When accepted (if applicable) |

**Use Case:** Passenger polling to detect when supervisor accepts booking

### GET /booking/my-requests

**Response JSON**
```json
[
  {
    "id": 3,
    "passenger_id": 5,
    "bus_id": 2,
    "bus": {
      "id": 2,
      "bus_number": "AC-30266",
      "route_from": "Dhaka",
      "route_to": "Chittagong",
      "departure_time": "2025-12-10T08:00:00"
    },
    "status": "pending",
    "request_time": "2025-11-28T12:00:00"
  },
  {
    "id": 1,
    "bus_id": 2,
    "status": "confirmed",
    "request_time": "2025-11-28T10:00:00"
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | bookings | id | Booking ID |
| passenger_id | bookings | passenger_id | Current user's ID |
| bus.* | buses | * | Joined via bus_id |
| status | bookings | status | All statuses included |

**Query:** `SELECT * FROM bookings WHERE passenger_id = ? ORDER BY request_time DESC`

**Use Case:** Passenger viewing complete booking history, includes all statuses

### POST /booking/ticket/confirm

**Response JSON**
```json
{
  "id": 1,
  "booking_id": 1,
  "seat_numbers": "A1, A2",
  "boarding_point": {
    "id": 4,
    "name": "Mohakhali Terminal"
  },
  "fare_per_seat": "800.00",
  "total_fare": "1600.00",
  "status": "confirmed",
  "created_at": "2025-11-28T10:30:00"
}
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | tickets | id | Ticket ID |
| booking_id | tickets | booking_id | FK to bookings |
| seat_numbers | tickets | seat_numbers | Comma-separated string |
| boarding_point | boarding_points | id, name | Joined from boarding_point_id FK |
| fare_per_seat | tickets | fare_per_seat | Copied from bus.fare |
| total_fare | tickets | total_fare | Auto-calculated |
| status | tickets | status | confirmed/completed/cancelled |
| created_at | tickets | created_at | Ticket issue time |

### GET /booking/tickets/mine

**Response JSON**
```json
[
  {
    "id": 1,
    "booking_id": 1,
    "bus": {
      "id": 2,
      "bus_number": "AC-30266",
      "route_from": "Dhaka",
      "route_to": "Chittagong",
      "departure_time": "2025-12-10T08:00:00"
    },
    "boarding_point": {
      "id": 4,
      "name": "Mohakhali Terminal",
      "lat": "23.77990000",
      "lng": "90.40830000"
    },
    "seat_numbers": "A1, A2",
    "total_fare": "1600.00",
    "status": "confirmed",
    "created_at": "2025-11-28T10:30:00"
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | tickets | id | PK |
| booking_id | tickets | booking_id | FK to bookings |
| bus.* | buses | * | Joined via bookings.bus_id |
| boarding_point.* | boarding_points | * | Joined via tickets.boarding_point_id |
| seat_numbers | tickets | seat_numbers | Selected seats |
| total_fare | tickets | total_fare | Calculated fare |
| status | tickets | status | Ticket status |

---

## 4. Owner Module

### GET /owner/dashboard

**Response JSON**
```json
{
  "total_buses": 4,
  "active_trips": 3,
  "total_bookings": 5,
  "confirmed_bookings": 3,
  "pending_bookings": 2,
  "total_revenue": 3500.00,
  "today_revenue": 800.00,
  "dashboard_date": "2025-11-28T12:00:00"
}
```

| JSON Field | Calculation | Notes |
|------------|-------------|-------|
| total_buses | `SELECT COUNT(*) FROM buses WHERE owner_id = ? AND is_active = true` | Owner's active buses |
| active_trips | `COUNT(*) WHERE departure_time = today` | Today's trips |
| total_bookings | `COUNT(*) FROM bookings WHERE bus_id IN (owner's buses)` | All bookings |
| confirmed_bookings | `COUNT(*) WHERE status = 'accepted'` | Accepted bookings |
| pending_bookings | `COUNT(*) WHERE status = 'pending'` | Pending bookings |
| total_revenue | `SUM(total_fare) FROM tickets WHERE status = 'confirmed'` | Total earnings |
| today_revenue | `SUM(total_fare) WHERE created_at = today` | Today's earnings |

### GET /owner/supervisors

**Response JSON**
```json
[
  {
    "id": 24,
    "name": "Rahim Uddin",
    "phone": "+8801710000001",
    "is_active": true,
    "assigned_buses": [
      {
        "id": 2,
        "bus_number": "AC-30266"
      }
    ]
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
|------------|----------|-----------|-------|
| id | users | id | Supervisor ID |
| name | users | name | Supervisor name |
| phone | users | phone | Contact number |
| is_active | users | is_active | Account status |
| assigned_buses | buses | id, bus_number | WHERE supervisor_id = supervisor.id |

---

## 5. Location Module

### POST /location/bus/{id}/update

**Request:** Query params `?lat=23.81&lng=90.41`

**Updates:**
```sql
UPDATE buses 
SET current_lat = ?, 
    current_lng = ?,
    last_location_update = NOW()
WHERE id = ?
```

### GET /location/boarding-points/{id}/nearby

**Response JSON**
```json
{
  "boarding_point_id": 4,
  "boarding_point_name": "Mohakhali Terminal",
  "boarding_point_location": {
    "lat": 23.7799,
    "lng": 90.4083
  },
  "search_radius": 1000,
  "place_type": "restaurant",
  "nearby_places": [
    {
      "name": "Cinnamon",
      "lat": 23.7802773,
      "lng": 90.4067739,
      "type": "restaurant",
      "distance_m": 160,
      "tags": {
        "amenity": "restaurant",
        "name": "Cinnamon"
      }
    }
  ]
}
```

**Sources:**
- `boarding_point_*`: From `boarding_points` table
- `nearby_places`: From OpenStreetMap Overpass API (not database)

---

## Key Relationships

```
users (owner) 
  └── buses (owner_id FK)
        ├── supervisor (supervisor_id FK → users)
        ├── boarding_points (bus_id FK)
        └── bookings (bus_id FK)
              └── tickets (booking_id FK)
                    └── boarding_point (boarding_point_id FK)
```

---