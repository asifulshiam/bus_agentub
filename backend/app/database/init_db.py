"""
Database initialization script for SQLite
Creates all tables and initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine
from app.models import user, bus, booking, ticket, boarding_point
from app.models.user import User, UserRole
from app.models.bus import Bus, BusType
from app.utils import hash_password
from datetime import datetime, timedelta


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def create_sample_data():
    """Create sample data for testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # ✅ Create owner first (need ID for supervisor)
        owner = User(
            name="Bus Owner",
            phone="01700000001",
            password_hash=hash_password("password123"),
            nid="1234567890123",
            role=UserRole.OWNER,
            is_active=True
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        print(f"Owner created with ID: {owner.id}")
        
        # ✅ Create supervisor linked to owner
        supervisor = User(
            name="Bus Supervisor",
            phone="01700000002",
            password_hash=hash_password("password123"),
            nid="1234567890124",
            role=UserRole.SUPERVISOR,
            owner_id=owner.id,  # ✅ Link supervisor to owner
            is_active=True
        )
        db.add(supervisor)
        
        # Create passengers (no owner_id needed)
        passenger1 = User(
            name="John Passenger",
            phone="01700000003",
            password_hash=hash_password("password123"),
            nid="1234567890125",
            role=UserRole.PASSENGER,
            is_active=True
        )
        passenger2 = User(
            name="Jane Passenger",
            phone="01700000004",
            password_hash=hash_password("password123"),
            nid="1234567890126",
            role=UserRole.PASSENGER,
            is_active=True
        )
        
        db.add(passenger1)
        db.add(passenger2)
        db.commit()
        print("Sample users created")
        
        # Create sample buses
        sample_buses = [
            Bus(
                bus_number="DHA-001",
                route_from="Dhaka",
                route_to="Chittagong",
                departure_time=datetime.now() + timedelta(hours=2),
                bus_type=BusType.AC,
                fare=850.00,
                seat_capacity=40,
                available_seats=40,
                owner_id=owner.id,
                supervisor_id=supervisor.id,
                is_active=True
            ),
            Bus(
                bus_number="DHA-002",
                route_from="Dhaka",
                route_to="Sylhet",
                departure_time=datetime.now() + timedelta(hours=4),
                bus_type=BusType.NON_AC,
                fare=650.00,
                seat_capacity=35,
                available_seats=35,
                owner_id=owner.id,
                supervisor_id=supervisor.id,
                is_active=True
            ),
            Bus(
                bus_number="CTG-001",
                route_from="Chittagong",
                route_to="Dhaka",
                departure_time=datetime.now() + timedelta(hours=6),
                bus_type=BusType.AC_SLEEPER,
                fare=1200.00,
                seat_capacity=30,
                available_seats=30,
                owner_id=owner.id,
                supervisor_id=supervisor.id,
                is_active=True
            )
        ]
        
        for bus_obj in sample_buses:
            db.add(bus_obj)
        
        db.commit()
        print("Sample buses created")
        
        # Get created buses
        bus_dhaka_ctg = db.query(Bus).filter(Bus.bus_number == "DHA-001").first()
        bus_dhaka_sylhet = db.query(Bus).filter(Bus.bus_number == "DHA-002").first()
        
        # Create sample boarding points
        sample_boarding_points = [
            # Dhaka to Chittagong
            {
                "bus_id": bus_dhaka_ctg.id,
                "name": "Mohakhali Bus Stand",
                "lat": 23.7808,
                "lng": 90.4044,
                "sequence_order": 1
            },
            {
                "bus_id": bus_dhaka_ctg.id,
                "name": "Comilla Bus Stand",
                "lat": 23.4607,
                "lng": 91.1809,
                "sequence_order": 2
            },
            {
                "bus_id": bus_dhaka_ctg.id,
                "name": "Feni Bus Stand",
                "lat": 23.0159,
                "lng": 91.3976,
                "sequence_order": 3
            },
            # Dhaka to Sylhet
            {
                "bus_id": bus_dhaka_sylhet.id,
                "name": "Mohakhali Bus Stand",
                "lat": 23.7808,
                "lng": 90.4044,
                "sequence_order": 1
            },
            {
                "bus_id": bus_dhaka_sylhet.id,
                "name": "Kishoreganj Bus Stand",
                "lat": 24.4333,
                "lng": 90.7833,
                "sequence_order": 2
            },
            {
                "bus_id": bus_dhaka_sylhet.id,
                "name": "Sylhet Bus Stand",
                "lat": 24.9045,
                "lng": 91.8611,
                "sequence_order": 3
            }
        ]
        
        from app.models.boarding_point import BoardingPoint
        
        for bp_data in sample_boarding_points:
            bp = BoardingPoint(**bp_data)
            db.add(bp)
        
        db.commit()
        print("Sample boarding points created")
        
        print("\n✅ Sample data created successfully!")
        print("\n📝 Sample login credentials:")
        print("Owner: 01700000001 / password123")
        print("Supervisor: 01700000002 / password123 (linked to owner)")
        print("Passenger: 01700000003 / password123")
        print("Passenger: 01700000004 / password123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
        raise
    finally:
        db.close()


def init_database():
    """Initialize the database with tables and sample data"""
    print("Initializing database...")
    create_tables()
    create_sample_data()
    print("Database initialization completed!")


if __name__ == "__main__":
    init_database()