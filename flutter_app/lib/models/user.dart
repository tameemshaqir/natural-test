class User {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String skinType;
  final int loyaltyPoints;
  final String loyaltyTier;
  final String referralCode;

  User({
    required this.id,
    required this.name,
    required this.email,
    this.phone = '',
    this.skinType = '',
    this.loyaltyPoints = 0,
    this.loyaltyTier = 'bronze',
    this.referralCode = '',
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      skinType: json['skin_type'] ?? '',
      loyaltyPoints: json['loyalty_points'] ?? 0,
      loyaltyTier: json['loyalty_tier'] ?? 'bronze',
      referralCode: json['referral_code'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'skin_type': skinType,
      'loyalty_points': loyaltyPoints,
      'loyalty_tier': loyaltyTier,
      'referral_code': referralCode,
    };
  }
}
