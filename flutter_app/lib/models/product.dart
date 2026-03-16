class Product {
  final int id;
  final String name;
  final double price;
  final String imageUrl;
  final String category;
  final String skinType;
  final String brand;
  final double rating;
  final int reviewCount;
  final bool isOrganic;
  final bool isVegan;
  final bool inStock;
  final String description;
  final String ingredients;
  final String usageInstructions;
  final double volumeMl;
  final bool isCrueltyFree;
  final List<ProductShade> shades;
  final List<ProductReview> reviews;
  final bool isSubscriptionEligible;
  final double subscriptionPrice;

  Product({
    required this.id,
    required this.name,
    required this.price,
    this.imageUrl = '',
    this.category = '',
    this.skinType = '',
    this.brand = '',
    this.rating = 0.0,
    this.reviewCount = 0,
    this.isOrganic = false,
    this.isVegan = false,
    this.inStock = true,
    this.description = '',
    this.ingredients = '',
    this.usageInstructions = '',
    this.volumeMl = 0.0,
    this.isCrueltyFree = false,
    this.shades = const [],
    this.reviews = const [],
    this.isSubscriptionEligible = false,
    this.subscriptionPrice = 0.0,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      imageUrl: json['image_url'] ?? '',
      category: json['category'] ?? '',
      skinType: json['skin_type'] ?? '',
      brand: json['brand'] ?? '',
      rating: (json['rating'] ?? 0).toDouble(),
      reviewCount: json['review_count'] ?? 0,
      isOrganic: json['is_organic'] ?? false,
      isVegan: json['is_vegan'] ?? false,
      inStock: json['in_stock'] ?? true,
      description: json['description'] ?? '',
      ingredients: json['ingredients'] ?? '',
      usageInstructions: json['usage_instructions'] ?? '',
      volumeMl: (json['volume_ml'] ?? 0).toDouble(),
      isCrueltyFree: json['is_cruelty_free'] ?? false,
      shades: (json['shades'] as List<dynamic>?)
              ?.map((s) => ProductShade.fromJson(s))
              .toList() ??
          [],
      reviews: (json['reviews'] as List<dynamic>?)
              ?.map((r) => ProductReview.fromJson(r))
              .toList() ??
          [],
      isSubscriptionEligible: json['is_subscription_eligible'] ?? false,
      subscriptionPrice: (json['subscription_price'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'price': price,
      'image_url': imageUrl,
      'category': category,
      'skin_type': skinType,
      'brand': brand,
      'rating': rating,
      'review_count': reviewCount,
      'is_organic': isOrganic,
      'is_vegan': isVegan,
      'in_stock': inStock,
    };
  }
}

class ProductShade {
  final int id;
  final String name;
  final String colorCode;
  final double extraPrice;

  ProductShade({
    required this.id,
    required this.name,
    this.colorCode = '',
    this.extraPrice = 0.0,
  });

  factory ProductShade.fromJson(Map<String, dynamic> json) {
    return ProductShade(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      colorCode: json['color_code'] ?? '',
      extraPrice: (json['extra_price'] ?? 0).toDouble(),
    );
  }
}

class ProductReview {
  final int id;
  final String customerName;
  final double rating;
  final String title;
  final String comment;
  final String date;
  final bool isVerified;

  ProductReview({
    required this.id,
    required this.customerName,
    required this.rating,
    this.title = '',
    this.comment = '',
    this.date = '',
    this.isVerified = false,
  });

  factory ProductReview.fromJson(Map<String, dynamic> json) {
    return ProductReview(
      id: json['id'] ?? 0,
      customerName: json['customer_name'] ?? '',
      rating: (json['rating'] ?? 0).toDouble(),
      title: json['title'] ?? '',
      comment: json['comment'] ?? '',
      date: json['date'] ?? '',
      isVerified: json['is_verified'] ?? false,
    );
  }
}
