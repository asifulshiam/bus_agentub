## **API Contract Table**

| Module | Endpoint | Method | Auth Required | Purpose | Query/Body Params | Response |
| --- | --- | --- | --- | --- | --- | --- |
| **User** | `/auth/register` | POST | No  | Register user | Body: `{name, phone, password, role}` | `{user_id, token}` |
| **User** | `/auth/login` | POST | No  | Login with phone+password | Body: `{phone, password}` | `{user_id, name, role, token}` |
| **User** | `/auth/profile` | GET | Yes | Get user profile | \-  | `{user_id, name, phone, role}` |
| **User** | `/auth/profile` | PUT | Yes | Update profile | Body: `{name}` | `{user_id, name, phone}` |
| **Bus** | `/buses` | GET | No  | Search buses | Query: `?from=&to=&date=` | `[{bus_id, route_from, route_to, departure_time, bus_type, fare, available_seats}]` |
| **Bus** | `/buses` | POST | Yes (Owner/Supervisor) | Add new bus | Body: `{bus_number, route_from, route_to, departure_time, bus_type, fare, seat_capacity}` | `{bus_id, message}` |
| **Bus** | `/buses/{id}` | GET | Yes (after booking accepted) | Get full bus details | \-  | `{bus_id, bus_number, ..., boarding_points, live_location}` |
| **Bus** | `/buses/{id}` | PUT | Yes (Owner/Supervisor) | Update bus | Body: `{fare?, available_seats?}` | `{bus_id, message}` |
| **Bus** | `/buses/{id}` | DELETE | Yes (Owner/Supervisor) | Delete bus | \-  | `{message}` |
| **Bus** | `/buses/{id}/stops` | POST | Yes (Supervisor) | Add boarding point | Body: `{name, lat, lng}` | `{stop_id, message}` |
| **Bus** | `/buses/{id}/stops` | GET | Yes (after booking accepted) | Get boarding points | \-  | `[{id, name, lat, lng}]` |
| **Booking** | `/booking/request` | POST | Yes (Passenger) | Send booking request | Body: `{bus_id}` | `{booking_id, status: "pending"}` |
| **Booking** | `/booking/requests` | GET | Yes (Supervisor) | View pending requests | Query: `?bus_id=&page=1&limit=20` | `[{booking_id, bus_id, status, request_time}]` (NO passenger details) |
| **Booking** | `/booking/accept` | POST | Yes (Supervisor) | Accept booking | Body: `{booking_id}` | `{booking_id, status: "accepted", passenger_name, passenger_phone, available_boarding_points}` |
| **Booking** | `/booking/reject` | POST | Yes (Supervisor) | Reject booking | Body: `{booking_id, reason?}` | `{booking_id, status: "rejected"}` |
| **Booking** | `/ticket/confirm` | POST | Yes (Passenger) | Confirm ticket details | Body: `{booking_id, boarding_point_id, seats}` | `{ticket_id, status: "confirmed"}` |
| **Booking** | `/tickets/mine` | GET | Yes (Passenger) | Get my tickets | Query: `?status=confirmed&page=1` | `[{ticket_id, bus_id, departure_time, boarding_point, seats_booked}]` |
| **Real-Time** | `/ws/booking` | WebSocket | Yes | Booking status updates | \-  | Events: `booking_accepted`, `booking_rejected`, `ticket_confirmed` |
| **Real-Time** | `/ws/location/{bus_id}` | WebSocket | Yes (after acceptance) | Live bus location | \-  | Events: `location_update` with `{lat, lng}` |
| **Admin** | `/admin/dashboard` | GET | Yes (Owner) | Dashboard overview | \-  | `{total_buses, active_trips, total_bookings, total_revenue}` |
| **Admin** | `/admin/buses` | GET | Yes (Owner) | List all buses | Query: `?supervisor_id=&page=1` | `[{bus_id, bus_number, supervisor_name, bookings_count}]` |
| **Admin** | `/admin/tickets` | GET | Yes (Owner) | Ticket sales report | Query: `?from_date=&to_date=` | `{total_revenue, tickets_sold, breakdown_by_bus}` |

* * *

&nbsp;