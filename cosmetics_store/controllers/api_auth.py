import json
import logging
import hashlib
import hmac
import time
import base64
import secrets

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# Secret key for JWT-like token signing (in production, use a config parameter)
TOKEN_EXPIRY = 86400  # 24 hours


def _generate_token(user_id):
    """Generate a signed authentication token."""
    timestamp = int(time.time())
    payload = f"{user_id}:{timestamp}"
    secret = request.env['ir.config_parameter'].sudo().get_param(
        'cosmetics_store.api_secret', 'change-me-in-production'
    )
    signature = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    token = base64.b64encode(f"{payload}:{signature}".encode()).decode()
    return token


def _verify_token(token):
    """Verify and decode an authentication token."""
    try:
        decoded = base64.b64decode(token).decode()
        parts = decoded.split(':')
        if len(parts) != 3:
            return None
        user_id, timestamp, signature = int(parts[0]), int(parts[1]), parts[2]

        # Check expiry
        if time.time() - timestamp > TOKEN_EXPIRY:
            return None

        # Verify signature
        payload = f"{user_id}:{timestamp}"
        secret = request.env['ir.config_parameter'].sudo().get_param(
            'cosmetics_store.api_secret', 'change-me-in-production'
        )
        expected_sig = hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None

        return user_id
    except Exception:
        return None


def authenticate(func):
    """Decorator to require authentication for API endpoints."""
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response(
                json.dumps({'error': 'Authentication required'}),
                status=401, content_type='application/json'
            )
        token = auth_header[7:]
        if not token:
            return Response(
                json.dumps({'error': 'Authentication required'}),
                status=401, content_type='application/json'
            )
        user_id = _verify_token(token)
        if not user_id:
            return Response(
                json.dumps({'error': 'Invalid or expired token'}),
                status=401, content_type='application/json'
            )
        request.uid = user_id
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def json_response(data, status=200):
    """Helper to create JSON responses."""
    return Response(
        json.dumps(data, default=str),
        status=status,
        content_type='application/json'
    )


class AuthController(http.Controller):

    @http.route('/api/v1/auth/register', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    def register(self, **kwargs):
        """Register a new customer account."""
        try:
            data = request.jsonrequest
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            phone = data.get('phone')

            if not all([name, email, password]):
                return {'error': 'Name, email, and password are required.'}

            # Check if user already exists
            existing = request.env['res.users'].sudo().search([
                ('login', '=', email)
            ], limit=1)
            if existing:
                return {'error': 'Email already registered.'}

            # Create user and partner
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password,
                'phone': phone,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
            })

            token = _generate_token(user.id)

            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user.partner_id.id,
                    'name': user.name,
                    'email': user.login,
                },
            }
        except Exception as e:
            _logger.exception("Registration error")
            return {'error': str(e)}

    @http.route('/api/v1/auth/login', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    def login(self, **kwargs):
        """Authenticate user and return token."""
        try:
            data = request.jsonrequest
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {'error': 'Email and password are required.'}

            # Authenticate
            uid = request.session.authenticate(
                request.session.db, email, password
            )

            if not uid:
                return {'error': 'Invalid credentials.'}

            user = request.env['res.users'].sudo().browse(uid)
            token = _generate_token(uid)

            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user.partner_id.id,
                    'name': user.name,
                    'email': user.login,
                    'phone': user.phone or '',
                    'loyalty_points': user.partner_id.loyalty_points,
                    'loyalty_tier': user.partner_id.loyalty_tier,
                },
            }
        except Exception as e:
            _logger.exception("Login error")
            return {'error': 'Invalid credentials.'}

    @http.route('/api/v1/auth/profile', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_profile(self, **kwargs):
        """Get current user profile."""
        auth_header = request.httprequest.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {'error': 'Authentication required.'}
        token = auth_header[7:]
        user_id = _verify_token(token)
        if not user_id:
            return {'error': 'Authentication required.'}

        user = request.env['res.users'].sudo().browse(user_id)
        partner = user.partner_id

        return {
            'id': partner.id,
            'name': partner.name,
            'email': user.login,
            'phone': partner.phone or '',
            'skin_type': partner.skin_type or '',
            'loyalty_points': partner.loyalty_points,
            'loyalty_tier': partner.loyalty_tier or 'bronze',
            'referral_code': partner.referral_code or '',
        }
