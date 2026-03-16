import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/widgets/loading_widget.dart';
import '../../../../models/product.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';
import '../../../cart/presentation/bloc/cart_bloc.dart';
import '../../presentation/bloc/product_bloc.dart';

class ProductDetailPage extends StatefulWidget {
  final int productId;

  const ProductDetailPage({super.key, required this.productId});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  int _quantity = 1;
  int? _selectedShadeIndex;

  @override
  void initState() {
    super.initState();
    context.read<ProductBloc>().add(ProductDetailRequested(widget.productId));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocBuilder<ProductBloc, ProductState>(
        builder: (context, state) {
          if (state is ProductLoading) return const LoadingWidget();
          if (state is ProductError) {
            return Center(child: Text(state.message));
          }
          if (state is ProductDetailLoaded) {
            return _buildProductDetail(state.product);
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }

  Widget _buildProductDetail(Product product) {
    return CustomScrollView(
      slivers: [
        // Image header
        SliverAppBar(
          expandedHeight: 350,
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            background: CachedNetworkImage(
              imageUrl: product.imageUrl,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(color: Colors.grey[200]),
              errorWidget: (context, url, error) =>
                  Container(color: Colors.grey[200]),
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.share),
              onPressed: () {},
            ),
            IconButton(
              icon: const Icon(Icons.favorite_border),
              onPressed: () {},
            ),
          ],
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Brand & name
                if (product.brand.isNotEmpty)
                  Text(
                    product.brand,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                const SizedBox(height: 4),
                Text(
                  product.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),

                // Rating
                Row(
                  children: [
                    ...List.generate(5, (index) {
                      return Icon(
                        index < product.rating.floor()
                            ? Icons.star
                            : Icons.star_border,
                        color: Colors.amber,
                        size: 20,
                      );
                    }),
                    const SizedBox(width: 8),
                    Text(
                      '${product.rating.toStringAsFixed(1)} (${product.reviewCount} reviews)',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Price
                Text(
                  '\$${product.price.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(height: 16),

                // Tags
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    if (product.isOrganic)
                      _buildTag('Organic', Icons.eco, Colors.green),
                    if (product.isVegan)
                      _buildTag('Vegan', Icons.grass, Colors.teal),
                    if (product.isCrueltyFree)
                      _buildTag('Cruelty Free', Icons.pets, Colors.purple),
                    if (product.skinType.isNotEmpty)
                      _buildTag(
                        'For ${product.skinType} skin',
                        Icons.face,
                        Colors.blue,
                      ),
                    if (product.volumeMl > 0)
                      _buildTag(
                        '${product.volumeMl.toStringAsFixed(0)} ml',
                        Icons.water_drop,
                        Colors.cyan,
                      ),
                  ],
                ),
                const SizedBox(height: 24),

                // Shades
                if (product.shades.isNotEmpty) ...[
                  const Text(
                    'Select Shade',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: product.shades.asMap().entries.map((entry) {
                      final index = entry.key;
                      final shade = entry.value;
                      final isSelected = _selectedShadeIndex == index;
                      return GestureDetector(
                        onTap: () =>
                            setState(() => _selectedShadeIndex = index),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: isSelected
                                  ? AppTheme.primaryColor
                                  : Colors.grey[300]!,
                              width: isSelected ? 2 : 1,
                            ),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(shade.name),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),
                ],

                // Description
                if (product.description.isNotEmpty) ...[
                  const Text(
                    'Description',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    product.description,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // Ingredients
                if (product.ingredients.isNotEmpty) ...[
                  const Text(
                    'Ingredients',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    product.ingredients,
                    style: const TextStyle(
                        fontSize: 13, color: Colors.grey, height: 1.4),
                  ),
                  const SizedBox(height: 24),
                ],

                // Usage
                if (product.usageInstructions.isNotEmpty) ...[
                  const Text(
                    'How to Use',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    product.usageInstructions,
                    style: const TextStyle(
                        fontSize: 13, color: Colors.grey, height: 1.4),
                  ),
                  const SizedBox(height: 24),
                ],

                // Reviews section
                if (product.reviews.isNotEmpty) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Reviews',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      Text('${product.reviewCount} reviews'),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ...product.reviews.take(5).map(
                        (review) => _buildReviewCard(review),
                      ),
                ],

                const SizedBox(height: 100),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTag(String text, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              fontSize: 12,
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReviewCard(dynamic review) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  review.customerName,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                ...List.generate(5, (index) {
                  return Icon(
                    index < review.rating.floor()
                        ? Icons.star
                        : Icons.star_border,
                    color: Colors.amber,
                    size: 16,
                  );
                }),
              ],
            ),
            if (review.isVerified)
              const Row(
                children: [
                  Icon(Icons.verified, size: 14, color: Colors.green),
                  SizedBox(width: 4),
                  Text(
                    'Verified Purchase',
                    style: TextStyle(fontSize: 11, color: Colors.green),
                  ),
                ],
              ),
            if (review.title.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(review.title,
                  style: const TextStyle(fontWeight: FontWeight.w500)),
            ],
            if (review.comment.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                review.comment,
                style: const TextStyle(fontSize: 13, color: Colors.grey),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
