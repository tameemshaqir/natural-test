class CartItem {
  final int id;
  final int productId;
  final String productName;
  final int quantity;
  final double priceUnit;
  final double subtotal;
  final String imageUrl;

  CartItem({
    required this.id,
    required this.productId,
    required this.productName,
    required this.quantity,
    required this.priceUnit,
    required this.subtotal,
    this.imageUrl = '',
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] ?? 0,
      productId: json['product_id'] ?? 0,
      productName: json['product_name'] ?? '',
      quantity: json['quantity'] ?? 0,
      priceUnit: (json['price_unit'] ?? 0).toDouble(),
      subtotal: (json['subtotal'] ?? 0).toDouble(),
      imageUrl: json['image_url'] ?? '',
    );
  }
}

class Cart {
  final int cartId;
  final List<CartItem> items;
  final int itemCount;
  final double subtotal;
  final double tax;
  final double total;
  final String couponCode;
  final double discount;

  Cart({
    required this.cartId,
    required this.items,
    this.itemCount = 0,
    this.subtotal = 0.0,
    this.tax = 0.0,
    this.total = 0.0,
    this.couponCode = '',
    this.discount = 0.0,
  });

  factory Cart.fromJson(Map<String, dynamic> json) {
    return Cart(
      cartId: json['cart_id'] ?? 0,
      items: (json['items'] as List<dynamic>?)
              ?.map((item) => CartItem.fromJson(item))
              .toList() ??
          [],
      itemCount: json['item_count'] ?? 0,
      subtotal: (json['subtotal'] ?? 0).toDouble(),
      tax: (json['tax'] ?? 0).toDouble(),
      total: (json['total'] ?? 0).toDouble(),
      couponCode: json['coupon_code'] ?? '',
      discount: (json['discount'] ?? 0).toDouble(),
    );
  }
}
