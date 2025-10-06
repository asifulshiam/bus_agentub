-- =====================================================
-- Bus Booking System Database Schema (Fixed)
-- PostgreSQL
-- =====================================================

DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS boarding_points CASCADE;
DROP TABLE IF EXISTS buses CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ENUM types
CREATE TYPE user_role AS ENUM ('passenger', 'supervisor', 'owner');
CREATE TYPE booking_status AS ENUM ('pending', 'accepted', 'rejected', 'cancelled');
CREATE TYPE ticket_status AS ENUM ('confirmed', 'completed', 'cancelled');
CREATE TYPE bus_type AS ENUM ('AC', 'Non-AC', 'AC Sleeper');

-- =====================================================
-- USERS
-- =====================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(11) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nid VARCHAR(20),
    role user_role NOT NULL DEFAULT 'passenger',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_phone_length CHECK (LENGTH(phone) = 11),
    CONSTRAINT chk_phone_starts_with_01 CHECK (phone LIKE '01%')
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);

-- =====================================================
-- BUSES
-- =====================================================
CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    bus_number VARCHAR(20) UNIQUE NOT NULL,
    route_from VARCHAR(100) NOT NULL,
    route_to VARCHAR(100) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    bus_type bus_type NOT NULL,
    fare DECIMAL(10, 2) NOT NULL,
    seat_capacity INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    supervisor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    current_lat DECIMAL(10, 7),
    current_lng DECIMAL(10, 7),
    last_location_update TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fare_positive CHECK (fare > 0),
    CONSTRAINT chk_seat_capacity_positive CHECK (seat_capacity > 0),
    CONSTRAINT chk_available_seats_valid CHECK (available_seats >= 0 AND available_seats <= seat_capacity)
);

CREATE INDEX idx_buses_route ON buses(route_from, route_to);
CREATE INDEX idx_buses_departure_time ON buses(departure_time);
CREATE INDEX idx_buses_owner ON buses(owner_id);
CREATE INDEX idx_buses_supervisor ON buses(supervisor_id);
CREATE INDEX idx_buses_active ON buses(is_active);

-- =====================================================
-- BOARDING POINTS
-- =====================================================
CREATE TABLE boarding_points (
    id SERIAL PRIMARY KEY,
    bus_id INTEGER NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    lat DECIMAL(10, 7) NOT NULL,
    lng DECIMAL(10, 7) NOT NULL,
    sequence_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_lat_range CHECK (lat >= -90 AND lat <= 90),
    CONSTRAINT chk_lng_range CHECK (lng >= -180 AND lng <= 180),
    CONSTRAINT chk_sequence_order_positive CHECK (sequence_order >= 0),
    CONSTRAINT uq_bus_stop_name UNIQUE(bus_id, name)
);

CREATE INDEX idx_boarding_points_bus ON boarding_points(bus_id);
CREATE INDEX idx_boarding_points_sequence ON boarding_points(bus_id, sequence_order);

-- =====================================================
-- BOOKINGS
-- =====================================================
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    passenger_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bus_id INTEGER NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
    status booking_status NOT NULL DEFAULT 'pending',
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_time TIMESTAMP,
    rejected_time TIMESTAMP,
    cancelled_time TIMESTAMP,
    rejection_reason TEXT,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_bookings_bus ON bookings(bus_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_request_time ON bookings(request_time);

-- =====================================================
-- TICKETS
-- =====================================================
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    boarding_point_id INTEGER NOT NULL REFERENCES boarding_points(id) ON DELETE RESTRICT,
    seats_booked INTEGER NOT NULL,
    fare_per_seat DECIMAL(10, 2) NOT NULL,
    total_fare DECIMAL(10, 2) NOT NULL,
    status ticket_status NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_seats_booked_positive CHECK (seats_booked > 0),
    CONSTRAINT chk_fare_per_seat_positive CHECK (fare_per_seat > 0),
    CONSTRAINT chk_total_fare_correct CHECK (total_fare = fare_per_seat * seats_booked),
    CONSTRAINT uq_booking_ticket UNIQUE(booking_id)
);

CREATE INDEX idx_tickets_booking ON tickets(booking_id);
CREATE INDEX idx_tickets_boarding_point ON tickets(boarding_point_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- auto update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_buses_updated_at BEFORE UPDATE ON buses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- validate bus owner/supervisor roles
CREATE OR REPLACE FUNCTION validate_bus_roles()
RETURNS TRIGGER AS $$
DECLARE
    v_owner_role user_role;
    v_supervisor_role user_role;
BEGIN
    SELECT role INTO v_owner_role FROM users WHERE id = NEW.owner_id;
    IF v_owner_role IS DISTINCT FROM 'owner' THEN
        RAISE EXCEPTION 'Invalid owner_id: user is not an owner';
    END IF;

    IF NEW.supervisor_id IS NOT NULL THEN
        SELECT role INTO v_supervisor_role FROM users WHERE id = NEW.supervisor_id;
        IF v_supervisor_role IS DISTINCT FROM 'supervisor' THEN
            RAISE EXCEPTION 'Invalid supervisor_id: user is not a supervisor';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_bus_roles
BEFORE INSERT OR UPDATE ON buses
FOR EACH ROW EXECUTE FUNCTION validate_bus_roles();

-- validate booking passenger role
CREATE OR REPLACE FUNCTION validate_booking_passenger()
RETURNS TRIGGER AS $$
DECLARE
    v_role user_role;
BEGIN
    SELECT role INTO v_role FROM users WHERE id = NEW.passenger_id;
    IF v_role IS DISTINCT FROM 'passenger' THEN
        RAISE EXCEPTION 'Invalid passenger_id: user is not a passenger';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_booking_passenger
BEFORE INSERT OR UPDATE ON bookings
FOR EACH ROW EXECUTE FUNCTION validate_booking_passenger();

-- update available seats
CREATE OR REPLACE FUNCTION update_bus_seats_on_ticket_change()
RETURNS TRIGGER AS $$
DECLARE
    v_bus_id INTEGER;
BEGIN
    SELECT b.bus_id INTO v_bus_id
    FROM bookings b
    WHERE b.id = NEW.booking_id;

    IF TG_OP = 'INSERT' AND NEW.status = 'confirmed' THEN
        UPDATE buses
        SET available_seats = available_seats - NEW.seats_booked
        WHERE id = v_bus_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'confirmed' AND NEW.status = 'cancelled' THEN
        UPDATE buses
        SET available_seats = available_seats + OLD.seats_booked
        WHERE id = v_bus_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_bus_seats
AFTER INSERT OR UPDATE ON tickets
FOR EACH ROW EXECUTE FUNCTION update_bus_seats_on_ticket_change();

-- cancel tickets if booking cancelled
CREATE OR REPLACE FUNCTION cancel_ticket_on_booking_cancel()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'cancelled' THEN
        UPDATE tickets
        SET status = 'cancelled', cancelled_at = CURRENT_TIMESTAMP
        WHERE booking_id = NEW.id AND status = 'confirmed';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_cancel_ticket_on_booking_cancel
AFTER UPDATE OF status ON bookings
FOR EACH ROW EXECUTE FUNCTION cancel_ticket_on_booking_cancel();
