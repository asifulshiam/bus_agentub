## Passengers request tickets → Supervisors approve → Owners monitor sales.

## User Roles

### Passenger

- Search buses (visible: route, departure time, type, fare).
    
- Send booking requests (no boarding point or ticket count initially).
    
- Post-acceptance:
    
    - Select ticket count and boarding point (from list).
        
    - View full bus details and live location.
        
- Access confirmed tickets in **My Tickets** (includes boarding point).
    
### Supervisor (Bus Staff)

- Publish bus trips (route, departure time, type, fare, seat capacity, bus number) — only if bus is registered by Owner.
    
- Define boarding points (stop name, GPS coordinates).
    
- Accept/reject booking requests (pre-acceptance: sees only request existence).
    
- Post-acceptance:
    
    - View passenger details and boarding points.
        
    - Monitor seat selections.
        
- Share live bus location.
    
### Bus Owner

- Register buses (route, departure time, type, fare, seat capacity, bus number).
    
- Manage supervisors.
    
- Monitor bookings, sales, and all supervisor operations.
    
## Booking Flow

1.  **Search & Request**
    
    - Passenger searches buses (sees route, time, type, fare only)
        
    - Sends booking request (no seat count or boarding point yet).
        
2.  **Supervisor Review**
    
    - Supervisor sees request existence (no passenger details, seat count or boarding point)
        
    - Accepts or rejects request
        
3.  **Post-Acceptance**
    
    - Passenger: selects ticket count & boarding point, views full details and ETA (Google Maps API).
        
    - Supervisor: sees passenger details and boarding points.
        
4.  **Ticket Generation**
    
    - Ticket generated with ticket count and boarding point
        
    - Stored in Passenger’s “My Tickets”
        
    - Supervisor sees passenger list with boarding sequence.
        
## Tech Stack

- **Apps**: Flutter (Passenger & Supervisor)
    
- **Owner Panel**: Flutter/Flutter Web
    
- **Backend**: FastAPI (Python)
    
- **Database**: PostgreSQL
    
- **Real-Time**: WebSockets (booking updates, live location)
    
- **Maps**: Google Maps API
    
## Modules

### 1\. User Module

- **Roles**: Passenger, Supervisor, Owner.
    
- **Features**: Registration, login, profile management.
    
    - Passenger: name, phone, NID (not exposed in APIs).
        
    - Supervisor: name, phone, NID (not exposed in APIs), associated buses.
        
    - Owner: company info, manage buses & supervisors.
        
### 2\. Bus Module

- Add/Edit/Delete buses (Owner/Supervisor).
- Details: route, departure time, type, seat capacity, fare, bus number.
- Define boarding points (stop name + GPS).
- Provide searchable bus listings (route, time, fare).

### 3\. Booking Module

- Passenger: send booking request.
- Supervisor: accept/reject request.
- Post-acceptance: passenger selects seat count & boarding point → ticket generated.
- Track available seats.
- Supervisor: view passenger list + boarding sequence.

### 4\. Real-Time & Map Module

- WebSockets for booking and acceptance updates.
    
- Real-time bus location sharing (after acceptance).
    
- Google Maps integration:
    
    - Display live bus marker & route.
        
    - Highlight passenger’s boarding point.
        
    - Calculate ETA.
        
### 5\. Owner Module

- Dashboard: bus & booking summaries.
    
- Manage buses & supervisors.
    
- View ticket sales and passenger data.
    
* * *

## Screens

### Passenger App (Flutter)

- Registration/Login.
    
- Bus Search & Results (route, departure time, type, fare).
    
- Send Booking Request.
    
- Ticket Confirmation (post-acceptance): select seats & boarding point, view ETA.
    
- My Tickets: confirmed tickets.
    
- Real-Time Map: live bus & boarding point.
    
### Supervisor App (Flutter)

- Registration/Login.
    
- Published Buses (assigned).
    
- Manage Requests: view/accept/reject.
    
- Passenger List (confirmed bookings + boarding points).
    
- Real-Time Map (bus + boarding points).
    
### Owner Panel (Flutter Web)

- Dashboard: bus & booking overview.
    
- Manage buses & supervisors.
    
- Ticket sales & reports.

---

## 🚀 Production Deployment

**Backend API:** https://web-production-9625a.up.railway.app

**API Documentation:** https://web-production-9625a.up.railway.app/docs

**Status:** ✅ Live and operational

**Database:** PostgreSQL on Railway

**Last Deployed:** November 23, 2025

### For Frontend Developers
See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for complete API integration guide.

### Technology Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Deployment:** Railway (with auto-deploy from GitHub)
- **Maps:** OpenStreetMap (Nominatim, OSRM, Overpass API)
- **Real-time:** WebSockets for live location tracking
- **Authentication:** JWT tokens (7-day expiry)
