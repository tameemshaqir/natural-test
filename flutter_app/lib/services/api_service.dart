import 'package:dio/dio.dart';
import 'package:hive/hive.dart';
import '../core/constants/app_constants.dart';
import '../models/product.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: '${AppConstants.baseUrl}${AppConstants.apiVersion}',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final box = Hive.box(AppConstants.settingsBox);
        final token = box.get(AppConstants.tokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired - clear and redirect to login
          final box = Hive.box(AppConstants.settingsBox);
          box.delete(AppConstants.tokenKey);
          box.delete(AppConstants.userKey);
        }
        return handler.next(error);
      },
    ));
  }

  // Products
  Future<Map<String, dynamic>> getProducts({
    int page = 1,
    int limit = 20,
    String? category,
    String? skinType,
    String? sort,
  }) async {
    final params = <String, dynamic>{
      'page': page,
      'limit': limit,
    };
    if (category != null) params['category'] = category;
    if (skinType != null) params['skin_type'] = skinType;
    if (sort != null) params['sort'] = sort;

    final response = await _dio.get('/products', queryParameters: params);
    return response.data;
  }

  Future<Product> getProductDetail(int productId) async {
    final response = await _dio.get('/products/$productId');
    return Product.fromJson(response.data);
  }

  Future<Map<String, dynamic>> searchProducts(String query, {int page = 1}) async {
    final response = await _dio.get('/products/search', queryParameters: {
      'q': query,
      'page': page,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getCategories() async {
    final response = await _dio.get('/categories');
    return response.data;
  }

  // Trending / Recommendations
  Future<List<Product>> getTrending({int limit = 10}) async {
    final response = await _dio.get('/recommendations/trending', queryParameters: {
      'limit': limit,
    });
    final list = response.data['trending'] as List;
    return list.map((json) => Product.fromJson(json)).toList();
  }

  Future<Map<String, dynamic>> getRecommendations() async {
    final response = await _dio.get('/recommendations');
    return response.data;
  }

  // Subscription Plans
  Future<Map<String, dynamic>> getSubscriptionPlans() async {
    final response = await _dio.get('/subscriptions/plans');
    return response.data;
  }

  // Generic request
  Dio get dio => _dio;
}
