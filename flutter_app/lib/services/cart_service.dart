import '../core/constants/app_constants.dart';
import '../models/cart_item.dart';
import 'api_service.dart';

class CartService {
  final ApiService _apiService;

  CartService(this._apiService);

  Future<Cart> getCart() async {
    try {
      final response = await _apiService.dio.post('/cart', data: {
        'jsonrpc': '2.0',
        'params': {},
      });
      final result = response.data['result'];
      return Cart.fromJson(result);
    } catch (e) {
      return Cart(cartId: 0, items: []);
    }
  }

  Future<Map<String, dynamic>> addToCart(int productId, {int quantity = 1}) async {
    try {
      final response = await _apiService.dio.post('/cart/add', data: {
        'jsonrpc': '2.0',
        'params': {
          'product_id': productId,
          'quantity': quantity,
        },
      });
      return response.data['result'] ?? {'error': 'Failed to add to cart'};
    } catch (e) {
      return {'error': 'Connection error'};
    }
  }

  Future<Map<String, dynamic>> updateCartItem(int lineId, int quantity) async {
    try {
      final response = await _apiService.dio.post('/cart/update', data: {
        'jsonrpc': '2.0',
        'params': {
          'line_id': lineId,
          'quantity': quantity,
        },
      });
      return response.data['result'] ?? {'error': 'Failed to update cart'};
    } catch (e) {
      return {'error': 'Connection error'};
    }
  }

  Future<Map<String, dynamic>> removeFromCart(int lineId) async {
    try {
      final response = await _apiService.dio.post('/cart/remove', data: {
        'jsonrpc': '2.0',
        'params': {
          'line_id': lineId,
        },
      });
      return response.data['result'] ?? {'error': 'Failed to remove item'};
    } catch (e) {
      return {'error': 'Connection error'};
    }
  }

  Future<Map<String, dynamic>> applyCoupon(String couponCode) async {
    try {
      final response = await _apiService.dio.post('/cart/coupon', data: {
        'jsonrpc': '2.0',
        'params': {
          'coupon_code': couponCode,
        },
      });
      return response.data['result'] ?? {'error': 'Failed to apply coupon'};
    } catch (e) {
      return {'error': 'Connection error'};
    }
  }

  Future<Map<String, dynamic>> checkout({
    required String paymentMethod,
    String shippingMethod = 'standard',
    Map<String, String>? shippingAddress,
    String? affiliateCode,
  }) async {
    try {
      final response = await _apiService.dio.post('/orders/checkout', data: {
        'jsonrpc': '2.0',
        'params': {
          'payment_method': paymentMethod,
          'shipping_method': shippingMethod,
          'shipping_address': shippingAddress ?? {},
          'affiliate_code': affiliateCode,
        },
      });
      return response.data['result'] ?? {'error': 'Checkout failed'};
    } catch (e) {
      return {'error': 'Connection error'};
    }
  }
}
