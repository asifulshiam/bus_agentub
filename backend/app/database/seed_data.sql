-- =====================================================
-- USERS (passwords should be bcrypt hashes in production)
-- =====================================================
INSERT INTO users (name, phone, password_hash, nid, role) VALUES
('Karim Ahmed', '01711111111', '$2b$12$hashed_passenger1', '1234567890123', 'passenger'),
('Fatema Begum', '01722222222', '$2b$12$hashed_passenger2', '9876543210987', 'passenger'),
('Rahim Uddin', '01710000001', '$2b$12$hashed_supervisor1', '5555555555555', 'supervisor'),
('Abdul Karim', '01720000002', '$2b$12$hashed_supervisor2', '4444444444444', 'supervisor'),
('Hasan Transport Ltd', '01700000001', '$2b$12$hashed_owner1', '2222222222222', 'owner');

-- =====================================================
-- BUSES (owned by Hasan Transport, assigned supervisors)
-- =====================================================
INSERT INTO buses (bus_number, route_from, route_to, departure_time, bus_type, fare, seat_capacity, available_seats, owner_id, supervisor_id) VALUES
('DB-1234', 'Dhaka', 'Chittagong', '2025-10-05 08:00:00', 'Non-AC', 500, 40, 40, 5, 3),
('DB-5678', 'Dhaka', 'Sylhet', '2025-10-05 09:30:00', 'AC', 700, 36, 36, 5, 3),
('DB-9012', 'Dhaka', 'Cox''s Bazar', '2025-10-05 22:00:00', 'AC Sleeper', 1200, 30, 30, 5, 4),
('DB-3456', 'Dhaka', 'Rajshahi', '2025-10-05 07:00:00', 'Non-AC', 450, 40, 40, 5, 4);

-- =====================================================
-- BOARDING POINTS (stops for each bus)
-- =====================================================
-- For DB-1234 (Dhaka → Chittagong)
INSERT INTO boarding_points (bus_id, name, lat, lng, sequence_order) VALUES
(1, 'Kalabagan', 23.7461, 90.3742, 1),
(1, 'Jatrabari', 23.7104, 90.4525, 2),
(1, 'Signboard', 23.7679, 90.4256, 3);

-- For DB-5678 (Dhaka → Sylhet)
INSERT INTO boarding_points (bus_id, name, lat, lng, sequence_order) VALUES
(2, 'Airport', 23.8493, 90.4195, 1),
(2, 'Uttara', 23.8767, 90.3798, 2),
(2, 'Gazipur', 23.9999, 90.4203, 3);

-- For DB-9012 (Dhaka → Cox''s Bazar)
INSERT INTO boarding_points (bus_id, name, lat, lng, sequence_order) VALUES
(3, 'Mohakhali', 23.7808, 90.4056, 1),
(3, 'Sayedabad', 23.7352, 90.4251, 2);

-- For DB-3456 (Dhaka → Rajshahi)
INSERT INTO boarding_points (bus_id, name, lat, lng, sequence_order) VALUES
(4, 'Gabtoli', 23.7786, 90.3481, 1),
(4, 'Abdullahpur', 23.8693, 90.3914, 2);

-- =====================================================
-- BOOKINGS
-- =====================================================
-- Karim requests booking on DB-1234 (pending)
INSERT INTO bookings (passenger_id, bus_id, status, request_time) VALUES
(1, 1, 'pending', '2025-10-05 07:45:00');

-- Karim requests booking on DB-5678 (accepted)
INSERT INTO bookings (passenger_id, bus_id, status, request_time, accepted_time) VALUES
(1, 2, 'accepted', '2025-10-05 08:00:00', '2025-10-05 08:05:00');

-- Fatema requests booking on DB-5678 (accepted)
INSERT INTO bookings (passenger_id, bus_id, status, request_time, accepted_time) VALUES
(2, 2, 'accepted', '2025-10-05 08:10:00', '2025-10-05 08:12:00');

-- =====================================================
-- TICKETS
-- =====================================================
-- Karim confirms 2 seats on DB-5678 (boarding at Airport)
INSERT INTO tickets (booking_id, boarding_point_id, seats_booked, fare_per_seat, total_fare, status) VALUES
(2, 4, 2, 700, 1400, 'confirmed');

-- Fatema confirms 1 seat on DB-5678 (boarding at Uttara)
INSERT INTO tickets (booking_id, boarding_point_id, seats_booked, fare_per_seat, total_fare, status) VALUES
(3, 5, 1, 700, 700, 'confirmed');
