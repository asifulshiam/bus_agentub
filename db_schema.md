&nbsp;

# 📘 Database Schema – Bus Ticketing System

## 1\. **Users**

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
| --- | --- | --- | --- | --- |
| `id` | SERIAL PK | Unique user ID | —   | `{user_id}` |
| `name` | VARCHAR(100) | User’s full name | Input on registration/profile update | Returned in profile/tickets |
| `phone` | VARCHAR(11), UNIQUE | Login credential | Input on registration/login | Returned in profile |
| `password_hash` | VARCHAR(255) | Encrypted password | Sent as `password` → hashed in backend | ❌ never returned |
| `nid` | VARCHAR(20) | National ID | Input on signup (hidden in APIs) | ❌ never returned |
| `role` | ENUM(passenger, supervisor, owner) | Defines permissions | Sent in registration | Returned in profile |
| `is_active` | BOOLEAN | Soft delete flag | —   | Backend only |
| `created_at`, `updated_at` | TIMESTAMP | Audit fields | —   | Backend only |

* * *

## 2\. **Buses**

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
| --- | --- | --- | --- | --- |
| `id` | SERIAL PK | Bus ID | —   | `{bus_id}` |
| `bus_number` | VARCHAR(20), UNIQUE | Bus plate/identifier | Input when Owner/Supervisor adds bus | Returned in full details |
| `route_from` | VARCHAR(100) | Starting point | Input on bus add | Returned in search & details |
| `route_to` | VARCHAR(100) | Ending point | Input on bus add | Returned in search & details |
| `departure_time` | TIMESTAMP | Departure time | Input on bus add | Returned in search & details |
| `bus_type` | ENUM(AC, Non-AC, AC Sleeper) | Bus category | Input on bus add | Returned in search & details |
| `fare` | DECIMAL(10,2) | Price per seat | Input on bus add | Returned in search & ticket |
| `seat_capacity` | INT | Total seats | Input on bus add | Backend only (except owner view) |
| `available_seats` | INT | Seats left | Auto-managed by triggers | Returned in search |
| `owner_id` | INT FK → users(id) | Owner of bus | Set by backend | Backend only |
| `supervisor_id` | INT FK → users(id) | Assigned supervisor | Input when assigning | Backend only (owner panel) |
| `current_lat`, `current_lng` | DECIMAL | Live bus position | Updated by supervisor app | Returned on map |
| `last_location_update` | TIMESTAMP | Last GPS ping | Auto-set | Backend only |
| `is_active` | BOOLEAN | Bus enabled/disabled | —   | Backend only |
| `created_at`, `updated_at` | TIMESTAMP | Audit fields | —   | Backend only |

* * *

## 3\. **Boarding Points**

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
| --- | --- | --- | --- | --- |
| `id` | SERIAL PK | Boarding point ID | —   | `{boarding_point_id}` |
| `bus_id` | INT FK → buses(id) | Belongs to bus | Auto from frontend’s bus selection | Backend only |
| `name` | VARCHAR(100) | Stop name | Supervisor adds | Passenger sees list after acceptance |
| `lat`, `lng` | DECIMAL | GPS location | Supervisor adds | Passenger sees on map |
| `sequence_order` | INT | Boarding order | Supervisor sets | Supervisor/Passenger see ordered list |
| `created_at` | TIMESTAMP | Audit field | —   | Backend only |

* * *

## 4\. **Bookings**

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
| --- | --- | --- | --- | --- |
| `id` | SERIAL PK | Booking ID | —   | `{booking_id}` |
| `passenger_id` | INT FK → users(id) | Who requested | Auto from logged-in passenger | Shown to supervisor only **after acceptance** |
| `bus_id` | INT FK → buses(id) | Which bus | Passenger sends in booking request | Backend only |
| `status` | ENUM(pending, accepted, rejected, cancelled) | Booking state | Auto default `pending`, updated by supervisor | Returned in booking flow |
| `request_time` | TIMESTAMP | Request timestamp | Auto | Passenger sees (history) |
| `accepted_time`, `rejected_time`, `cancelled_time` | TIMESTAMP | State transitions | Auto | Backend only |
| `rejection_reason`, `cancellation_reason` | TEXT | Why cancelled | Supervisor/passenger input | Returned if exists |
| `created_at`, `updated_at` | TIMESTAMP | Audit fields | —   | Backend only |

* * *

## 5\. **Tickets**

| Field | Type | Purpose | Frontend → Backend | Backend → Frontend |
| --- | --- | --- | --- | --- |
| `id` | SERIAL PK | Ticket ID | —   | `{ticket_id}` |
| `booking_id` | INT FK → bookings(id) | Parent booking | Passenger sends | Backend only |
| `boarding_point_id` | INT FK → boarding_points(id) | Where to board | Passenger selects after acceptance | Returned in confirmed ticket |
| `seats_booked` | INT | Seat count | Passenger sends | Returned in ticket |
| `fare_per_seat` | DECIMAL(10,2) | Price | Auto from bus.fare | Returned in ticket |
| `total_fare` | DECIMAL(10,2) | seats × fare | Auto-calculated | Returned in ticket |
| `status` | ENUM(confirmed, completed, cancelled) | Ticket state | Auto default `confirmed` | Returned in ticket |
| `created_at` | TIMESTAMP | When ticket issued | Auto | Passenger sees issue date |
| `completed_at`, `cancelled_at` | TIMESTAMP | Status transitions | Auto | Passenger sees if completed/cancelled |
| `updated_at` | TIMESTAMP | Audit field | —   | Backend only |

* * *

## 🔄 How Data Flows

- **Passenger Registration/Login** → writes to `users` (role = passenger).
    
- **Owner adds bus** → writes to `buses` (linked to owner).
    
- **Supervisor adds boarding points** → writes to `boarding_points`.
    
- **Passenger requests booking** → writes to `bookings` (status = pending).
    
- **Supervisor accepts booking** → updates `bookings.status = accepted`.
    
- **Passenger confirms ticket** → writes to `tickets` (calculates fare, updates `buses.available_seats`).
    
- **Live location updates** → supervisor updates `buses.current_lat/lng`, passengers receive via WebSocket.