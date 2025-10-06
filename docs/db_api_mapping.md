# 📘 DB → API Response Mapping

* * *

## **1\. User Module**

### **GET /auth/profile**

**Response JSON**

```json
{
  "user_id": 1,
  "name": "Karim Ahmed",
  "phone": "01711111111",
  "role": "passenger"
}
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| user_id | users | id  | Primary key |
| name | users | name | Full name |
| phone | users | phone | Login phone |
| role | users | role | Enum: passenger/supervisor/owner |

* * *

## **2\. Bus Module**

### **GET /buses (search results)**

**Response JSON**

```json
[
  {
    "bus_id": 2,
    "route_from": "Dhaka",
    "route_to": "Sylhet",
    "departure_time": "2025-10-05T09:30:00",
    "bus_type": "AC",
    "fare": 700,
    "available_seats": 36
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| bus_id | buses | id  | Primary key |
| route_from | buses | route_from | Start point |
| route_to | buses | route_to | End point |
| departure_time | buses | departure_time | Timestamp |
| bus_type | buses | bus_type | Enum |
| fare | buses | fare | Price per seat |
| available_seats | buses | available_seats | Auto-updated by tickets |

### **GET /buses/{id} (full details)**

**Response JSON**

```json
{
  "bus_id": 2,
  "bus_number": "DB-5678",
  "route_from": "Dhaka",
  "route_to": "Sylhet",
  "departure_time": "2025-10-05T09:30:00",
  "bus_type": "AC",
  "fare": 700,
  "seat_capacity": 36,
  "available_seats": 36,
  "supervisor_name": "Rahim Uddin",
  "supervisor_phone": "01710000001",
  "boarding_points": [
    {"id": 4, "name": "Airport", "lat": 23.8493, "lng": 90.4195},
    {"id": 5, "name": "Uttara", "lat": 23.8767, "lng": 90.3798},
    {"id": 6, "name": "Gazipur", "lat": 23.9999, "lng": 90.4203}
  ],
  "live_location": {"lat": 23.8103, "lng": 90.4125}
}
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| bus_id | buses | id  | PK  |
| bus_number | buses | bus_number | Plate |
| route_from | buses | route_from | Start point |
| route_to | buses | route_to | End point |
| departure_time | buses | departure_time | Timestamp |
| bus_type | buses | bus_type | Enum |
| fare | buses | fare | Price per seat |
| seat_capacity | buses | seat_capacity | Total seats |
| available_seats | buses | available_seats | Remaining seats |
| supervisor_name | users | name | Role = supervisor |
| supervisor_phone | users | phone | Supervisor contact |
| boarding_points | boarding_points | id,name,lat,lng | Ordered by sequence_order |
| live_location.lat/lng | buses | current_lat/current_lng | Updated via WebSocket |

* * *

## **3\. Booking Module**

### **GET /booking/requests**

**Response JSON**

```json
[
  {
    "booking_id": 1,
    "bus_id": 1,
    "status": "pending",
    "request_time": "2025-10-05T07:45:00"
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| booking_id | bookings | id  | PK  |
| bus_id | bookings | bus_id | FK to buses |
| status | bookings | status | pending/accepted/rejected |
| request_time | bookings | request_time | Timestamp |

### **POST /ticket/confirm**

**Response JSON**

```json
{
  "ticket_id": 2,
  "status": "confirmed"
}
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| ticket_id | tickets | id  | PK  |
| status | tickets | status | confirmed |

### **GET /tickets/mine**

**Response JSON**

```json
[
  {
    "ticket_id": 2,
    "bus_id": 2,
    "departure_time": "2025-10-05T09:30:00",
    "boarding_point": "Airport",
    "seats_booked": 2
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| ticket_id | tickets | id  | PK  |
| bus_id | bookings → buses | bookings.bus_id | FK  |
| departure_time | buses | departure_time | Timestamp |
| boarding_point | boarding_points | name | Selected boarding stop |
| seats_booked | tickets | seats_booked | Integer |

* * *

## **4\. Admin Module**

### **GET /admin/dashboard**

**Response JSON**

```json
{
  "total_buses": 4,
  "active_trips": 3,
  "total_bookings": 5,
  "total_revenue": 3500
}
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| total_buses | buses | COUNT(\*) | All active buses |
| active_trips | buses | COUNT(\*) WHERE departure_time = today | Active trips |
| total_bookings | bookings | COUNT(\*) | All bookings |
| total_revenue | tickets | SUM(total_fare) WHERE status=‘confirmed’ | Total revenue |

### **GET /admin/buses**

**Response JSON**

```json
[
  {
    "bus_id": 2,
    "bus_number": "DB-5678",
    "supervisor_name": "Rahim Uddin",
    "bookings_count": 2
  }
]
```

| JSON Field | DB Table | DB Column | Notes |
| --- | --- | --- | --- |
| bus_id | buses | id  | PK  |
| bus_number | buses | bus_number | Plate |
| supervisor_name | users | name (supervisor) | FK  |
| bookings_count | bookings | COUNT(\*) | Related bookings |

* * *

&nbsp;