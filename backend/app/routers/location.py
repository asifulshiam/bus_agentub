from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.dependencies import get_current_supervisor, get_current_user
from app.models.boarding_point import BoardingPoint
from app.models.bus import Bus
from app.models.user import User
from app.routers.websocket import send_bus_location_update
from app.schemas.location import GeocodeRequest
from app.services.maps_service import maps_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/location", tags=["Location Services"])


@router.post("/bus/{bus_id}/update")
async def update_bus_location(
    bus_id: int,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db),
):
    """
    Update bus location (SUPERVISOR only)

    Updates the current location of a bus and broadcasts to connected clients.
    """
    # Get the bus
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found"
        )

    # Verify supervisor has access to this bus
    if bus.supervisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update location for this bus",
        )

    # Update bus location
    bus.current_lat = Decimal(str(lat))
    bus.current_lng = Decimal(str(lng))
    bus.last_location_update = datetime.utcnow()

    db.commit()

    # Broadcast location update to connected clients
    await send_bus_location_update(bus_id, lat, lng)

    return {
        "message": "Bus location updated successfully",
        "bus_id": bus_id,
        "location": {
            "lat": lat,
            "lng": lng,
            "updated_at": bus.last_location_update.isoformat(),
        },
    }


@router.get("/bus/{bus_id}")
def get_bus_location(
    bus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current bus location

    Returns the current location of a bus for authenticated users.
    """
    # Get the bus
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found"
        )

    # Check permissions
    has_access = False

    if current_user.role.value == "passenger":
        # Passenger needs accepted booking for this bus
        from app.models.booking import Booking, BookingStatus

        booking = (
            db.query(Booking)
            .filter(
                Booking.passenger_id == current_user.id,
                Booking.bus_id == bus_id,
                Booking.status == BookingStatus.accepted,
            )
            .first()
        )
        has_access = booking is not None

    elif current_user.role.value == "supervisor":
        # Supervisor needs to be assigned to this bus
        has_access = bus.supervisor_id == current_user.id

    elif current_user.role.value == "owner":
        # Owner has access to all their buses
        has_access = bus.owner_id == current_user.id

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to bus location",
        )

    location_data = {
        "bus_id": bus_id,
        "bus_number": bus.bus_number,
        "route": f"{bus.route_from} - {bus.route_to}",
        "has_location": bus.current_lat is not None and bus.current_lng is not None,
    }

    if bus.current_lat and bus.current_lng:
        location_data.update(
            {
                "location": {
                    "lat": float(bus.current_lat),
                    "lng": float(bus.current_lng),
                    "last_update": bus.last_location_update.isoformat()
                    if bus.last_location_update
                    else None,
                }
            }
        )

    return location_data


@router.get("/bus/{bus_id}/eta/{boarding_point_id}")
async def get_eta_to_boarding_point(
    bus_id: int,
    boarding_point_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get estimated time of arrival to a specific boarding point

    Calculates ETA from current bus location to boarding point.
    """
    # Get the bus
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found"
        )

    # Get the boarding point
    boarding_point = (
        db.query(BoardingPoint)
        .filter(BoardingPoint.id == boarding_point_id, BoardingPoint.bus_id == bus_id)
        .first()
    )
    if not boarding_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding point not found for this bus",
        )

    # Check permissions
    has_access = False

    if current_user.role.value == "passenger":
        # Passenger needs accepted booking for this bus
        from app.models.booking import Booking, BookingStatus

        booking = (
            db.query(Booking)
            .filter(
                Booking.passenger_id == current_user.id,
                Booking.bus_id == bus_id,
                Booking.status == BookingStatus.accepted,
            )
            .first()
        )
        has_access = booking is not None

    elif current_user.role.value == "supervisor":
        # Supervisor needs to be assigned to this bus
        has_access = bus.supervisor_id == current_user.id

    elif current_user.role.value == "owner":
        # Owner has access to all their buses
        has_access = bus.owner_id == current_user.id

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to bus location",
        )

    # Check if bus has current location
    if not bus.current_lat or not bus.current_lng:
        return {
            "bus_id": bus_id,
            "boarding_point_id": boarding_point_id,
            "boarding_point_name": boarding_point.name,
            "eta_available": False,
            "message": "Bus location not available",
        }

    # Calculate ETA using OpenStreetMap
    try:
        eta_data = await maps_service.calculate_eta(
            float(bus.current_lat),
            float(bus.current_lng),
            float(boarding_point.lat),
            float(boarding_point.lng),
        )

        if eta_data:
            return {
                "bus_id": bus_id,
                "boarding_point_id": boarding_point_id,
                "boarding_point_name": boarding_point.name,
                "boarding_point_location": {
                    "lat": float(boarding_point.lat),
                    "lng": float(boarding_point.lng),
                },
                "current_bus_location": {
                    "lat": float(bus.current_lat),
                    "lng": float(bus.current_lng),
                    "last_update": bus.last_location_update.isoformat()
                    if bus.last_location_update
                    else None,
                },
                "eta_available": True,
                "distance_km": eta_data["distance_km"],
                "eta_minutes": eta_data["eta_minutes"],
                "distance_text": f"{eta_data['distance_km']} km",
                "duration_text": f"{eta_data['eta_minutes']} minutes",
                "eta_time": eta_data["eta_time"],
            }
        else:
            # Fallback to simple distance calculation
            distance_km = maps_service.calculate_distance(
                float(bus.current_lat),
                float(bus.current_lng),
                float(boarding_point.lat),
                float(boarding_point.lng),
            )

            # Rough estimate: 50 km/h average speed
            estimated_duration = int((distance_km / 50) * 3600)  # seconds

            return {
                "bus_id": bus_id,
                "boarding_point_id": boarding_point_id,
                "boarding_point_name": boarding_point.name,
                "boarding_point_location": {
                    "lat": float(boarding_point.lat),
                    "lng": float(boarding_point.lng),
                },
                "current_bus_location": {
                    "lat": float(bus.current_lat),
                    "lng": float(bus.current_lng),
                    "last_update": bus.last_location_update.isoformat()
                    if bus.last_location_update
                    else None,
                },
                "eta_available": True,
                "distance_km": round(distance_km, 2),
                "estimated_duration": estimated_duration,
                "estimated_duration_text": f"{estimated_duration // 60} min",
                "note": "Estimated using simple distance calculation",
            }

    except Exception as e:
        return {
            "bus_id": bus_id,
            "boarding_point_id": boarding_point_id,
            "boarding_point_name": boarding_point.name,
            "eta_available": False,
            "error": str(e),
            "message": "Unable to calculate ETA",
        }


@router.get("/boarding-points/{boarding_point_id}/nearby")
async def get_nearby_places(
    boarding_point_id: int,
    place_type: str = Query("restaurant", description="Type of places to find"),
    radius: int = Query(500, ge=100, le=5000, description="Search radius in meters"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Find nearby places around a boarding point

    Uses Overpass API to find nearby amenities.
    """
    # Get the boarding point
    boarding_point = (
        db.query(BoardingPoint).filter(BoardingPoint.id == boarding_point_id).first()
    )
    if not boarding_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boarding point not found"
        )

    # Get nearby places
    try:
        nearby_places = await maps_service.get_nearby_places(
            float(boarding_point.lat), float(boarding_point.lng), radius, place_type
        )

        return {
            "boarding_point_id": boarding_point_id,
            "boarding_point_name": boarding_point.name,
            "boarding_point_location": {
                "lat": float(boarding_point.lat),
                "lng": float(boarding_point.lng),
            },
            "search_radius": radius,
            "place_type": place_type,
            "nearby_places": nearby_places or [],
        }

    except Exception as e:
        return {
            "boarding_point_id": boarding_point_id,
            "boarding_point_name": boarding_point.name,
            "error": str(e),
            "message": "Unable to find nearby places",
        }


@router.post("/geocode")
async def geocode_address(
    request: GeocodeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Convert address to coordinates using Nominatim

    Example: "Mohakhali, Dhaka" → {lat: 23.7799, lng: 90.4083}
    """
    try:
        result = await maps_service.geocode_address(request.address)

        if result:
            return {
                "address": request.address,
                "lat": result["lat"],
                "lng": result["lng"],
                "display_name": result.get("display_name", ""),
                "address_details": result.get("address", {}),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find location for '{request.address}'",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geocoding failed: {str(e)}",
        )


@router.get("/route/{bus_id}")
async def get_bus_route(
    bus_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed route information for a bus

    Returns route details including boarding points and directions.
    """
    # Get the bus
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found"
        )

    # Check permissions
    has_access = False

    if current_user.role.value == "passenger":
        # Passenger needs accepted booking for this bus
        from app.models.booking import Booking, BookingStatus

        booking = (
            db.query(Booking)
            .filter(
                Booking.passenger_id == current_user.id,
                Booking.bus_id == bus_id,
                Booking.status == BookingStatus.accepted,
            )
            .first()
        )
        has_access = booking is not None

    elif current_user.role.value == "supervisor":
        # Supervisor needs to be assigned to this bus
        has_access = bus.supervisor_id == current_user.id

    elif current_user.role.value == "owner":
        # Owner has access to all their buses
        has_access = bus.owner_id == current_user.id

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to bus route"
        )

    # Get boarding points
    boarding_points = (
        db.query(BoardingPoint)
        .filter(BoardingPoint.bus_id == bus_id)
        .order_by(BoardingPoint.sequence_order)
        .all()
    )

    boarding_points_data = [
        {
            "id": bp.id,
            "name": bp.name,
            "lat": float(bp.lat),
            "lng": float(bp.lng),
            "sequence_order": bp.sequence_order,
        }
        for bp in boarding_points
    ]

    # Try to get route directions if we have boarding points
    route_data = None
    if boarding_points_data and len(boarding_points_data) >= 2:
        try:
            # Get route from first to last boarding point
            origin = boarding_points_data[0]
            destination = boarding_points_data[-1]

            route_data = await maps_service.get_route(
                origin["lat"],
                origin["lng"],
                destination["lat"],
                destination["lng"],
            )
        except Exception as e:
            print(f"Error getting route directions: {e}")

    return {
        "bus_id": bus_id,
        "bus_number": bus.bus_number,
        "route_from": bus.route_from,
        "route_to": bus.route_to,
        "departure_time": bus.departure_time.isoformat()
        if bus.departure_time
        else None,
        "boarding_points": boarding_points_data,
        "route_directions": route_data,
        "current_location": {
            "lat": float(bus.current_lat) if bus.current_lat else None,
            "lng": float(bus.current_lng) if bus.current_lng else None,
            "last_update": bus.last_location_update.isoformat()
            if bus.last_location_update
            else None,
        }
        if bus.current_lat and bus.current_lng
        else None,
    }
