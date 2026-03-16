class Order {
  final int id;
  final String name;
  final String date;
  final String status;
  final double total;
  final int itemCount;
  final String paymentMethod;
  final String paymentStatus;
  final String trackingNumber;
  final String trackingUrl;
  final String estimatedDelivery;

  Order({
    required this.id,
    required this.name,
    this.date = '',
    this.status = 'pending',
    this.total = 0.0,
    this.itemCount = 0,
    this.paymentMethod = '',
    this.paymentStatus = 'pending',
    this.trackingNumber = '',
    this.trackingUrl = '',
    this.estimatedDelivery = '',
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      date: json['date'] ?? '',
      status: json['status'] ?? 'pending',
      total: (json['total'] ?? 0).toDouble(),
      itemCount: json['item_count'] ?? 0,
      paymentMethod: json['payment_method'] ?? '',
      paymentStatus: json['payment_status'] ?? 'pending',
      trackingNumber: json['tracking_number'] ?? '',
      trackingUrl: json['tracking_url'] ?? '',
      estimatedDelivery: json['estimated_delivery'] ?? '',
    );
  }
}
