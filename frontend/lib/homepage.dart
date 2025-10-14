import 'dart:async';
import 'package:busapp/available_routes.dart';
import 'package:busapp/login.dart';
import 'package:busapp/my_tickets.dart';
import 'package:busapp/searching.dart';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Timer? _timer;

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _handlePressDown(TapDownDetails details) {
    _timer = Timer(const Duration(seconds: 1), () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const SearchingPage()),
      );
    });
  }

  void _handlePressUp(TapUpDetails details) {
    _timer?.cancel();
  }

  void _handlePressCancel() {
    _timer?.cancel();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: PopupMenuButton<String>(
          icon: const Icon(Icons.menu, color: Colors.black, size: 30),
          onSelected: (String result) {
            switch (result) {
              case 'Account Settings':
                // TODO: Implement account settings navigation
                break;
              case 'LOG OUT':
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (context) => const login()),
                  (Route<dynamic> route) => false,
                );
                break;
            }
          },
          itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
            const PopupMenuItem<String>(
              value: 'Account Settings',
              child: Text('Account Settings'),
            ),
            const PopupMenuItem<String>(
              value: 'LOG OUT',
              child: Text('LOG OUT'),
            ),
          ],
        ),
        title: const Text(
          'Home',
          style: TextStyle(
            color: Colors.black,
            fontSize: 32.0,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SizedBox(
              width: 300,
              height: 70,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const AvailableRoutesPage(),
                    ),
                  );
                },
                child: const Text(
                  'AVAILABLE ROUTES',
                  style: TextStyle(fontSize: 20),
                ),
              ),
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: 300,
              height: 70,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const MyTicketsPage(),
                    ),
                  );
                },
                child: const Text(
                  'MY TICKETS',
                  style: TextStyle(fontSize: 20),
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: GestureDetector(
        onTapDown: _handlePressDown,
        onTapUp: _handlePressUp,
        onTapCancel: _handlePressCancel,
        child: SizedBox(
          width: 180,
          height: 70,
          child: FloatingActionButton(
            backgroundColor: Colors.black,
            onPressed: () {},
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(15),
            ),
            child: const Text(
              'Press to Book',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, color: Colors.white),
            ),
          ),
        ),
      ),
    );
  }
}
