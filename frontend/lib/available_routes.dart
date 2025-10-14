import 'package:flutter/material.dart';

class AvailableRoutesPage extends StatelessWidget {
  const AvailableRoutesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Available Routes'),
      ),
      body: const Center(
        child: Text('This is the Available Routes page.'),
      ),
    );
  }
}
