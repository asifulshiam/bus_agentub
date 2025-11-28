# Bus AgentUB 🚌

A modern bus ticketing system connecting passengers, bus staff, and bus owners in real-time.

---

## What is This?

Imagine booking a bus ticket as easy as ordering food online. That's Bus AgentUB.

**The Problem We Solve:**
- Passengers struggle to find and book intercity buses
- Bus staff manage bookings manually with phone calls
- Owners can't track their buses and revenue in real-time

**Our Solution:**
- **Passengers:** Search buses, book seats, track live bus location
- **Supervisors** (Bus Staff): Manage bookings, update location, handle passengers
- **Owners:** Monitor all buses, view sales reports, manage staff

---

## How It Works

### 1. Passenger Journey
```
Search buses → Send booking request → Wait for approval → 
Choose seats & boarding point → Get confirmed ticket → Track bus live
```

**Key Feature:** Passenger details stay private until supervisor approves the booking.

### 2. Supervisor (Bus Staff) Journey
```
See booking requests → Accept/Reject → View passenger details → 
Update bus location → Manage boarding
```

**Key Feature:** See only booking existence initially, full details appear after acceptance.

### 3. Owner Journey
```
Add buses → Register supervisors → Monitor bookings → 
View revenue reports → Track all operations
```

**Key Feature:** Complete dashboard showing all buses, bookings, and earnings.

---

## Technology

**Built With:**
- **Backend:** Python (FastAPI) - The server that handles all requests
- **Database:** PostgreSQL - Where all data is securely stored
- **Hosting:** Railway - Cloud platform for 24/7 availability
- **Maps:** OpenStreetMap - Free, open-source maps for location features
- **Real-time:** WebSockets - Live updates without refreshing

**Frontend (Coming Soon):**
- Flutter mobile apps for Passengers & Supervisors
- Flutter web dashboard for Owners

---

## Key Features

### Privacy First
- Passenger phone numbers hidden until booking approved
- National IDs never exposed in API responses
- Secure authentication with 7-day session tokens

### Smart Booking Flow
1. **Request:** Passenger sends simple booking request (just bus selection)
2. **Review:** Supervisor sees request without passenger details
3. **Approval:** Supervisor accepts → passenger details revealed
4. **Confirmation:** Passenger selects exact seats and boarding point
5. **Ticket:** Digital ticket generated with all details

### Real-Time Features
- Live bus location tracking on map
- Instant booking status updates
- Real-time seat availability

### Owner Benefits
- Dashboard with key metrics (buses, bookings, revenue)
- Detailed sales reports by date and bus
- Supervisor management system
- Complete ownership verification (supervisors can't self-register)

---

## User Roles Explained

### 👤 Passenger (Bus Rider)
**Can Do:**
- Search for buses by route and date
- Send booking requests
- Choose seats and boarding points (after approval)
- View confirmed tickets
- Track bus location in real-time
- Cancel bookings

**Cannot Do:**
- See bus details before booking is accepted
- Book without approval
- Access supervisor or owner features

### 🧑‍✈️ Supervisor (Bus Staff)
**Can Do:**
- View all booking requests for their buses
- Accept or reject bookings
- See passenger details after accepting
- Update live bus GPS location
- Manage boarding points
- View passenger list with boarding sequence

**Cannot Do:**
- Self-register (must be registered by owner)
- Access owner dashboard
- Manage other buses

### 👔 Owner (Bus Company)
**Can Do:**
- Register and manage buses
- Create supervisor accounts
- View complete dashboard
- Monitor all bookings and tickets
- Generate revenue reports
- Assign supervisors to buses

**Has Access To:**
- All bus operations
- Sales analytics
- Supervisor management
- Complete system overview

---

## Data Flow Example

**Scenario:** Sarah wants to travel from Dhaka to Chittagong

1. **Sarah searches** for buses:
   - Sees: Route, time, type (AC/Non-AC), price, available seats
   - Doesn't see: Supervisor details, boarding points (privacy!)

2. **Sarah requests booking** for Bus #123:
   - System creates pending booking
   - Supervisor Ahmed gets notification
   - Ahmed sees: "1 new booking request" (no passenger details yet)

3. **Ahmed accepts** the booking:
   - System reveals: Sarah's name and phone to Ahmed
   - Sarah gets notification: "Booking accepted!"
   - Sarah now sees: Boarding points list, full bus details

4. **Sarah confirms** ticket:
   - Chooses: 2 seats, Mohakhali boarding point
   - System generates ticket with total fare
   - Bus seat count auto-updates

5. **Journey day:**
   - Sarah tracks bus live on map
   - Sees ETA to her boarding point
   - Ahmed manages all passengers' boarding sequence

---

## Technical Architecture

```
Frontend Apps → API Gateway → Backend (FastAPI) → Database (PostgreSQL)
                    ↓
            WebSocket Server (Real-time updates)
                    ↓
            OpenStreetMap APIs (Location services)
```

### Security Layers
1. JWT authentication (7-day tokens)
2. Role-based access control
3. Password hashing (bcrypt)
4. Input validation on all endpoints
5. CORS protection
6. SQL injection prevention

---

## Project Structure

```
bus_agentub/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── models/   # Database tables
│   │   ├── routers/  # API endpoints
│   │   └── schemas/  # Data validation
│   └── requirements.txt
├── frontend/         # Flutter apps (coming soon)
├── docs/            # Technical documentation
│   ├── api_contract.md      # Complete API reference
│   ├── db_schema.md         # Database structure
│   └── db_api_mapping.md    # Data flow diagrams
└── README.md        # This file
```

---

## For Developers

**API Documentation:** See `docs/api_contract.md` for complete endpoint reference

**Quick Test:**
```bash
# Health check
curl https://web-production-9625a.up.railway.app/

# Search buses
curl https://web-production-9625a.up.railway.app/buses?route_from=Dhaka&route_to=Chittagong

# Interactive API testing
Visit: https://web-production-9625a.up.railway.app/docs
```

**Tech Stack Details:**
- **Language:** Python 3.12
- **Framework:** FastAPI 0.104.1
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 16
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Validation:** Pydantic v2
- **WebSocket:** Native FastAPI WebSockets
- **Maps:** Nominatim (geocoding), OSRM (routing), Overpass (places)

---

## Deployment

**Platform:** Railway  
**Auto-deploy:** Enabled from GitHub main branch  
**Database:** Managed PostgreSQL on Railway  
**Environment:** Production-ready with monitoring

**Deploy Process:**
```bash
git push origin main
# Railway automatically deploys in ~2 minutes
```
