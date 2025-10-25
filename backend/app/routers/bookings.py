from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.bus import Bus
from app.models.booking import Booking, BookingStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.boarding_point import BoardingPoint
from app.schemas.booking import (
    BookingRequestCreate,
    BookingAcceptRequest,
    BookingRejectRequest,
    BookingCancelRequest,
    BookingBasicResponse,
    BookingDetailedResponse,
    BookingAcceptanceResponse,
    BookingStatusResponse
)
from app.schemas.ticket import (
    TicketConfirmRequest,
    TicketCancelRequest,
    TicketResponse,
    TicketConfirmResponse,
    TicketStatusResponse
)
from app.dependencies import (
    get_current_user,
    get_current_passenger,
    get_current_supervisor
)

router = APIRouter(prefix="/booking", tags=["Booking Management"])


@router.post("/request", response_model=BookingStatusResponse, status_code=status.HTTP_201_CREATED)
def create_booking_request(
    booking_data: BookingRequestCreate,
    current_user: User = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Send a booking request (PASSENGER only)
    
    Creates a pending booking request for a specific bus.
    Passenger details are not shown to supervisor until accepted.
    """
    # Verify bus exists and is active
    bus = db.query(Bus).filter(Bus.id == booking_data.bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found"
        )
    
    if not bus.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bus is no longer available"
        )
    
    # Check if user already has a pending/accepted booking for this bus
    existing_booking = db.query(Booking).filter(
        Booking.passenger_id == current_user.id,
        Booking.bus_id == booking_data.bus_id,
        Booking.status.in_([BookingStatus.pending, BookingStatus.accepted])
    ).first()
    
    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a booking request for this bus"
        )
    
    # Create new booking request
    new_booking = Booking(
        passenger_id=current_user.id,
        bus_id=booking_data.bus_id,
        status=BookingStatus.pending
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return BookingStatusResponse(
        booking_id=new_booking.id,
        status=new_booking.status,
        message="Booking request sent successfully"
    )


@router.get("/requests", response_model=List[BookingBasicResponse])
def get_booking_requests(
    bus_id: Optional[int] = Query(None, description="Filter by bus ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """
    View pending booking requests (SUPERVISOR only)
    
    Returns basic booking info without passenger details.
    Passenger details are only shown after acceptance.
    """
    # Build query - only pending requests
    query = db.query(Booking).filter(Booking.status == BookingStatus.pending)
    
    # Filter by bus_id if supervisor is assigned to specific buses
    if bus_id:
        query = query.filter(Booking.bus_id == bus_id)
        # Verify supervisor has access to this bus
        bus = db.query(Bus).filter(Bus.id == bus_id).first()
        if bus and bus.supervisor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to bookings for this bus"
            )
    else:
        # If no bus_id specified, only show buses assigned to this supervisor
        query = query.join(Bus).filter(Bus.supervisor_id == current_user.id)
    
    # Apply pagination
    offset = (page - 1) * limit
    bookings = query.offset(offset).limit(limit).all()
    
    return [BookingBasicResponse.model_validate(booking) for booking in bookings]


@router.post("/accept", response_model=BookingAcceptanceResponse)
def accept_booking(
    accept_data: BookingAcceptRequest,
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """
    Accept a booking request (SUPERVISOR only)
    
    Changes booking status to accepted and returns passenger details
    along with available boarding points.
    """
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == accept_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify supervisor has access to this bus
    bus = db.query(Bus).filter(Bus.id == booking.bus_id).first()
    if not bus or bus.supervisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage bookings for this bus"
        )
    
    # Check if booking is still pending
    if booking.status != BookingStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking is already {booking.status.value}"
        )
    
    # Check if bus has available seats
    if bus.available_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No seats available on this bus"
        )
    
    # Update booking status
    booking.status = BookingStatus.accepted
    booking.accepted_time = datetime.utcnow()
    
    # Get passenger details
    passenger = db.query(User).filter(User.id == booking.passenger_id).first()
    
    # Get available boarding points for this bus
    boarding_points = db.query(BoardingPoint).filter(
        BoardingPoint.bus_id == booking.bus_id
    ).order_by(BoardingPoint.sequence_order).all()
    
    boarding_points_data = [
        {
            "id": bp.id,
            "name": bp.name,
            "lat": float(bp.lat),
            "lng": float(bp.lng),
            "sequence_order": bp.sequence_order
        }
        for bp in boarding_points
    ]
    
    db.commit()
    
    return BookingAcceptanceResponse(
        booking_id=booking.id,
        status=booking.status,
        passenger_name=passenger.name,
        passenger_phone=passenger.phone,
        available_boarding_points=boarding_points_data
    )


@router.post("/reject", response_model=BookingStatusResponse)
def reject_booking(
    reject_data: BookingRejectRequest,
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """
    Reject a booking request (SUPERVISOR only)
    
    Changes booking status to rejected with optional reason.
    """
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == reject_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify supervisor has access to this bus
    bus = db.query(Bus).filter(Bus.id == booking.bus_id).first()
    if not bus or bus.supervisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage bookings for this bus"
        )
    
    # Check if booking is still pending
    if booking.status != BookingStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking is already {booking.status.value}"
        )
    
    # Update booking status
    booking.status = BookingStatus.rejected
    booking.rejected_time = datetime.utcnow()
    booking.rejection_reason = reject_data.reason
    
    db.commit()
    
    return BookingStatusResponse(
        booking_id=booking.id,
        status=booking.status,
        message="Booking rejected successfully"
    )


@router.post("/cancel", response_model=BookingStatusResponse)
def cancel_booking(
    cancel_data: BookingCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking (PASSENGER or SUPERVISOR)
    
    Passengers can cancel their own bookings.
    Supervisors can cancel bookings for their assigned buses.
    """
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == cancel_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    is_passenger = (
        current_user.role.value == "passenger" and 
        booking.passenger_id == current_user.id
    )
    
    bus = db.query(Bus).filter(Bus.id == booking.bus_id).first()
    is_supervisor = (
        current_user.role.value == "supervisor" and 
        bus and bus.supervisor_id == current_user.id
    )
    
    if not (is_passenger or is_supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this booking"
        )
    
    # Check if booking can be cancelled
    if booking.status in [BookingStatus.rejected, BookingStatus.cancelled]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking is already {booking.status.value}"
        )
    
    # If ticket exists, cancel it first
    ticket = db.query(Ticket).filter(Ticket.booking_id == booking.id).first()
    if ticket and ticket.status == TicketStatus.confirmed:
        ticket.status = TicketStatus.cancelled
        ticket.cancelled_at = datetime.utcnow()
        
        # Restore available seats
        bus.available_seats += ticket.seats_booked
    
    # Update booking status
    booking.status = BookingStatus.cancelled
    booking.cancelled_time = datetime.utcnow()
    booking.cancellation_reason = cancel_data.reason
    
    db.commit()
    
    return BookingStatusResponse(
        booking_id=booking.id,
        status=booking.status,
        message="Booking cancelled successfully"
    )


@router.post("/ticket/confirm", response_model=TicketConfirmResponse, status_code=status.HTTP_201_CREATED)
def confirm_ticket(
    ticket_data: TicketConfirmRequest,
    current_user: User = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Confirm ticket details after booking acceptance (PASSENGER only)
    
    Creates a confirmed ticket with boarding point and seat count.
    """
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == ticket_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify passenger owns this booking
    if booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to confirm this booking"
        )
    
    # Check if booking is accepted
    if booking.status != BookingStatus.accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be accepted before confirming ticket"
        )
    
    # Check if ticket already exists
    existing_ticket = db.query(Ticket).filter(Ticket.booking_id == booking.id).first()
    if existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already confirmed for this booking"
        )
    
    # Get bus and boarding point
    bus = db.query(Bus).filter(Bus.id == booking.bus_id).first()
    boarding_point = db.query(BoardingPoint).filter(
        BoardingPoint.id == ticket_data.boarding_point_id,
        BoardingPoint.bus_id == booking.bus_id
    ).first()
    
    if not boarding_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding point not found for this bus"
        )
    
    # Check seat availability
    if bus.available_seats < ticket_data.seats_booked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {bus.available_seats} seats available"
        )
    
    # Create ticket
    new_ticket = Ticket(
        booking_id=booking.id,
        boarding_point_id=ticket_data.boarding_point_id,
        seats_booked=ticket_data.seats_booked,
        fare_per_seat=bus.fare,
        total_fare=bus.fare * ticket_data.seats_booked,
        status=TicketStatus.confirmed
    )
    
    # Update available seats
    bus.available_seats -= ticket_data.seats_booked
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    # Prepare response data
    boarding_point_data = {
        "id": boarding_point.id,
        "name": boarding_point.name,
        "lat": float(boarding_point.lat),
        "lng": float(boarding_point.lng),
        "sequence_order": boarding_point.sequence_order
    }
    
    bus_details = {
        "bus_number": bus.bus_number,
        "route_from": bus.route_from,
        "route_to": bus.route_to,
        "departure_time": bus.departure_time
    }
    
    return TicketConfirmResponse(
        ticket_id=new_ticket.id,
        status=new_ticket.status,
        seats_booked=new_ticket.seats_booked,
        total_fare=new_ticket.total_fare,
        boarding_point=boarding_point_data,
        bus_details=bus_details,
        message="Ticket confirmed successfully"
    )


@router.get("/tickets/mine", response_model=List[TicketResponse])
def get_my_tickets(
    status_filter: Optional[str] = Query(None, description="Filter by ticket status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Get my tickets (PASSENGER only)
    
    Returns all tickets for the current passenger.
    """
    # Build query
    query = db.query(Ticket).join(Booking).filter(Booking.passenger_id == current_user.id)
    
    # Apply status filter
    if status_filter:
        try:
            ticket_status = TicketStatus(status_filter)
            query = query.filter(Ticket.status == ticket_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )
    
    # Apply pagination
    offset = (page - 1) * limit
    tickets = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    ticket_responses = []
    for ticket in tickets:
        ticket_data = TicketResponse.model_validate(ticket)
        ticket_responses.append(ticket_data)
    
    return ticket_responses


@router.post("/ticket/cancel", response_model=TicketStatusResponse)
def cancel_ticket(
    cancel_data: TicketCancelRequest,
    current_user: User = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Cancel a confirmed ticket (PASSENGER only)
    
    Cancels a ticket and restores available seats.
    """
    # Get the ticket
    ticket = db.query(Ticket).filter(Ticket.id == cancel_data.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Verify passenger owns this ticket
    booking = db.query(Booking).filter(Booking.id == ticket.booking_id).first()
    if not booking or booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this ticket"
        )
    
    # Check if ticket can be cancelled
    if ticket.status != TicketStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket is already {ticket.status.value}"
        )
    
    # Update ticket status
    ticket.status = TicketStatus.cancelled
    ticket.cancelled_at = datetime.utcnow()
    
    # Restore available seats
    bus = db.query(Bus).filter(Bus.id == booking.bus_id).first()
    if bus:
        bus.available_seats += ticket.seats_booked
    
    # Cancel the associated booking as well
    booking.status = BookingStatus.cancelled
    booking.cancelled_time = datetime.utcnow()
    booking.cancellation_reason = cancel_data.reason
    
    db.commit()
    
    return TicketStatusResponse(
        ticket_id=ticket.id,
        status=ticket.status,
        message="Ticket cancelled successfully"
    )
