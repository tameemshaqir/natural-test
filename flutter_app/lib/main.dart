import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'core/constants/app_constants.dart';
import 'core/theme/app_theme.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/cart_service.dart';
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/products/presentation/bloc/product_bloc.dart';
import 'features/cart/presentation/bloc/cart_bloc.dart';
import 'features/products/presentation/pages/home_page.dart';
import 'features/auth/presentation/pages/login_page.dart';
import 'features/products/presentation/pages/product_detail_page.dart';
import 'features/cart/presentation/pages/cart_page.dart';
import 'features/checkout/presentation/pages/checkout_page.dart';
import 'features/orders/presentation/pages/orders_page.dart';
import 'features/subscriptions/presentation/pages/subscriptions_page.dart';
import 'features/profile/presentation/pages/profile_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  await Hive.openBox(AppConstants.settingsBox);
  await Hive.openBox(AppConstants.cartBox);

  runApp(const CosmeticsStoreApp());
}

class CosmeticsStoreApp extends StatelessWidget {
  const CosmeticsStoreApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    final authService = AuthService(apiService);
    final cartService = CartService(apiService);

    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => AuthBloc(authService)),
        BlocProvider(create: (_) => ProductBloc(apiService)),
        BlocProvider(create: (_) => CartBloc(cartService)),
      ],
      child: MaterialApp(
        title: 'Cosmetics Store',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const HomePage(),
        routes: {
          '/login': (context) => const LoginPage(),
          '/cart': (context) => const CartPage(),
          '/checkout': (context) => const CheckoutPage(),
          '/orders': (context) => const OrdersPage(),
          '/subscriptions': (context) => const SubscriptionsPage(),
          '/profile': (context) => const ProfilePage(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/product') {
            final productId = settings.arguments as int;
            return MaterialPageRoute(
              builder: (context) => ProductDetailPage(productId: productId),
            );
          }
          return null;
        },
      ),
    );
  }
}
