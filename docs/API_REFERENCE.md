# API Reference

Base URL: `https://your-server.com/api/v1`

## Authentication

All authenticated endpoints require the `Authorization` header:
```
Authorization: Bearer <token>
```

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword123",
  "phone": "+1234567890"
}
```

Response:
```json
{
  "success": true,
  "token": "base64-encoded-token",
  "user": {
    "id": 1,
    "name": "Jane Smith",
    "email": "jane@example.com"
  }
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "success": true,
  "token": "base64-encoded-token",
  "user": {
    "id": 1,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "loyalty_points": 150,
    "loyalty_tier": "silver"
  }
}
```

### Get Profile (Authenticated)

```http
GET /auth/profile
Authorization: Bearer <token>
```

---

## Products (Public)

### List Products

```http
GET /products?page=1&limit=20&category=skincare&sort=price_asc
```

Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| limit | int | Items per page (default: 20, max: 100) |
| category | string | Filter by category |
| skin_type | string | Filter by skin type |
| brand_id | int | Filter by brand ID |
| is_organic | bool | Filter organic products |
| min_price | float | Minimum price filter |
| max_price | float | Maximum price filter |
| sort | string | Sort: name_asc, name_desc, price_asc, price_desc, rating, newest |

Response:
```json
{
  "products": [
    {
      "id": 1,
      "name": "Vitamin C Serum",
      "price": 29.99,
      "image_url": "/web/image/product.template/1/image_256",
      "category": "skincare",
      "brand": "GlowUp",
      "rating": 4.5,
      "review_count": 128,
      "is_organic": true,
      "in_stock": true
    }
  ],
  "total": 245,
  "page": 1,
  "limit": 20,
  "pages": 13
}
```

### Product Detail

```http
GET /products/{product_id}
```

### Search Products

```http
GET /products/search?q=vitamin+c&page=1
```

### Categories & Brands

```http
GET /categories
```

---

## Cart (Authenticated)

### Get Cart

```http
GET /cart
Authorization: Bearer <token>
```

### Add to Cart

```http
POST /cart/add
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

### Update Cart Item

```http
PUT /cart/update
Authorization: Bearer <token>
Content-Type: application/json

{
  "line_id": 5,
  "quantity": 3
}
```

### Remove from Cart

```http
DELETE /cart/remove
Authorization: Bearer <token>
Content-Type: application/json

{
  "line_id": 5
}
```

### Apply Coupon

```http
POST /cart/coupon
Authorization: Bearer <token>
Content-Type: application/json

{
  "coupon_code": "SUMMER20"
}
```

---

## Orders (Authenticated)

### Checkout

```http
POST /orders/checkout
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_method": "paypal",
  "shipping_method": "standard",
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "zip": "10001"
  },
  "affiliate_code": "REF-ABC123"
}
```

### Order History

```http
GET /orders
Authorization: Bearer <token>
```

### Order Detail

```http
GET /orders/{order_id}
Authorization: Bearer <token>
```

### Process Payment

```http
POST /orders/{order_id}/payment
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_id": "PAYPAL-12345",
  "payer_id": "PAYER-67890"
}
```

---

## Subscriptions

### List Plans (Public)

```http
GET /subscriptions/plans
```

### My Subscriptions (Authenticated)

```http
GET /subscriptions
Authorization: Bearer <token>
```

### Create Subscription

```http
POST /subscriptions/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_id": 1
}
```

### Cancel Subscription

```http
POST /subscriptions/{id}/cancel
Authorization: Bearer <token>
```

---

## AI Recommendations

### Personalized Recommendations (Authenticated)

```http
GET /recommendations
Authorization: Bearer <token>
```

### Skincare Routine (Authenticated)

```http
GET /recommendations/skincare
Authorization: Bearer <token>
```

### Trending Products (Public)

```http
GET /recommendations/trending?limit=10
```
