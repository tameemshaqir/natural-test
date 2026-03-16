import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../services/cart_service.dart';
import '../../../../services/api_service.dart';

class CheckoutPage extends StatefulWidget {
  const CheckoutPage({super.key});

  @override
  State<CheckoutPage> createState() => _CheckoutPageState();
}

class _CheckoutPageState extends State<CheckoutPage> {
  String _selectedShipping = 'standard';
  String _selectedPayment = 'paypal';
  bool _isProcessing = false;
  final _streetController = TextEditingController();
  final _cityController = TextEditingController();
  final _zipController = TextEditingController();

  @override
  void dispose() {
    _streetController.dispose();
    _cityController.dispose();
    _zipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Checkout')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Shipping Address
            const Text(
              'Shipping Address',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _streetController,
              decoration: const InputDecoration(
                labelText: 'Street Address',
                prefixIcon: Icon(Icons.home_outlined),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _cityController,
                    decoration: const InputDecoration(labelText: 'City'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _zipController,
                    decoration: const InputDecoration(labelText: 'ZIP Code'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Shipping Method
            const Text(
              'Shipping Method',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildShippingOption('standard', 'Standard (5-7 days)', 'Free'),
            _buildShippingOption('express', 'Express (2-3 days)', '\$9.99'),
            _buildShippingOption('overnight', 'Overnight', '\$19.99'),
            const SizedBox(height: 24),

            // Payment Method
            const Text(
              'Payment Method',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildPaymentOption('paypal', 'PayPal', Icons.payment),
            _buildPaymentOption('credit_card', 'Credit Card', Icons.credit_card),
            _buildPaymentOption('cod', 'Cash on Delivery', Icons.money),
            const SizedBox(height: 32),

            // Place Order Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isProcessing ? null : _placeOrder,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isProcessing
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Place Order', style: TextStyle(fontSize: 18)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildShippingOption(String value, String title, String price) {
    return RadioListTile<String>(
      value: value,
      groupValue: _selectedShipping,
      onChanged: (v) => setState(() => _selectedShipping = v!),
      title: Text(title),
      subtitle: Text(price),
      activeColor: AppTheme.primaryColor,
    );
  }

  Widget _buildPaymentOption(String value, String title, IconData icon) {
    return RadioListTile<String>(
      value: value,
      groupValue: _selectedPayment,
      onChanged: (v) => setState(() => _selectedPayment = v!),
      title: Row(
        children: [
          Icon(icon, color: AppTheme.primaryColor),
          const SizedBox(width: 8),
          Text(title),
        ],
      ),
      activeColor: AppTheme.primaryColor,
    );
  }

  Future<void> _placeOrder() async {
    setState(() => _isProcessing = true);

    try {
      final apiService = ApiService();
      final cartService = CartService(apiService);

      final result = await cartService.checkout(
        paymentMethod: _selectedPayment,
        shippingMethod: _selectedShipping,
        shippingAddress: {
          'street': _streetController.text,
          'city': _cityController.text,
          'zip': _zipController.text,
        },
      );

      if (mounted) {
        if (result['success'] == true) {
          _showOrderConfirmation(result);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Checkout failed'),
              backgroundColor: AppTheme.errorColor,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('An error occurred. Please try again.'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  void _showOrderConfirmation(Map<String, dynamic> result) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: AppTheme.successColor, size: 32),
            SizedBox(width: 8),
            Text('Order Placed!'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Order: ${result['order_name']}'),
            Text('Total: \$${result['total']?.toStringAsFixed(2)}'),
            const SizedBox(height: 8),
            const Text('Thank you for your purchase!'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(this.context).popUntil((route) => route.isFirst);
            },
            child: const Text('Continue Shopping'),
          ),
        ],
      ),
    );
  }
}
