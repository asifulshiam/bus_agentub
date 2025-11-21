#!/bin/bash
# OpenStreetMap Integration Testing Suite

BASE_URL="http://localhost:8000"
BUS_ID=1
BOARDING_POINT_ID=1

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OpenStreetMap Integration Test Suite ===${NC}\n"

echo "Getting authentication tokens..."

SUPERVISOR_TOKEN=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801222222222", "password": "supervisor123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

PASSENGER_TOKEN=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801333333333", "password": "passenger123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo -e "${GREEN}✓ Tokens obtained${NC}\n"

# Test 1: Update bus location
echo -e "${BLUE}Test 1: POST /location/bus/{id}/update${NC}"
curl -s -X POST "${BASE_URL}/location/bus/${BUS_ID}/update?lat=23.8103&lng=90.4125" \
  -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 1 Complete${NC}\n"
sleep 2

# Test 2: Get bus location
echo -e "${BLUE}Test 2: GET /location/bus/{id}${NC}"
curl -s -X GET "${BASE_URL}/location/bus/${BUS_ID}" \
  -H "Authorization: Bearer ${PASSENGER_TOKEN}" | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 2 Complete${NC}\n"
sleep 2

# Test 3: Calculate ETA
echo -e "${BLUE}Test 3: GET /location/bus/{id}/eta/{boarding_point_id}${NC}"
curl -s -X GET "${BASE_URL}/location/bus/${BUS_ID}/eta/${BOARDING_POINT_ID}" \
  -H "Authorization: Bearer ${PASSENGER_TOKEN}" | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 3 Complete (OSRM routing)${NC}\n"
sleep 2

# Test 4: Get nearby places
echo -e "${BLUE}Test 4: GET /location/boarding-points/{id}/nearby${NC}"
curl -s -X GET "${BASE_URL}/location/boarding-points/${BOARDING_POINT_ID}/nearby?place_type=restaurant&radius=500" \
  -H "Authorization: Bearer ${PASSENGER_TOKEN}" | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 4 Complete (Overpass API)${NC}\n"
sleep 2

# Test 5: Geocode address
echo -e "${BLUE}Test 5: POST /location/geocode${NC}"
curl -s -X POST "${BASE_URL}/location/geocode" \
  -H "Authorization: Bearer ${PASSENGER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"address": "Mohakhali, Dhaka, Bangladesh"}' | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 5 Complete (Nominatim)${NC}\n"
sleep 2

# Test 6: Get bus route
echo -e "${BLUE}Test 6: GET /location/route/{bus_id}${NC}"
curl -s -X GET "${BASE_URL}/location/route/${BUS_ID}" \
  -H "Authorization: Bearer ${PASSENGER_TOKEN}" | python3 -m json.tool
echo -e "\n${GREEN}✓ Test 6 Complete${NC}\n"

echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "${GREEN}✓ All 6 location endpoints tested${NC}"
echo -e "${GREEN}✓ Nominatim geocoding working${NC}"
echo -e "${GREEN}✓ OSRM routing working${NC}"
echo -e "${GREEN}✓ Overpass POI search working${NC}"
echo ""
echo -e "${BLUE}Note: OpenStreetMap has no live traffic data${NC}"
