import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class AvailableRoutesPage extends StatefulWidget {
  const AvailableRoutesPage({super.key});

  @override
  State<AvailableRoutesPage> createState() => _AvailableRoutesPageState();
}

class _AvailableRoutesPageState extends State<AvailableRoutesPage> {
  String _selectedRoute = 'All Routes';
  List<Map<String, dynamic>> _filteredRoutes = [];
  final MapController _mapController = MapController();
  bool _isLoading = true;
  String? _error;
  
  List<Map<String, dynamic>> _routes = [];

  @override
  void initState() {
    super.initState();
    _loadBusesFromAPI();
  }

  Future<void> _loadBusesFromAPI() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Fetch buses from API
      final response = await http.get(
        Uri.parse('http://localhost:8000/buses'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> busesData = jsonDecode(response.body);
        
        // Fetch boarding points for each bus
        List<Map<String, dynamic>> routesWithStops = [];
        List<Color> routeColors = [Colors.blue, Colors.green, Colors.red, Colors.orange, Colors.purple];
        
        for (int i = 0; i < busesData.length; i++) {
          final bus = busesData[i];
          
          // Fetch boarding points for this bus
          final stopsResponse = await http.get(
            Uri.parse('http://localhost:8000/buses/${bus['id']}/stops'),
            headers: {
              'Content-Type': 'application/json',
            },
          );
          
          List<Map<String, dynamic>> stops = [];
          if (stopsResponse.statusCode == 200) {
            final List<dynamic> stopsData = jsonDecode(stopsResponse.body);
            stops = stopsData.map((stop) => {
              'name': stop['name'],
              'lat': double.parse(stop['lat'].toString()),
              'lng': double.parse(stop['lng'].toString()),
            }).toList();
          }
          
          // Format departure time
          final departureTime = DateTime.parse(bus['departure_time']);
          final formattedTime = '${departureTime.hour.toString().padLeft(2, '0')}:${departureTime.minute.toString().padLeft(2, '0')}';
          
          routesWithStops.add({
            'id': bus['id'].toString(),
            'name': '${bus['route_from']} - ${bus['route_to']}',
            'busNumber': bus['bus_number'],
            'type': bus['bus_type'],
            'fare': double.parse(bus['fare'].toString()),
            'departureTime': formattedTime,
            'availableSeats': bus['available_seats'],
            'totalSeats': bus['available_seats'], // We'll get this from detailed API later
            'stops': stops,
            'color': routeColors[i % routeColors.length],
          });
        }
        
        setState(() {
          _routes = routesWithStops;
          _filteredRoutes = List.from(_routes);
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load buses: ${response.statusCode}';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Network error: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  void _filterRoutes(String routeName) {
    setState(() {
      _selectedRoute = routeName;
      if (routeName == 'All Routes') {
        _filteredRoutes = List.from(_routes);
      } else {
        _filteredRoutes = _routes.where((route) => route['name'] == routeName).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: Row(
        children: [
          // Left Sidebar
          Container(
            width: 280,
            color: Colors.grey[900],
            child: Column(
              children: [
                // Header
                Container(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(Icons.directions_bus, color: Colors.white, size: 24),
                          const SizedBox(width: 8),
                          Text(
                            'Bus AgentUB',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'Available Routes',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Navigation Buttons
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    children: [
                      _buildNavButton(Icons.home, 'HOME', true),
                      const SizedBox(height: 8),
                      _buildNavButton(Icons.inbox, 'INBOX', false),
                      const SizedBox(height: 20),
                      _buildNavButton(Icons.location_on, 'Current Bus Location', false),
                      const SizedBox(height: 8),
                      _buildNavButton(Icons.add, 'Register New Bus', false),
                      const SizedBox(height: 8),
                      _buildNavButton(Icons.person, 'Manage Supervisor', false),
                      const SizedBox(height: 8),
                      _buildNavButton(Icons.bar_chart, 'SALES', false),
                    ],
                  ),
                ),
                
                const Spacer(),
                
                // Logout Button
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        // Handle logout
                      },
                      icon: Icon(Icons.power_settings_new, color: Colors.white),
                      label: Text('LOGOUT', style: TextStyle(color: Colors.white)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red[700],
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Main Content Area
          Expanded(
            child: Column(
              children: [
                // Top Header
                Container(
                  height: 80,
                  color: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      Icon(Icons.directions_bus, color: Colors.grey[800], size: 32),
                      const SizedBox(width: 12),
                      Text(
                        'Available Bus Routes',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      const Spacer(),
                      // Search Bar
                      Container(
                        width: 300,
                        height: 40,
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: 'Search routes...',
                            prefixIcon: Icon(Icons.search, color: Colors.grey[600]),
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          ),
                        ),
                      ),
                      const SizedBox(width: 20),
                      Icon(Icons.settings, color: Colors.grey[600], size: 24),
                      const SizedBox(width: 20),
                      Icon(Icons.account_circle, color: Colors.grey[600], size: 24),
                    ],
                  ),
                ),
                
                // Route Filter Bar
                Container(
                  height: 50,
                  color: Colors.grey[200],
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      Text(
                        'Filter Routes:',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: [
                              _buildFilterChip('All Routes'),
                              const SizedBox(width: 8),
                              ..._routes.map((route) => Padding(
                                padding: const EdgeInsets.only(right: 8),
                                child: _buildFilterChip(route['name']),
                              )),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Map Area
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.3),
                          spreadRadius: 2,
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: _buildMapContent(),
                    ),
                  ),
                ),
                
                // Route Information Panel
                Container(
                  height: 140,
                  color: Colors.white,
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Route Information',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Expanded(
                        child: _isLoading
                            ? const Center(
                                child: CircularProgressIndicator(),
                              )
                            : _error != null
                                ? Center(
                                    child: Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        Icon(
                                          Icons.error_outline,
                                          size: 48,
                                          color: Colors.red[400],
                                        ),
                                        const SizedBox(height: 16),
                                        Text(
                                          _error!,
                                          style: TextStyle(
                                            fontSize: 16,
                                            color: Colors.red[600],
                                          ),
                                          textAlign: TextAlign.center,
                                        ),
                                        const SizedBox(height: 16),
                                        ElevatedButton(
                                          onPressed: _loadBusesFromAPI,
                                          child: const Text('Retry'),
                                        ),
                                      ],
                                    ),
                                  )
                                : ListView.builder(
                                    scrollDirection: Axis.horizontal,
                                    itemCount: _filteredRoutes.length,
                                    itemBuilder: (context, index) {
                                      final route = _filteredRoutes[index];
                                      return Container(
                                        width: 300,
                                        margin: const EdgeInsets.only(right: 16),
                                        padding: const EdgeInsets.all(16),
                                        decoration: BoxDecoration(
                                          color: Colors.grey[50],
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: Colors.grey[300]!),
                                        ),
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Container(
                                                  width: 12,
                                                  height: 12,
                                                  decoration: BoxDecoration(
                                                    color: route['color'],
                                                    shape: BoxShape.circle,
                                                  ),
                                                ),
                                                const SizedBox(width: 8),
                                                Expanded(
                                                  child: Text(
                                                    route['name'],
                                                    style: TextStyle(
                                                      fontSize: 16,
                                                      fontWeight: FontWeight.bold,
                                                      color: Colors.grey[800],
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 8),
                                            Text(
                                              '${route['busNumber']} • ${route['type']} • ${route['departureTime']}',
                                              style: TextStyle(
                                                fontSize: 14,
                                                color: Colors.grey[600],
                                              ),
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              'BDT ${route['fare']} • ${route['availableSeats']}/${route['totalSeats']} seats',
                                              style: TextStyle(
                                                fontSize: 14,
                                                color: Colors.grey[600],
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                    },
                                  ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavButton(IconData icon, String label, bool isSelected) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 4),
      child: ElevatedButton.icon(
        onPressed: () {
          // Handle navigation
        },
        icon: Icon(icon, color: Colors.white, size: 20),
        label: Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: isSelected ? Colors.blue[700] : Colors.transparent,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
          alignment: Alignment.centerLeft,
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label) {
    final isSelected = _selectedRoute == label;
    return FilterChip(
      label: Text(
        label,
        style: TextStyle(
          color: isSelected ? Colors.white : Colors.grey[700],
          fontSize: 14,
        ),
      ),
      selected: isSelected,
      onSelected: (selected) {
        _filterRoutes(label);
      },
      backgroundColor: Colors.grey[200],
      selectedColor: Colors.blue[600],
      checkmarkColor: Colors.white,
    );
  }

  List<Marker> _buildMapMarkers() {
    List<Marker> markers = [];
    
    for (var route in _filteredRoutes) {
      for (var stop in route['stops']) {
        markers.add(
          Marker(
            point: LatLng(stop['lat'], stop['lng']),
            width: 40,
            height: 40,
            child: Container(
              decoration: BoxDecoration(
                color: route['color'],
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 3),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    spreadRadius: 1,
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Icon(
                Icons.location_on,
                color: Colors.white,
                size: 20,
              ),
            ),
          ),
        );
      }
    }
    
    return markers;
  }

  List<Polyline> _buildMapPolylines() {
    List<Polyline> polylines = [];
    
    for (var route in _filteredRoutes) {
      if (route['stops'].length > 1) {
        List<LatLng> points = route['stops']
            .map<LatLng>((stop) => LatLng(stop['lat'], stop['lng']))
            .toList();

        polylines.add(
          Polyline(
            points: points,
            color: route['color'],
            strokeWidth: 4.0,
            isDotted: true,
          ),
        );
      }
    }
    
    return polylines;
  }

  Widget _buildMapContent() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading routes...'),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[400],
            ),
            const SizedBox(height: 16),
            Text(
              _error!,
              style: TextStyle(
                fontSize: 18,
                color: Colors.red[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadBusesFromAPI,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return Stack(
      children: [
        // OpenStreetMap
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: const LatLng(23.8103, 90.4125), // Dhaka center
            initialZoom: 11.0,
            minZoom: 5.0,
            maxZoom: 18.0,
          ),
          children: [
            // Tile layer
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.busagentub.app',
              maxZoom: 18,
            ),
            
            // Markers layer
            MarkerLayer(
              markers: _buildMapMarkers(),
            ),
            
            // Polylines layer
            PolylineLayer(
              polylines: _buildMapPolylines(),
            ),
          ],
        ),
        
        // Map controls
        Positioned(
          top: 16,
          right: 16,
          child: Column(
            children: [
              _buildMapControl(Icons.add, () {
                _mapController.move(_mapController.camera.center, _mapController.camera.zoom + 1);
              }),
              const SizedBox(height: 8),
              _buildMapControl(Icons.remove, () {
                _mapController.move(_mapController.camera.center, _mapController.camera.zoom - 1);
              }),
              const SizedBox(height: 8),
              _buildMapControl(Icons.my_location, () {
                _mapController.move(const LatLng(23.8103, 90.4125), 11.0);
              }),
            ],
          ),
        ),
        
        // Map info
        Positioned(
          bottom: 16,
          left: 16,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.9),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Route Overview',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${_filteredRoutes.length} active routes',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  '${_filteredRoutes.fold<int>(0, (sum, route) => sum + (route['availableSeats'] as int))} seats available',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMapControl(IconData icon, VoidCallback onPressed) {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: IconButton(
        icon: Icon(icon, size: 20, color: Colors.grey[700]),
        onPressed: onPressed,
      ),
    );
  }
}
