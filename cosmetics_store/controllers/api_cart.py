import json
import logging

from odoo import http
from odoo.http import request, Response

from .api_auth import authenticate, _verify_token, json_response

_logger = logging.getLogger(__name__)


class CartController(http.Controller):

    def _get_or_create_cart(self, partner_id):
        """Get existing draft order or create new cart."""
        order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner_id),
            ('state', '=', 'draft'),
        ], limit=1, order='create_date desc')

        if not order:
            order = request.env['sale.order'].sudo().create({
                'partner_id': partner_id,
            })
        return order

    @http.route('/api/v1/cart', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_cart(self, **kwargs):
        """Get current user's cart."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            cart = self._get_or_create_cart(user.partner_id.id)

            items = [{
                'id': line.id,
                'product_id': line.product_id.product_tmpl_id.id,
                'product_name': line.product_id.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'subtotal': line.price_subtotal,
                'image_url': f'/web/image/product.template/{line.product_id.product_tmpl_id.id}/image_256',
            } for line in cart.order_line]

            return {
                'cart_id': cart.id,
                'items': items,
                'item_count': len(items),
                'subtotal': cart.amount_untaxed,
                'tax': cart.amount_tax,
                'total': cart.amount_total,
                'coupon_code': cart.coupon_code or '',
                'discount': cart.discount_amount,
            }
        except Exception as e:
            _logger.exception("Error fetching cart")
            return {'error': str(e)}

    @http.route('/api/v1/cart/add', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def add_to_cart(self, **kwargs):
        """Add product to cart."""
        try:
            data = request.jsonrequest
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)

            if not product_id:
                return {'error': 'Product ID is required.'}

            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return {'error': 'Product not found.'}

            user = request.env['res.users'].sudo().browse(request.uid)
            cart = self._get_or_create_cart(user.partner_id.id)

            # Check if product already in cart
            existing_line = cart.order_line.filtered(
                lambda l: l.product_id.product_tmpl_id.id == product_id
            )

            if existing_line:
                existing_line.product_uom_qty += quantity
            else:
                request.env['sale.order.line'].sudo().create({
                    'order_id': cart.id,
                    'product_id': product.product_variant_id.id,
                    'product_uom_qty': quantity,
                })

            return {
                'success': True,
                'message': 'Product added to cart.',
                'cart_total': cart.amount_total,
                'item_count': len(cart.order_line),
            }
        except Exception as e:
            _logger.exception("Error adding to cart")
            return {'error': str(e)}

    @http.route('/api/v1/cart/update', type='json', auth='none',
                methods=['PUT'], csrf=False, cors='*')
    @authenticate
    def update_cart_item(self, **kwargs):
        """Update cart item quantity."""
        try:
            data = request.jsonrequest
            line_id = data.get('line_id')
            quantity = data.get('quantity')

            if not line_id or quantity is None:
                return {'error': 'Line ID and quantity are required.'}

            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return {'error': 'Cart item not found.'}

            if quantity <= 0:
                line.unlink()
                return {'success': True, 'message': 'Item removed from cart.'}
            else:
                line.product_uom_qty = quantity
                return {
                    'success': True,
                    'message': 'Cart updated.',
                    'subtotal': line.price_subtotal,
                }
        except Exception as e:
            _logger.exception("Error updating cart")
            return {'error': str(e)}

    @http.route('/api/v1/cart/remove', type='json', auth='none',
                methods=['DELETE'], csrf=False, cors='*')
    @authenticate
    def remove_from_cart(self, **kwargs):
        """Remove item from cart."""
        try:
            data = request.jsonrequest
            line_id = data.get('line_id')

            if not line_id:
                return {'error': 'Line ID is required.'}

            line = request.env['sale.order.line'].sudo().browse(line_id)
            if line.exists():
                line.unlink()

            return {'success': True, 'message': 'Item removed from cart.'}
        except Exception as e:
            _logger.exception("Error removing from cart")
            return {'error': str(e)}

    @http.route('/api/v1/cart/coupon', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def apply_coupon(self, **kwargs):
        """Apply coupon code to cart."""
        try:
            data = request.jsonrequest
            coupon_code = data.get('coupon_code', '').strip()

            if not coupon_code:
                return {'error': 'Coupon code is required.'}

            user = request.env['res.users'].sudo().browse(request.uid)
            cart = self._get_or_create_cart(user.partner_id.id)

            coupon = request.env['cosmetics.discount'].sudo().search([
                ('code', '=', coupon_code),
                ('active', '=', True),
            ], limit=1)

            if not coupon:
                return {'error': 'Invalid coupon code.'}

            validation = coupon.validate_coupon(cart.amount_untaxed, user.partner_id.id)
            if not validation['valid']:
                return {'error': validation['message']}

            cart.coupon_code = coupon_code

            return {
                'success': True,
                'message': 'Coupon applied successfully.',
                'discount': cart.discount_amount,
                'new_total': cart.amount_total - cart.discount_amount,
            }
        except Exception as e:
            _logger.exception("Error applying coupon")
            return {'error': str(e)}
