#!/usr/bin/env python3
"""
Simple API test script for Bus AgentUB Backend
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    # Register a passenger
    passenger_data = {
        "name": "Test Passenger",
        "phone": "01700000005",
        "password": "password123",
        "nid": "1234567890127",
        "role": "passenger"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=passenger_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"User registered successfully!")
        print(f"Access token: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_bus_search():
    """Test bus search"""
    print("Testing bus search...")
    response = requests.get(f"{BASE_URL}/buses")
    print(f"Status: {response.status_code}")
    buses = response.json()
    print(f"Found {len(buses)} buses")
    for bus in buses[:2]:  # Show first 2 buses
        print(f"- {bus['bus_number']}: {bus['route_from']} to {bus['route_to']}")
    print()

def test_booking_flow(token):
    """Test booking flow"""
    print("Testing booking flow...")
    
    # Get buses first
    buses_response = requests.get(f"{BASE_URL}/buses")
    buses = buses_response.json()
    
    if not buses:
        print("No buses available for testing")
        return
    
    bus_id = buses[0]['id']
    
    # Create booking request
    headers = {"Authorization": f"Bearer {token}"}
    booking_data = {"bus_id": bus_id}
    
    response = requests.post(f"{BASE_URL}/booking/request", json=booking_data, headers=headers)
    print(f"Booking request status: {response.status_code}")
    
    if response.status_code == 201:
        booking = response.json()
        print(f"Booking created: ID {booking['booking_id']}")
        print(f"Status: {booking['status']}")
    else:
        print(f"Error: {response.json()}")
    print()

def test_owner_dashboard():
    """Test owner dashboard (using sample credentials)"""
    print("Testing owner dashboard...")
    
    # Login as owner
    login_data = {
        "phone": "01700000001",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        owner_token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        # Get dashboard
        dashboard_response = requests.get(f"{BASE_URL}/owner/dashboard", headers=headers)
        print(f"Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard = dashboard_response.json()
            print(f"Dashboard data:")
            print(f"- Total buses: {dashboard['total_buses']}")
            print(f"- Active trips: {dashboard['active_trips']}")
            print(f"- Total bookings: {dashboard['total_bookings']}")
            print(f"- Total revenue: {dashboard['total_revenue']}")
    else:
        print(f"Login failed: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("Starting Bus AgentUB API Tests")
    print("=" * 50)
    
    try:
        # Test basic endpoints
        test_health_check()
        test_bus_search()
        
        # Test user registration and booking
        token = test_user_registration()
        if token:
            test_booking_flow(token)
        
        # Test owner dashboard
        test_owner_dashboard()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
