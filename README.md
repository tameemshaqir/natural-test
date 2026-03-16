# Cosmetics E-Commerce System

A complete production-ready e-commerce platform for selling cosmetic products, featuring an Odoo admin dashboard and Flutter Android mobile app.

## System Overview

| Component | Technology | Description |
|-----------|-----------|-------------|
| Admin Dashboard | Odoo 17 | Product, order, customer, subscription management |
| REST API | Odoo Controllers | Secure API layer with token authentication |
| Mobile App | Flutter 3.x | Android app with Clean Architecture & BLoC |
| Database | PostgreSQL | Data persistence |
| Payments | PayPal REST API | Secure payment processing |
| Notifications | Firebase Cloud Messaging | Push notifications |
| AI Features | Custom recommendation engine | Collaborative filtering & content-based |

## Project Structure

```
├── cosmetics_store/          # Odoo Custom Module
│   ├── models/               # Data models (Product, Order, Customer, etc.)
│   ├── controllers/          # REST API endpoints
│   ├── services/             # Business logic (Payment, Notifications, AI)
│   ├── views/                # Admin dashboard XML views
│   ├── security/             # Access control rules
│   ├── data/                 # Default data (categories, skin concerns)
│   ├── static/               # CSS, JS, OWL templates
│   ├── __init__.py
│   └── __manifest__.py
│
├── flutter_app/              # Flutter Android App
│   ├── lib/
│   │   ├── core/             # Theme, constants, utils, widgets
│   │   ├── features/         # Feature modules (auth, products, cart, etc.)
│   │   ├── models/           # Data models
│   │   ├── services/         # API, Auth, Cart services
│   │   └── main.dart         # App entry point
│   └── pubspec.yaml
│
└── docs/                     # Documentation
    ├── SYSTEM_ARCHITECTURE.md
    ├── API_REFERENCE.md
    ├── DEPLOYMENT_GUIDE.md
    └── SECURITY.md
```

## Odoo Admin Dashboard

### Core Features

- **Product Management**: Extended product model with cosmetic-specific fields (skin type, ingredients, shades, organic/vegan badges)
- **Brand Management**: Dedicated brand entity with logo, country, featured status
- **Order Management**: Extended orders with shipping tracking, payment status, delivery notes
- **Customer Profiles**: Skin type, allergies, loyalty points, referral codes
- **Subscription System**: Monthly beauty boxes with configurable plans
- **Discount/Coupon System**: Percentage/fixed discounts with usage limits and validity periods
- **Affiliate Program**: Referral tracking, commission management, payout system
- **Analytics Dashboard**: Real-time KPIs with OWL-based interactive dashboard
- **Product Reviews**: Customer reviews with verified purchase badges

### Dashboard Design

The admin dashboard features:
- **KPI Cards**: Total orders, revenue, customers, products, active subscriptions, pending orders
- **Recent Orders**: Live feed of latest orders with status badges
- **Top Products**: Highest-rated products display
- **Navigation**: Sidebar menu with Products, Orders, Customers, Subscriptions, Marketing sections

## REST API

Secure REST API layer for Flutter ↔ Odoo communication.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Register new customer |
| POST | `/api/v1/auth/login` | No | Login and get token |
| GET | `/api/v1/auth/profile` | Yes | Get user profile |
| GET | `/api/v1/products` | No | List products (paginated) |
| GET | `/api/v1/products/{id}` | No | Product details |
| GET | `/api/v1/products/search` | No | Search products |
| GET | `/api/v1/categories` | No | List categories |
| GET | `/api/v1/cart` | Yes | Get cart contents |
| POST | `/api/v1/cart/add` | Yes | Add item to cart |
| PUT | `/api/v1/cart/update` | Yes | Update cart item |
| DELETE | `/api/v1/cart/remove` | Yes | Remove cart item |
| POST | `/api/v1/cart/coupon` | Yes | Apply coupon code |
| POST | `/api/v1/orders/checkout` | Yes | Create order |
| GET | `/api/v1/orders` | Yes | Order history |
| GET | `/api/v1/subscriptions/plans` | No | List subscription plans |
| GET | `/api/v1/recommendations` | Yes | AI recommendations |
| GET | `/api/v1/recommendations/trending` | No | Trending products |

See [API Reference](docs/API_REFERENCE.md) for complete documentation.

## Flutter Mobile App

### Architecture

- **Clean Architecture**: Separation of data, domain, and presentation layers
- **State Management**: BLoC pattern with `flutter_bloc`
- **API Client**: Dio with interceptors for auth token injection
- **Local Storage**: Hive for token and settings persistence
- **UI**: Material Design 3 with custom cosmetics-themed design

### Features

- Browse products as guest (no login required)
- Create account and sign in
- Product search with filters (category, skin type, brand, price range)
- Product details with shades, reviews, ingredients
- Shopping cart with quantity management
- Coupon/discount code support
- Checkout with PayPal payment
- Order tracking with status updates
- Subscription management (monthly beauty boxes)
- Push notifications for order updates
- User profile with loyalty points and referral codes

### Key Screens

1. **Home Page**: Banner, category chips, product grid
2. **Product Detail**: Image gallery, shades, reviews, add to cart
3. **Cart**: Item list, quantity controls, coupon input, order summary
4. **Checkout**: Shipping address, shipping method, payment method
5. **Orders**: Order history with status tracking
6. **Subscriptions**: Plan selection and management
7. **Profile**: User info, loyalty card, referral code

## AI Features

### Product Recommendations

- **Collaborative Filtering**: Recommends products based on similar customers' purchase patterns
- **Content-Based Filtering**: Matches products to customer's skin type, preferred brands, and profile
- **Trending Products**: Shows popular items based on recent sales and ratings

### Customer Segmentation

Automatic segmentation for targeted marketing:
- **High Value**: Customers with total spend > $500
- **Frequent**: Customers with 5+ orders
- **New**: First order within last 30 days
- **At Risk**: No orders in 60+ days
- **Subscription**: Active subscription holders

### AI Skincare Suggestions

Personalized skincare routine recommendations based on:
- Customer's skin type (oily, dry, combination, normal, sensitive)
- Skin concerns (acne, aging, dark spots, etc.)
- Purchase history
- Product ratings and reviews

## Deployment

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Quick Start

1. Install Odoo 17 on Ubuntu server
2. Copy `cosmetics_store/` to Odoo custom addons
3. Install the module from Odoo Apps
4. Configure system parameters (API secret, PayPal, Firebase)
5. Set up Nginx with SSL
6. Update Flutter app constants with server URL
7. Build Flutter APK: `flutter build apk --release`

## Security

See [Security Best Practices](docs/SECURITY.md) for detailed security guide.

### Key Security Features

- Token-based authentication with HMAC-SHA256
- Rate limiting via Nginx
- HTTPS/TLS 1.2+ enforcement
- Input validation and SQL injection prevention via ORM
- Server-side price calculation
- Firewall and SSH hardening
- fail2ban brute-force protection

## License

This project is proprietary software. All rights reserved.