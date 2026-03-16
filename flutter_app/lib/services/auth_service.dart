import 'dart:convert';
import 'package:hive/hive.dart';
import '../core/constants/app_constants.dart';
import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService;

  AuthService(this._apiService);

  Future<User?> get currentUser async {
    final box = Hive.box(AppConstants.settingsBox);
    final userData = box.get(AppConstants.userKey);
    if (userData != null) {
      return User.fromJson(json.decode(userData));
    }
    return null;
  }

  bool get isLoggedIn {
    final box = Hive.box(AppConstants.settingsBox);
    return box.get(AppConstants.tokenKey) != null;
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _apiService.dio.post('/auth/login', data: {
        'jsonrpc': '2.0',
        'params': {
          'email': email,
          'password': password,
        },
      });

      final result = response.data['result'];
      if (result != null && result['success'] == true) {
        final box = Hive.box(AppConstants.settingsBox);
        await box.put(AppConstants.tokenKey, result['token']);
        await box.put(AppConstants.userKey, json.encode(result['user']));
        return {'success': true, 'user': User.fromJson(result['user'])};
      }
      return {'success': false, 'error': result?['error'] ?? 'Login failed'};
    } catch (e) {
      return {'success': false, 'error': 'Connection error. Please try again.'};
    }
  }

  Future<Map<String, dynamic>> register(
    String name,
    String email,
    String password, {
    String? phone,
  }) async {
    try {
      final response = await _apiService.dio.post('/auth/register', data: {
        'jsonrpc': '2.0',
        'params': {
          'name': name,
          'email': email,
          'password': password,
          'phone': phone,
        },
      });

      final result = response.data['result'];
      if (result != null && result['success'] == true) {
        final box = Hive.box(AppConstants.settingsBox);
        await box.put(AppConstants.tokenKey, result['token']);
        await box.put(AppConstants.userKey, json.encode(result['user']));
        return {'success': true, 'user': User.fromJson(result['user'])};
      }
      return {'success': false, 'error': result?['error'] ?? 'Registration failed'};
    } catch (e) {
      return {'success': false, 'error': 'Connection error. Please try again.'};
    }
  }

  Future<void> logout() async {
    final box = Hive.box(AppConstants.settingsBox);
    await box.delete(AppConstants.tokenKey);
    await box.delete(AppConstants.userKey);
  }

  Future<User?> getProfile() async {
    try {
      final response = await _apiService.dio.post('/auth/profile', data: {
        'jsonrpc': '2.0',
        'params': {},
      });
      final result = response.data['result'];
      if (result != null && result['error'] == null) {
        return User.fromJson(result);
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
