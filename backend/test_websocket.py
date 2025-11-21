"""
WebSocket Testing Suite for Bus AgentUB
Tests real-time features: location updates, booking notifications, ticket alerts
"""

import asyncio
import websockets
import json
import httpx
from datetime import datetime


class WebSocketTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.tokens = {}
    
    async def login(self, phone: str, password: str, role: str):
        """Get JWT token for user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"phone": phone, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                print(f"✓ Logged in as {role}: {phone}")
                return data["access_token"]
            else:
                print(f"✗ Login failed for {role}")
                return None
    
    async def connect_websocket(self, token: str, connection_type: str, entity_id: int = None):
        """
        Connect to WebSocket endpoint
        
        Args:
            token: JWT access token
            connection_type: 'location', 'booking', or 'ticket'
            entity_id: Bus ID, Booking ID, or Ticket ID
        """
        if entity_id:
            ws_endpoint = f"{self.ws_url}/ws/{connection_type}/{entity_id}?token={token}"
        else:
            ws_endpoint = f"{self.ws_url}/ws/{connection_type}?token={token}"
        
        try:
            async with websockets.connect(ws_endpoint) as websocket:
                print(f"✓ Connected to WebSocket: {connection_type}" + 
                      (f" (ID: {entity_id})" if entity_id else ""))
                
                # Listen for messages
                async for message in websocket:
                    data = json.loads(message)
                    self.print_websocket_message(connection_type, data)
        
        except websockets.exceptions.ConnectionClosed:
            print(f"✓ WebSocket connection closed normally")
        except Exception as e:
            print(f"✗ WebSocket connection failed: {e}")
    
    def print_websocket_message(self, msg_type: str, data: dict):
        """Pretty print WebSocket messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 📡 WebSocket Message ({msg_type}):")
        print(json.dumps(data, indent=2))
    
    async def test_bus_location_updates(self, bus_id: int):
        """Test 1: Real-time bus location updates"""
        print("\n" + "="*60)
        print("TEST 1: Real-Time Bus Location Updates")
        print("="*60)
        
        supervisor_token = self.tokens.get("supervisor")
        passenger_token = self.tokens.get("passenger")
        
        if not supervisor_token or not passenger_token:
            print("✗ Missing tokens")
            return
        
        # Passenger subscribes to bus location updates
        passenger_task = asyncio.create_task(
            self.connect_websocket(passenger_token, "location", bus_id)
        )
        
        # Give passenger time to connect
        await asyncio.sleep(2)
        
        # Supervisor updates bus location multiple times
        print("\n🚌 Supervisor updating bus locations...")
        locations = [
            {"lat": 23.8103, "lng": 90.4125, "location": "Mohakhali"},
            {"lat": 23.8050, "lng": 90.4100, "location": "Banani"},
            {"lat": 23.8000, "lng": 90.4050, "location": "Gulshan"}
        ]
        
        async with httpx.AsyncClient() as client:
            for loc in locations:
                print(f"\n📍 Updating location: {loc['location']}")
                response = await client.post(
                    f"{self.base_url}/location/bus/{bus_id}/update",
                    params={"lat": loc["lat"], "lng": loc["lng"]},
                    headers={"Authorization": f"Bearer {supervisor_token}"}
                )
                print(f"   Update status: {response.status_code}")
                await asyncio.sleep(3)
        
        await asyncio.sleep(2)
        passenger_task.cancel()
        try:
            await passenger_task
        except asyncio.CancelledError:
            pass
        print("\n✓ Bus location update test complete")
    
    async def test_booking_notifications(self, bus_id: int):
        """Test 2: Booking status change notifications"""
        print("\n" + "="*60)
        print("TEST 2: Booking Status Notifications")
        print("="*60)
        
        passenger_token = self.tokens.get("passenger")
        supervisor_token = self.tokens.get("supervisor")
        
        # Create a new booking
        print("\n📝 Passenger creating booking request...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/booking/request",
                json={"bus_id": bus_id},
                headers={"Authorization": f"Bearer {passenger_token}"}
            )
            
            if response.status_code != 200:
                print(f"✗ Booking creation failed: {response.text}")
                return
            
            booking = response.json()
            booking_id = booking["id"]
            print(f"✓ Booking created: ID {booking_id}")
        
        # Passenger subscribes to booking updates
        passenger_task = asyncio.create_task(
            self.connect_websocket(passenger_token, "booking")
        )
        
        await asyncio.sleep(2)
        
        # Supervisor accepts booking
        print(f"\n✅ Supervisor accepting booking {booking_id}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/booking/accept",
                json={"booking_id": booking_id},
                headers={"Authorization": f"Bearer {supervisor_token}"}
            )
            print(f"   Accept status: {response.status_code}")
        
        await asyncio.sleep(3)
        passenger_task.cancel()
        try:
            await passenger_task
        except asyncio.CancelledError:
            pass
        print("\n✓ Booking notification test complete")
        
        return booking_id
    
    async def test_ticket_alerts(self, booking_id: int, boarding_point_id: int):
        """Test 3: Ticket confirmation alerts"""
        print("\n" + "="*60)
        print("TEST 3: Ticket Status Alerts")
        print("="*60)
        
        passenger_token = self.tokens.get("passenger")
        
        # Confirm ticket
        print("\n🎫 Passenger confirming ticket...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/booking/ticket/confirm",
                json={
                    "booking_id": booking_id,
                    "boarding_point_id": boarding_point_id,
                    "seats_booked": 2
                },
                headers={"Authorization": f"Bearer {passenger_token}"}
            )
            
            if response.status_code != 200:
                print(f"✗ Ticket confirmation failed: {response.text}")
                return
            
            ticket = response.json()
            ticket_id = ticket["id"]
            print(f"✓ Ticket confirmed: ID {ticket_id}")
        
        # Subscribe to ticket updates
        passenger_task = asyncio.create_task(
            self.connect_websocket(passenger_token, "booking")
        )
        
        print("\n📢 Listening for ticket updates...")
        await asyncio.sleep(5)
        
        passenger_task.cancel()
        try:
            await passenger_task
        except asyncio.CancelledError:
            pass
        print("\n✓ Ticket alert test complete")
    
    async def run_all_tests(self):
        """Run complete WebSocket test suite"""
        print("\n" + "="*60)
        print("🧪 WebSocket Integration Test Suite")
        print("="*60)
        
        # Login all users
        print("\n📱 Logging in test users...")
        await self.login("+8801222222222", "supervisor123", "supervisor")
        await self.login("+8801333333333", "passenger123", "passenger")
        
        # Test 1: Bus location updates
        await self.test_bus_location_updates(bus_id=1)
        
        # Test 2: Booking notifications
        booking_id = await self.test_booking_notifications(bus_id=1)
        
        # Test 3: Ticket alerts
        if booking_id:
            await self.test_ticket_alerts(booking_id=booking_id, boarding_point_id=1)
        
        print("\n" + "="*60)
        print("✅ All WebSocket tests complete!")
        print("="*60)


async def main():
    tester = WebSocketTester("http://localhost:8000")
    await tester.run_all_tests()


if __name__ == "__main__":
    print("\n⚠️  Make sure your FastAPI server is running:")
    print("   cd ~/Projects/bus_agentub/backend")
    print("   source venv/bin/activate")
    print("   uvicorn app.main:app --reload\n")
    
    asyncio.run(main())
