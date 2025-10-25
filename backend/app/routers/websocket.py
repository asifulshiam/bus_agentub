from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.bus import Bus
from app.models.booking import Booking
from app.models.ticket import Ticket
from app.utils import decode_access_token

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store bus location connections by bus_id
        self.bus_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect_user(self, websocket: WebSocket, user_id: int):
        """Connect a user for booking updates"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    async def disconnect_user(self, websocket: WebSocket, user_id: int):
        """Disconnect a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def connect_bus_location(self, websocket: WebSocket, bus_id: int):
        """Connect for bus location updates"""
        await websocket.accept()
        if bus_id not in self.bus_connections:
            self.bus_connections[bus_id] = []
        self.bus_connections[bus_id].append(websocket)
    
    async def disconnect_bus_location(self, websocket: WebSocket, bus_id: int):
        """Disconnect from bus location updates"""
        if bus_id in self.bus_connections:
            self.bus_connections[bus_id].remove(websocket)
            if not self.bus_connections[bus_id]:
                del self.bus_connections[bus_id]
    
    async def send_booking_update(self, user_id: int, message: dict):
        """Send booking update to a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)
    
    async def send_bus_location_update(self, bus_id: int, message: dict):
        """Send bus location update to all connected clients"""
        if bus_id in self.bus_connections:
            for connection in self.bus_connections[bus_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.bus_connections[bus_id].remove(connection)
    
    async def broadcast_booking_update(self, message: dict):
        """Broadcast booking update to all connected users"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)


# Global connection manager
manager = ConnectionManager()


def get_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token"""
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


@router.websocket("/ws/booking")
async def websocket_booking_updates(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for booking status updates
    
    Clients connect with JWT token to receive real-time booking updates.
    """
    try:
        # Authenticate user
        user = get_user_from_token(token, db)
        
        # Connect user
        await manager.connect_user(websocket, user.id)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected as {user.name} ({user.role.value})",
            "user_id": user.id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (heartbeat, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except HTTPException as e:
        await websocket.close(code=4001, reason=e.detail)
    except Exception as e:
        await websocket.close(code=4000, reason="Internal server error")
    finally:
        # Disconnect user
        await manager.disconnect_user(websocket, user.id)


@router.websocket("/ws/location/{bus_id}")
async def websocket_bus_location(websocket: WebSocket, bus_id: int, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time bus location updates
    
    Clients connect to receive live bus location updates.
    """
    try:
        # Authenticate user
        user = get_user_from_token(token, db)
        
        # Verify user has access to this bus
        bus = db.query(Bus).filter(Bus.id == bus_id).first()
        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found"
            )
        
        # Check permissions - passenger needs accepted booking, supervisor needs assigned bus
        has_access = False
        
        if user.role.value == "passenger":
            # Check if passenger has accepted booking for this bus
            booking = db.query(Booking).filter(
                Booking.passenger_id == user.id,
                Booking.bus_id == bus_id,
                Booking.status == "accepted"
            ).first()
            has_access = booking is not None
        
        elif user.role.value == "supervisor":
            # Check if supervisor is assigned to this bus
            has_access = bus.supervisor_id == user.id
        
        elif user.role.value == "owner":
            # Owner has access to all their buses
            has_access = bus.owner_id == user.id
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to bus location"
            )
        
        # Connect for bus location updates
        await manager.connect_bus_location(websocket, bus_id)
        
        # Send welcome message with current location
        current_location = {
            "type": "connected",
            "message": f"Connected to bus {bus.bus_number} location updates",
            "bus_id": bus_id,
            "bus_number": bus.bus_number,
            "route": f"{bus.route_from} - {bus.route_to}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if bus.current_lat and bus.current_lng:
            current_location.update({
                "current_location": {
                    "lat": float(bus.current_lat),
                    "lng": float(bus.current_lng),
                    "last_update": bus.last_location_update.isoformat() if bus.last_location_update else None
                }
            })
        
        await websocket.send_text(json.dumps(current_location))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
    
    except HTTPException as e:
        await websocket.close(code=4001, reason=e.detail)
    except Exception as e:
        await websocket.close(code=4000, reason="Internal server error")
    finally:
        # Disconnect from bus location updates
        await manager.disconnect_bus_location(websocket, bus_id)


# Utility functions for sending updates from other parts of the application

async def send_booking_accepted_notification(user_id: int, booking_id: int, bus_details: dict):
    """Send notification when booking is accepted"""
    message = {
        "type": "booking_accepted",
        "booking_id": booking_id,
        "message": "Your booking request has been accepted!",
        "bus_details": bus_details,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_booking_update(user_id, message)


async def send_booking_rejected_notification(user_id: int, booking_id: int, reason: str = None):
    """Send notification when booking is rejected"""
    message = {
        "type": "booking_rejected",
        "booking_id": booking_id,
        "message": "Your booking request has been rejected.",
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_booking_update(user_id, message)


async def send_ticket_confirmed_notification(user_id: int, ticket_id: int, ticket_details: dict):
    """Send notification when ticket is confirmed"""
    message = {
        "type": "ticket_confirmed",
        "ticket_id": ticket_id,
        "message": "Your ticket has been confirmed!",
        "ticket_details": ticket_details,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_booking_update(user_id, message)


async def send_bus_location_update(bus_id: int, lat: float, lng: float):
    """Send bus location update to all connected clients"""
    message = {
        "type": "location_update",
        "bus_id": bus_id,
        "location": {
            "lat": lat,
            "lng": lng,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    await manager.send_bus_location_update(bus_id, message)
