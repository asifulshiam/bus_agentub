import 'package:flutter/material.dart';

class SearchingPage extends StatelessWidget {
  const SearchingPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Searching for Buses'),
      ),
      body: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
