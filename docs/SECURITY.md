# Security Best Practices

## Authentication

### Token-Based Authentication (JWT-like)

The system uses HMAC-SHA256 signed tokens for API authentication:

- **Token Generation**: `user_id:timestamp` signed with server secret
- **Token Expiry**: 24 hours (configurable)
- **Token Storage**: Hive encrypted local storage on device
- **Token Validation**: Signature verification + expiry check on every request

### Best Practices Implemented

1. **Constant-time comparison** using `hmac.compare_digest()` to prevent timing attacks
2. **Unique server secret** stored in Odoo system parameters
3. **Token expiry** to limit exposure window
4. **Automatic token refresh** on 401 responses
5. **Secure logout** that clears local storage

## API Security

### Input Validation

- All API inputs are validated before processing
- SQL injection prevention via Odoo ORM (parameterized queries)
- XSS prevention via JSON responses (no HTML rendering)

### CORS Configuration

- CORS headers set per-endpoint
- Restrict allowed origins in production

### Rate Limiting

Implemented at Nginx level:
- Authentication endpoints: 5 requests/minute
- General API: 60 requests/minute
- Burst handling with nodelay option

### Request Size Limits

- Maximum request body: 50MB (for image uploads)
- Maximum query parameter length: enforced by Nginx

## HTTPS / TLS

### Requirements

- **TLS 1.2 minimum** (TLS 1.3 preferred)
- Strong cipher suites only
- HSTS header with 1-year max-age
- Certificate auto-renewal via Certbot

### Configuration

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Server Hardening

### Operating System

1. Keep Ubuntu updated with security patches
2. Enable automatic security updates
3. Disable unnecessary services
4. Use non-root user for all services

### Firewall (UFW)

```
Allow: SSH (22), HTTP (80), HTTPS (443)
Deny: All other incoming traffic
```

### SSH Security

- Disable root login
- Use SSH key authentication
- Change default SSH port (optional)
- Install fail2ban for brute-force protection

### Database Security

- PostgreSQL listening on localhost only
- Strong password for database user
- Regular automated backups
- No direct external database access

## Payment Security

### PayPal Integration

- Use PayPal REST API with OAuth 2.0
- Server-side payment verification (never trust client)
- Webhook validation for payment status updates
- PCI DSS compliance handled by PayPal

### Order Security

- Server-side price calculation (never trust client prices)
- Inventory check before order confirmation
- Idempotent payment processing to prevent double charges

## Data Protection

### Personal Data

- Minimum data collection principle
- Encrypted storage for sensitive data
- GDPR-ready data export/deletion
- No plain-text password storage (Odoo handles hashing)

### Session Security

- HTTP-only cookies for web sessions
- Secure flag on cookies (HTTPS only)
- SameSite cookie attribute
- Session timeout configuration

## Monitoring & Logging

### Application Logs

- Structured logging with levels (INFO, WARNING, ERROR)
- No sensitive data in logs (tokens, passwords)
- Log rotation configured
- Centralized log collection recommended

### Security Monitoring

- fail2ban for SSH and HTTP brute force
- Nginx access logs for traffic analysis
- Odoo audit trail for admin actions
- Regular security audits recommended

## Checklist

- [ ] Change default admin password
- [ ] Set strong `cosmetics_store.api_secret`
- [ ] Configure SSL/TLS certificates
- [ ] Enable firewall rules
- [ ] Configure rate limiting in Nginx
- [ ] Disable debug mode in production
- [ ] Set up automated backups
- [ ] Configure fail2ban
- [ ] Review file permissions
- [ ] Test payment flow in sandbox
- [ ] Enable automatic security updates
