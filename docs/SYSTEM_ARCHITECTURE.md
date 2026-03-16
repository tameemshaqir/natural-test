# System Architecture

## Overview

The Cosmetics E-Commerce System is a complete production-ready platform consisting of:

1. **Odoo Admin Dashboard** — Backend management system
2. **REST API Layer** — Secure communication bridge
3. **Flutter Android App** — Customer-facing mobile application
4. **PostgreSQL Database** — Data persistence layer

## Architecture Diagram

```
┌─────────────────────────┐
│   Flutter Android App   │
│  (Customer Interface)   │
└───────────┬─────────────┘
            │ HTTPS
            ▼
┌─────────────────────────┐
│   REST API Controllers  │
│   (Odoo HTTP Routes)    │
│   /api/v1/*             │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     Odoo Backend        │
│  (Business Logic Layer) │
│  - Models & Services    │
│  - Payment Processing   │
│  - Notification Service │
│  - AI Recommendations   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   PostgreSQL Database   │
│  (Data Persistence)     │
└─────────────────────────┘
```

## Authentication Flow

```
1. User opens Flutter app
2. User enters credentials (email/password)
3. Flutter sends POST /api/v1/auth/login
4. Odoo validates credentials against res.users
5. Odoo generates signed token (HMAC-SHA256)
6. Token returned to Flutter app
7. Flutter stores token in Hive local storage
8. All subsequent API requests include Bearer token
9. Token expires after 24 hours
10. Flutter intercepts 401 responses and redirects to login
```

## Payment Flow (PayPal)

```
1. User fills cart and proceeds to checkout
2. Flutter sends POST /api/v1/orders/checkout
3. Odoo creates sale order, validates inventory
4. Odoo returns order details with PayPal payment URL
5. Flutter opens PayPal SDK for payment approval
6. User approves payment in PayPal
7. Flutter receives payment_id and payer_id
8. Flutter sends POST /api/v1/orders/{id}/payment
9. Odoo verifies payment with PayPal API
10. Odoo updates order status to "confirmed"
11. Push notification sent to customer
```

## Push Notification Flow

```
1. Flutter app registers with Firebase Cloud Messaging
2. Firebase returns device token
3. Flutter sends device token to Odoo via profile update
4. Odoo stores token in res.partner.firebase_token
5. On order status change, Odoo triggers NotificationService
6. NotificationService sends FCM message with order details
7. Flutter receives notification via FirebaseMessaging
8. Notification displayed to user
```

## Database Relationships

### Core Models

```
product.template (Extended)
├── brand_id → cosmetics.brand (Many2One)
├── shade_ids → product.shade (One2Many)
├── review_ids → product.review (One2Many)
└── skin_concern_ids → cosmetics.skin.concern (Many2Many)

res.partner (Extended)
├── skin_concerns → cosmetics.skin.concern (Many2Many)
├── preferred_brands → cosmetics.brand (Many2Many)
├── wishlist_ids → product.template (Many2Many)
├── subscription_ids → cosmetics.subscription (One2Many)
└── review_ids → product.review (One2Many)

sale.order (Extended)
├── affiliate_id → cosmetics.affiliate (Many2One)
└── subscription_id → cosmetics.subscription (Many2One)

cosmetics.subscription
├── customer_id → res.partner (Many2One)
├── plan_id → cosmetics.subscription.plan (Many2One)
├── product_ids → product.template (Many2Many)
└── order_ids → sale.order (One2Many)

cosmetics.affiliate
├── partner_id → res.partner (Many2One)
├── referral_ids → cosmetics.affiliate.referral (One2Many)
└── payout_ids → cosmetics.affiliate.payout (One2Many)

cosmetics.discount
├── applicable_products → product.template (Many2Many)
└── applicable_categories → product.category (Many2Many)
```

## API Versioning

All API endpoints are versioned under `/api/v1/`. When breaking changes are needed:

1. Create new controller files (e.g., `api_v2_products.py`)
2. Register routes under `/api/v2/`
3. Maintain v1 endpoints for backward compatibility
4. Deprecate v1 with appropriate response headers

## Rate Limiting

Rate limiting is configured per-endpoint:

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Authentication | 5 requests/minute |
| Product Listing | 60 requests/minute |
| Cart Operations | 30 requests/minute |
| Order Operations | 10 requests/minute |
| Search | 20 requests/minute |

Implementation via Nginx:
```nginx
limit_req_zone $binary_remote_addr zone=api_auth:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_general:10m rate=60r/m;
```
