import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/widgets/loading_widget.dart';
import '../../../../models/product.dart';
import '../../presentation/bloc/product_bloc.dart';
import '../widgets/product_card.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;
  String? _selectedCategory;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    context.read<ProductBloc>().add(ProductsFetchRequested());
    context.read<AuthBloc>().add(AuthCheckRequested());
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(),
      body: _buildBody(),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text('Cosmetics Store'),
      actions: [
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: _showSearch,
        ),
        BlocBuilder<AuthBloc, AuthState>(
          builder: (context, state) {
            if (state is AuthAuthenticated) {
              return IconButton(
                icon: const Icon(Icons.shopping_cart_outlined),
                onPressed: () => Navigator.pushNamed(context, '/cart'),
              );
            }
            return const SizedBox.shrink();
          },
        ),
      ],
    );
  }

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return _buildHomeContent();
      case 1:
        return _buildCategoriesContent();
      case 2:
        return _buildCartOrLoginPrompt();
      case 3:
        return _buildProfileOrLogin();
      default:
        return _buildHomeContent();
    }
  }

  Widget _buildHomeContent() {
    return RefreshIndicator(
      onRefresh: () async {
        context.read<ProductBloc>().add(ProductsFetchRequested());
      },
      child: CustomScrollView(
        slivers: [
          // Banner
          SliverToBoxAdapter(child: _buildBanner()),
          // Category chips
          SliverToBoxAdapter(child: _buildCategoryChips()),
          // Products grid
          BlocBuilder<ProductBloc, ProductState>(
            builder: (context, state) {
              if (state is ProductLoading) {
                return const SliverFillRemaining(
                  child: ShimmerProductGrid(),
                );
              }
              if (state is ProductError) {
                return SliverFillRemaining(
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 48, color: Colors.grey),
                        const SizedBox(height: 16),
                        Text(state.message),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () => context
                              .read<ProductBloc>()
                              .add(ProductsFetchRequested()),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                );
              }
              if (state is ProductsLoaded) {
                return SliverPadding(
                  padding: const EdgeInsets.all(16),
                  sliver: SliverGrid(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 0.65,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final product = state.products[index];
                        return ProductCard(
                          product: product,
                          onTap: () => Navigator.pushNamed(
                            context,
                            '/product',
                            arguments: product.id,
                          ),
                        );
                      },
                      childCount: state.products.length,
                    ),
                  ),
                );
              }
              return const SliverFillRemaining(
                child: Center(child: Text('Browse our products')),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildBanner() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'New Collection',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Discover our latest skincare\nand beauty products',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: AppTheme.primaryColor,
            ),
            child: const Text('Shop Now'),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChips() {
    final categories = [
      {'key': null, 'label': 'All'},
      {'key': 'skincare', 'label': 'Skincare'},
      {'key': 'makeup', 'label': 'Makeup'},
      {'key': 'haircare', 'label': 'Haircare'},
      {'key': 'fragrance', 'label': 'Fragrance'},
      {'key': 'bodycare', 'label': 'Body Care'},
    ];

    return SizedBox(
      height: 50,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final cat = categories[index];
          final isSelected = _selectedCategory == cat['key'];
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(cat['label'] as String),
              selected: isSelected,
              onSelected: (_) {
                setState(() => _selectedCategory = cat['key'] as String?);
                context.read<ProductBloc>().add(
                      ProductsFetchRequested(category: _selectedCategory),
                    );
              },
              selectedColor: AppTheme.primaryColor.withOpacity(0.2),
              checkmarkColor: AppTheme.primaryColor,
            ),
          );
        },
      ),
    );
  }

  Widget _buildCategoriesContent() {
    final categories = [
      {'icon': Icons.face, 'name': 'Skincare', 'key': 'skincare'},
      {'icon': Icons.brush, 'name': 'Makeup', 'key': 'makeup'},
      {'icon': Icons.content_cut, 'name': 'Haircare', 'key': 'haircare'},
      {'icon': Icons.spa, 'name': 'Fragrance', 'key': 'fragrance'},
      {'icon': Icons.water_drop, 'name': 'Body Care', 'key': 'bodycare'},
      {'icon': Icons.colorize, 'name': 'Nail Care', 'key': 'nailcare'},
      {'icon': Icons.handyman, 'name': 'Tools', 'key': 'tools'},
    ];

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final cat = categories[index];
        return Card(
          child: InkWell(
            onTap: () {
              setState(() {
                _currentIndex = 0;
                _selectedCategory = cat['key'] as String;
              });
              context.read<ProductBloc>().add(
                    ProductsFetchRequested(category: cat['key'] as String),
                  );
            },
            borderRadius: BorderRadius.circular(16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(cat['icon'] as IconData, size: 40,
                     color: AppTheme.primaryColor),
                const SizedBox(height: 8),
                Text(
                  cat['name'] as String,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCartOrLoginPrompt() {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated) {
          // Navigate to cart
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushNamed(context, '/cart');
            setState(() => _currentIndex = 0);
          });
          return const LoadingWidget();
        }
        return _buildLoginPrompt();
      },
    );
  }

  Widget _buildProfileOrLogin() {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated) {
          return _buildProfileContent(state.user);
        }
        return _buildLoginPrompt();
      },
    );
  }

  Widget _buildLoginPrompt() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.account_circle_outlined, size: 80,
                     color: Colors.grey),
          const SizedBox(height: 16),
          const Text(
            'Sign in to access your account',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pushNamed(context, '/login'),
            child: const Text('Sign In'),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileContent(dynamic user) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Profile header
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 40,
                  backgroundColor: AppTheme.primaryColor,
                  child: Icon(Icons.person, size: 40, color: Colors.white),
                ),
                const SizedBox(height: 12),
                Text(
                  user.name,
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold),
                ),
                Text(user.email, style: const TextStyle(color: Colors.grey)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // Menu items
        _buildMenuItem(Icons.shopping_bag_outlined, 'My Orders', '/orders'),
        _buildMenuItem(Icons.autorenew, 'Subscriptions', '/subscriptions'),
        _buildMenuItem(Icons.person_outline, 'Edit Profile', '/profile'),
        _buildMenuItem(Icons.logout, 'Sign Out', null, isLogout: true),
      ],
    );
  }

  Widget _buildMenuItem(IconData icon, String title, String? route,
      {bool isLogout = false}) {
    return Card(
      child: ListTile(
        leading: Icon(icon,
            color: isLogout ? AppTheme.errorColor : AppTheme.primaryColor),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          if (isLogout) {
            context.read<AuthBloc>().add(AuthLogoutRequested());
            setState(() => _currentIndex = 0);
          } else if (route != null) {
            Navigator.pushNamed(context, route);
          }
        },
      ),
    );
  }

  void _showSearch() {
    showSearch(context: context, delegate: ProductSearchDelegate(context));
  }

  BottomNavigationBar _buildBottomNav() {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: (index) => setState(() => _currentIndex = index),
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'Home'),
        BottomNavigationBarItem(
            icon: Icon(Icons.category_outlined), label: 'Categories'),
        BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart_outlined), label: 'Cart'),
        BottomNavigationBarItem(
            icon: Icon(Icons.person_outline), label: 'Profile'),
      ],
    );
  }
}

class ProductSearchDelegate extends SearchDelegate<String> {
  final BuildContext parentContext;

  ProductSearchDelegate(this.parentContext);

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear),
        onPressed: () => query = '',
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () => close(context, ''),
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    if (query.length < 2) {
      return const Center(child: Text('Enter at least 2 characters'));
    }
    parentContext.read<ProductBloc>().add(ProductSearchRequested(query));
    return BlocBuilder<ProductBloc, ProductState>(
      bloc: parentContext.read<ProductBloc>(),
      builder: (context, state) {
        if (state is ProductLoading) return const LoadingWidget();
        if (state is ProductsLoaded) {
          return ListView.builder(
            itemCount: state.products.length,
            itemBuilder: (context, index) {
              final product = state.products[index];
              return ListTile(
                leading: const Icon(Icons.shopping_bag),
                title: Text(product.name),
                subtitle: Text('\$${product.price.toStringAsFixed(2)}'),
                onTap: () {
                  close(context, '');
                  Navigator.pushNamed(parentContext, '/product',
                      arguments: product.id);
                },
              );
            },
          );
        }
        return const Center(child: Text('No results found'));
      },
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    return const Center(
      child: Text('Search for products, brands, or ingredients'),
    );
  }
}
