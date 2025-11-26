from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_owner
from app.models.boarding_point import BoardingPoint
from app.models.booking import Booking, BookingStatus
from app.models.bus import Bus
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole
from app.schemas.bus import BusOwnerResponse
from app.schemas.user import UserRegister
from app.utils import hash_password

router = APIRouter(prefix="/owner", tags=["Owner Dashboard"])


@router.get("/dashboard")
def get_owner_dashboard(
    current_user: User = Depends(get_current_owner), db: Session = Depends(get_db)
):
    """
    Get owner dashboard overview (OWNER only)

    Returns summary statistics for buses, bookings, and revenue.
    """
    # Get total buses owned by this user
    total_buses = db.query(Bus).filter(Bus.owner_id == current_user.id).count()

    # Get active trips (buses with upcoming departures)
    active_trips = (
        db.query(Bus)
        .filter(
            Bus.owner_id == current_user.id,
            Bus.is_active == True,
            Bus.departure_time > datetime.utcnow(),
        )
        .count()
    )

    # Get total bookings across all buses
    total_bookings = (
        db.query(Booking).join(Bus).filter(Bus.owner_id == current_user.id).count()
    )

    # Get confirmed bookings
    confirmed_bookings = (
        db.query(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id, Booking.status == BookingStatus.accepted
        )
        .count()
    )

    # Get total revenue from confirmed tickets
    revenue_result = (
        db.query(func.sum(Ticket.total_fare))
        .join(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id, Ticket.status == TicketStatus.confirmed
        )
        .first()
    )

    total_revenue = float(revenue_result[0]) if revenue_result[0] else 0.0

    # Get today's revenue
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_revenue_result = (
        db.query(func.sum(Ticket.total_fare))
        .join(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id,
            Ticket.status == TicketStatus.confirmed,
            Ticket.created_at >= today_start,
        )
        .first()
    )

    today_revenue = float(today_revenue_result[0]) if today_revenue_result[0] else 0.0

    # Get pending bookings
    pending_bookings = (
        db.query(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id, Booking.status == BookingStatus.pending
        )
        .count()
    )

    return {
        "total_buses": total_buses,
        "active_trips": active_trips,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "pending_bookings": pending_bookings,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "dashboard_date": datetime.utcnow().isoformat(),
    }


@router.get("/buses", response_model=List[BusOwnerResponse])
def get_owner_buses(
    supervisor_id: Optional[int] = Query(None, description="Filter by supervisor ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    List all buses owned by the current user (OWNER only)

    Returns detailed bus information with booking counts and supervisor details.
    """
    # Build query
    query = db.query(Bus).filter(Bus.owner_id == current_user.id)

    # Filter by supervisor if specified
    if supervisor_id:
        query = query.filter(Bus.supervisor_id == supervisor_id)

    # Apply pagination
    offset = (page - 1) * limit
    buses = query.offset(offset).limit(limit).all()

    # Convert to response format with additional data
    bus_responses = []
    for bus in buses:
        # Get boarding points count
        boarding_points_count = (
            db.query(BoardingPoint).filter(BoardingPoint.bus_id == bus.id).count()
        )

        # Get total bookings count
        total_bookings = db.query(Booking).filter(Booking.bus_id == bus.id).count()

        # Get supervisor details
        supervisor = None
        if bus.supervisor_id:
            supervisor_user = (
                db.query(User).filter(User.id == bus.supervisor_id).first()
            )
            if supervisor_user:
                supervisor = {
                    "id": supervisor_user.id,
                    "name": supervisor_user.name,
                    "phone": supervisor_user.phone,
                }

        bus_data = BusOwnerResponse.model_validate(bus)
        bus_data.boarding_points_count = boarding_points_count
        bus_data.total_bookings = total_bookings
        bus_data.supervisor = supervisor

        bus_responses.append(bus_data)

    return bus_responses


@router.get("/tickets")
def get_ticket_sales_report(
    from_date: Optional[date] = Query(None, description="Start date for report"),
    to_date: Optional[date] = Query(None, description="End date for report"),
    bus_id: Optional[int] = Query(None, description="Filter by specific bus"),
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    Get ticket sales report (OWNER only)

    Returns revenue breakdown by bus and date range.
    """
    # Build query for tickets
    query = (
        db.query(Ticket)
        .join(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id, Ticket.status == TicketStatus.confirmed
        )
    )

    # Apply date filters
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time())
        query = query.filter(Ticket.created_at >= from_datetime)

    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time())
        query = query.filter(Ticket.created_at <= to_datetime)

    # Apply bus filter
    if bus_id:
        query = query.filter(Bus.id == bus_id)
        # Verify owner has access to this bus
        bus = (
            db.query(Bus)
            .filter(Bus.id == bus_id, Bus.owner_id == current_user.id)
            .first()
        )
        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found or access denied",
            )

    tickets = query.all()

    # Calculate totals
    total_revenue = sum(float(ticket.total_fare) for ticket in tickets)
    total_tickets = len(tickets)

    # Group by bus
    breakdown_by_bus = {}
    for ticket in tickets:
        bus = ticket.booking.bus
        bus_key = f"{bus.bus_number} ({bus.route_from} - {bus.route_to})"

        if bus_key not in breakdown_by_bus:
            breakdown_by_bus[bus_key] = {
                "bus_id": bus.id,
                "bus_number": bus.bus_number,
                "route": f"{bus.route_from} - {bus.route_to}",
                "tickets_sold": 0,
                "revenue": 0.0,
            }

        breakdown_by_bus[bus_key]["tickets_sold"] += ticket.seats_booked
        breakdown_by_bus[bus_key]["revenue"] += float(ticket.total_fare)

    return {
        "total_revenue": total_revenue,
        "total_tickets_sold": total_tickets,
        "date_range": {
            "from": from_date.isoformat() if from_date else None,
            "to": to_date.isoformat() if to_date else None,
        },
        "breakdown_by_bus": list(breakdown_by_bus.values()),
        "report_generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/supervisors", response_model=List[dict])
def get_owner_supervisors(
    current_user: User = Depends(get_current_owner), db: Session = Depends(get_db)
):
    """
    Get all supervisors hired by THIS owner (OWNER only)

    Returns only supervisors where owner_id matches current owner.
    """
    # ✅ FIXED: Only return supervisors hired by this owner
    supervisors = (
        db.query(User)
        .filter(
            User.role == UserRole.SUPERVISOR,
            User.owner_id == current_user.id,  # ✅ Filter by owner
            User.is_active == True,
        )
        .all()
    )

    result = []
    for supervisor in supervisors:
        # Get assigned buses
        assigned_buses = db.query(Bus).filter(Bus.supervisor_id == supervisor.id).all()

        result.append(
            {
                "id": supervisor.id,
                "name": supervisor.name,
                "phone": supervisor.phone,
                "is_active": supervisor.is_active,
                "assigned_buses": [
                    {"id": bus.id, "bus_number": bus.bus_number}
                    for bus in assigned_buses
                ],
            }
        )

    return result


@router.post("/register-supervisor")
def register_supervisor(
    supervisor_data: UserRegister,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    Owner registers a new supervisor and links them
    """
    # Check if phone already exists
    existing = db.query(User).filter(User.phone == supervisor_data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    # Create supervisor
    new_supervisor = User(
        name=supervisor_data.name,
        phone=supervisor_data.phone,
        password_hash=hash_password(supervisor_data.password),
        nid=supervisor_data.nid,
        role=UserRole.SUPERVISOR,
        owner_id=current_user.id,  # ✅ Link to hiring owner
        is_active=True,
    )

    db.add(new_supervisor)
    db.commit()
    db.refresh(new_supervisor)

    return {
        "message": "Supervisor registered successfully",
        "supervisor": {
            "id": new_supervisor.id,
            "name": new_supervisor.name,
            "phone": new_supervisor.phone,
        },
    }


@router.get("/bookings")
def get_owner_bookings(
    bus_id: Optional[int] = Query(None, description="Filter by bus ID"),
    status_filter: Optional[str] = Query(None, description="Filter by booking status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    Get all bookings for owner's buses (OWNER only)

    Returns booking details with passenger information.
    """
    # Build query
    query = db.query(Booking).join(Bus).filter(Bus.owner_id == current_user.id)

    # Apply filters
    if bus_id:
        query = query.filter(Booking.bus_id == bus_id)
        # Verify owner has access to this bus
        bus = (
            db.query(Bus)
            .filter(Bus.id == bus_id, Bus.owner_id == current_user.id)
            .first()
        )
        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found or access denied",
            )

    if status_filter:
        try:
            booking_status = BookingStatus(status_filter)
            query = query.filter(Booking.status == booking_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status filter"
            )

    # Apply pagination
    offset = (page - 1) * limit
    bookings = query.offset(offset).limit(limit).all()

    # Convert to response format
    booking_responses = []
    for booking in bookings:
        passenger = booking.passenger
        bus = booking.bus

        booking_data = {
            "id": booking.id,
            "bus_id": booking.bus_id,
            "bus_number": bus.bus_number,
            "route": f"{bus.route_from} - {bus.route_to}",
            "departure_time": bus.departure_time,
            "passenger_id": booking.passenger_id,
            "passenger_name": passenger.name,
            "passenger_phone": passenger.phone,
            "status": booking.status,
            "request_time": booking.request_time,
            "accepted_time": booking.accepted_time,
            "rejected_time": booking.rejected_time,
            "cancelled_time": booking.cancelled_time,
            "rejection_reason": booking.rejection_reason,
            "cancellation_reason": booking.cancellation_reason,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
        }

        booking_responses.append(booking_data)

    return booking_responses


@router.get("/revenue-summary")
def get_revenue_summary(
    period: str = Query(
        "month", regex="^(day|week|month|year)$", description="Revenue period"
    ),
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    Get revenue summary for different time periods (OWNER only)

    Returns revenue data grouped by the specified period.
    """
    # Calculate date range based on period
    now = datetime.utcnow()

    if period == "day":
        start_date = datetime.combine(now.date(), datetime.min.time())
        end_date = now
    elif period == "week":
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == "year":
        start_date = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end_date = now

    # Get tickets in the period
    tickets = (
        db.query(Ticket)
        .join(Booking)
        .join(Bus)
        .filter(
            Bus.owner_id == current_user.id,
            Ticket.status == TicketStatus.confirmed,
            Ticket.created_at >= start_date,
            Ticket.created_at <= end_date,
        )
        .all()
    )

    # Calculate totals
    total_revenue = sum(float(ticket.total_fare) for ticket in tickets)
    total_tickets = len(tickets)

    # Group by date
    revenue_by_date = {}
    for ticket in tickets:
        date_key = ticket.created_at.date().isoformat()

        if date_key not in revenue_by_date:
            revenue_by_date[date_key] = {"date": date_key, "revenue": 0.0, "tickets": 0}

        revenue_by_date[date_key]["revenue"] += float(ticket.total_fare)
        revenue_by_date[date_key]["tickets"] += ticket.seats_booked

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_revenue": total_revenue,
        "total_tickets": total_tickets,
        "revenue_by_date": list(revenue_by_date.values()),
        "average_ticket_value": total_revenue / total_tickets
        if total_tickets > 0
        else 0.0,
    }
