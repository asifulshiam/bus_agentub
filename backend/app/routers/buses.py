from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.database import get_db
from app.dependencies import get_current_owner, get_current_user
from app.models import User
from app.models.boarding_point import BoardingPoint
from app.models.bus import Bus, BusType
from app.models.enums import UserRole
from app.models.user import User, UserRole
from app.schemas.boarding_point import BoardingPointCreate, BoardingPointResponse
from app.schemas.bus import BusCreate, BusDetailedResponse, BusPublicResponse, BusUpdate

router = APIRouter(prefix="/buses", tags=["Bus Management"])


@router.get("", response_model=List[BusPublicResponse])
def search_buses(
    route_from: Optional[str] = Query(None, description="Departure city"),
    route_to: Optional[str] = Query(None, description="Destination city"),
    bus_type: Optional[BusType] = Query(None, description="Bus type filter"),
    min_fare: Optional[float] = Query(None, ge=0, description="Minimum fare"),
    max_fare: Optional[float] = Query(None, ge=0, description="Maximum fare"),
    min_seats: Optional[int] = Query(None, ge=1, description="Minimum available seats"),
    date: Optional[str] = Query(None, description="Departure date (YYYY-MM-DD)"),
    sort_by: str = Query("departure_time", regex="^(fare|departure_time)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """
    Search for available buses (PUBLIC - no authentication required)

    Returns basic bus information without supervisor contact details.
    Supports filtering by route, type, fare, seats, and date.
    """
    # Start with base query - only active buses
    query = db.query(Bus).filter(Bus.is_active == True)

    # Apply filters
    if route_from:
        query = query.filter(Bus.route_from.ilike(f"%{route_from}%"))

    if route_to:
        query = query.filter(Bus.route_to.ilike(f"%{route_to}%"))

    if bus_type:
        query = query.filter(Bus.bus_type == bus_type)

    if min_fare is not None:
        query = query.filter(Bus.fare >= min_fare)

    if max_fare is not None:
        query = query.filter(Bus.fare <= max_fare)

    if min_seats is not None:
        query = query.filter(Bus.available_seats >= min_seats)

    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            # Filter buses departing on this date
            query = query.filter(db.func.date(Bus.departure_time) == date_obj.date())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            )

    # Apply sorting
    if sort_by == "fare":
        query = query.order_by(Bus.fare.desc() if order == "desc" else Bus.fare.asc())
    else:  # departure_time
        query = query.order_by(
            Bus.departure_time.desc() if order == "desc" else Bus.departure_time.asc()
        )

    buses = query.all()
    return [BusPublicResponse.model_validate(bus) for bus in buses]


@router.post(
    "", response_model=BusDetailedResponse, status_code=status.HTTP_201_CREATED
)
def create_bus(
    bus_data: BusCreate,
    current_user: User = Depends(get_current_owner),  # Only owners!
    db: Session = Depends(get_db),
):
    """
    Create a new bus (OWNER only)

    - Only owners can create buses
    - Owner becomes the bus owner automatically
    - Owner can assign a supervisor during creation
    """

    # Check if bus number already exists
    existing_bus = db.query(Bus).filter(Bus.bus_number == bus_data.bus_number).first()
    if existing_bus:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bus number {bus_data.bus_number} already exists",
        )

    # Validate route (from and to must be different)
    if bus_data.route_from.lower() == bus_data.route_to.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departure and destination cities must be different",
        )

    # ✅ UPDATED: Validate supervisor belongs to this owner
    if bus_data.supervisor_id:
        supervisor = (
            db.query(User)
            .filter(
                User.id == bus_data.supervisor_id,
                User.role == UserRole.SUPERVISOR,
                User.owner_id == current_user.id,  # ✅ Must be hired by this owner
            )
            .first()
        )

        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign supervisor. Either they don't exist or were not hired by you.",
            )

    # Create new bus
    new_bus = Bus(
        bus_number=bus_data.bus_number,
        route_from=bus_data.route_from,
        route_to=bus_data.route_to,
        departure_time=bus_data.departure_time,
        bus_type=bus_data.bus_type,
        fare=bus_data.fare,
        seat_capacity=bus_data.seat_capacity,
        available_seats=bus_data.seat_capacity,  # Initially all seats available
        owner_id=current_user.id,
        supervisor_id=bus_data.supervisor_id,
        is_active=True,
    )

    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)

    return BusDetailedResponse.model_validate(new_bus)


@router.get("/{bus_id}", response_model=BusDetailedResponse)
def get_bus_details(
    bus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed bus information (AUTHENTICATED)

    Shows full details including supervisor contact and boarding points.
    In production, this would only show full details after booking acceptance.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found",
        )

    # Check if bus is active
    if not bus.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bus is no longer available"
        )

    return BusDetailedResponse.model_validate(bus)


@router.put("/{bus_id}", response_model=BusDetailedResponse)
def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update bus information (OWNER or ASSIGNED SUPERVISOR only)

    - Owner can update their own buses
    - Assigned supervisor can update their assigned bus
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found",
        )

    # Check permissions
    is_owner = current_user.id == bus.owner_id
    is_assigned_supervisor = (
        current_user.role.value == "supervisor" and current_user.id == bus.supervisor_id
    )

    if not (is_owner or is_assigned_supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this bus",
        )

    # Update fields if provided
    update_data = bus_data.model_dump(exclude_unset=True)

    # Validate bus_number uniqueness if being updated
    if "bus_number" in update_data:
        existing = (
            db.query(Bus)
            .filter(Bus.bus_number == update_data["bus_number"], Bus.id != bus_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bus number {update_data['bus_number']} already exists",
            )

    # Validate route if both are being updated or check against existing
    if "route_from" in update_data or "route_to" in update_data:
        new_from = update_data.get("route_from", bus.route_from)
        new_to = update_data.get("route_to", bus.route_to)
        if new_from.lower() == new_to.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Departure and destination cities must be different",
            )

    # ✅ UPDATED: Validate supervisor ownership if provided
    if "supervisor_id" in update_data and update_data["supervisor_id"]:
        supervisor = (
            db.query(User)
            .filter(
                User.id == update_data["supervisor_id"],
                User.role == UserRole.SUPERVISOR,
                User.owner_id == bus.owner_id,  # ✅ Must belong to bus owner
            )
            .first()
        )

        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign supervisor. Either they don't exist or were not hired by you.",
            )

    # Update seat capacity logic
    if "seat_capacity" in update_data:
        booked_seats = bus.seat_capacity - bus.available_seats
        new_capacity = update_data["seat_capacity"]

        if new_capacity < booked_seats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reduce capacity below {booked_seats} (already booked seats)",
            )

        # Update available seats proportionally
        update_data["available_seats"] = new_capacity - booked_seats

    # Apply updates
    for key, value in update_data.items():
        setattr(bus, key, value)

    db.commit()
    db.refresh(bus)

    return BusDetailedResponse.model_validate(bus)


@router.delete("/{bus_id}", status_code=status.HTTP_200_OK)
def delete_bus(
    bus_id: int,
    current_user: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    """
    Delete (deactivate) a bus (OWNER only)

    Performs soft delete by setting is_active to False.
    Only the bus owner can delete their bus.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found",
        )

    # Check if current user is the owner
    if current_user.id != bus.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the bus owner can delete this bus",
        )

    # Check if already deleted
    if not bus.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bus is already inactive"
        )

    # Soft delete
    bus.is_active = False
    db.commit()

    return {
        "message": f"Bus {bus.bus_number} has been deactivated successfully",
        "bus_id": bus_id,
    }


@router.post(
    "/{bus_id}/stops",
    response_model=BoardingPointResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_boarding_point(
    bus_id: int,
    stop_data: BoardingPointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a boarding point to a bus (OWNER or ASSIGNED SUPERVISOR only)

    - Sequence order must be unique per bus
    - GPS coordinates validated by schema
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found",
        )

    # Check permissions
    is_owner = current_user.id == bus.owner_id
    is_assigned_supervisor = (
        current_user.role.value == "supervisor" and current_user.id == bus.supervisor_id
    )

    if not (is_owner or is_assigned_supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add boarding points to this bus",
        )

    # Check if sequence order already exists for this bus
    existing_stop = (
        db.query(BoardingPoint)
        .filter(
            BoardingPoint.bus_id == bus_id,
            BoardingPoint.sequence_order == stop_data.sequence_order,
        )
        .first()
    )

    if existing_stop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A boarding point with sequence order {stop_data.sequence_order} already exists for this bus",
        )

    # Create new boarding point
    new_stop = BoardingPoint(
        bus_id=bus_id,
        name=stop_data.name,
        lat=stop_data.lat,
        lng=stop_data.lng,
        sequence_order=stop_data.sequence_order,
    )

    db.add(new_stop)
    db.commit()
    db.refresh(new_stop)

    return BoardingPointResponse.model_validate(new_stop)


@router.get("/{bus_id}/stops", response_model=List[BoardingPointResponse])
def get_boarding_points(bus_id: int, db: Session = Depends(get_db)):
    """
    Get all boarding points for a bus (PUBLIC after booking acceptance)

    Returns boarding points ordered by sequence.
    In production, this would require booking acceptance first.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found",
        )

    # Get boarding points ordered by sequence
    stops = (
        db.query(BoardingPoint)
        .filter(BoardingPoint.bus_id == bus_id)
        .order_by(BoardingPoint.sequence_order)
        .all()
    )

    return [BoardingPointResponse.model_validate(stop) for stop in stops]
