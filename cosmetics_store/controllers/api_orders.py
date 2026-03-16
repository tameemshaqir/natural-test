import json
import logging

from odoo import http
from odoo.http import request, Response

from .api_auth import authenticate, _verify_token, json_response

_logger = logging.getLogger(__name__)


class OrderController(http.Controller):

    @http.route('/api/v1/orders/checkout', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def checkout(self, **kwargs):
        """Process checkout from cart."""
        try:
            data = request.jsonrequest
            payment_method = data.get('payment_method', 'paypal')
            shipping_method = data.get('shipping_method', 'standard')
            shipping_address = data.get('shipping_address', {})
            delivery_notes = data.get('delivery_notes', '')
            affiliate_code = data.get('affiliate_code')

            user = request.env['res.users'].sudo().browse(request.uid)
            cart = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user.partner_id.id),
                ('state', '=', 'draft'),
            ], limit=1, order='create_date desc')

            if not cart or not cart.order_line:
                return {'error': 'Cart is empty.'}

            # Update shipping address if provided
            if shipping_address:
                user.partner_id.sudo().write({
                    'street': shipping_address.get('street', user.partner_id.street),
                    'city': shipping_address.get('city', user.partner_id.city),
                    'zip': shipping_address.get('zip', user.partner_id.zip),
                })

            # Handle affiliate
            affiliate = None
            if affiliate_code:
                affiliate = request.env['cosmetics.affiliate'].sudo().search([
                    ('referral_code', '=', affiliate_code),
                    ('status', '=', 'active'),
                ], limit=1)

            # Update order
            cart.sudo().write({
                'shipping_method': shipping_method,
                'payment_method': payment_method,
                'delivery_notes': delivery_notes,
                'affiliate_id': affiliate.id if affiliate else False,
                'order_status': 'pending',
            })

            # Confirm order
            cart.sudo().action_confirm()

            # Add loyalty points
            points = int(cart.amount_total)
            user.partner_id.sudo().add_loyalty_points(points)

            # Create affiliate referral
            if affiliate:
                request.env['cosmetics.affiliate.referral'].sudo().create({
                    'affiliate_id': affiliate.id,
                    'customer_id': user.partner_id.id,
                    'order_id': cart.id,
                    'order_amount': cart.amount_total,
                    'commission_amount': cart.amount_total * affiliate.commission_rate / 100,
                })

            return {
                'success': True,
                'order_id': cart.id,
                'order_name': cart.name,
                'total': cart.amount_total,
                'payment_method': payment_method,
                'message': 'Order placed successfully!',
            }
        except Exception as e:
            _logger.exception("Checkout error")
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/api/v1/orders', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_orders(self, **kwargs):
        """Get user's order history."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            orders = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user.partner_id.id),
                ('state', '!=', 'draft'),
            ], order='create_date desc')

            order_list = [{
                'id': order.id,
                'name': order.name,
                'date': str(order.date_order),
                'status': order.order_status or 'pending',
                'total': order.amount_total,
                'item_count': len(order.order_line),
                'payment_method': order.payment_method or '',
                'payment_status': order.payment_status or 'pending',
                'tracking_number': order.tracking_number or '',
                'tracking_url': order.tracking_url or '',
                'estimated_delivery': str(order.estimated_delivery) if order.estimated_delivery else '',
            } for order in orders]

            return {'orders': order_list}
        except Exception as e:
            _logger.exception("Error fetching orders")
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/api/v1/orders/<int:order_id>', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_order_detail(self, order_id, **kwargs):
        """Get detailed order information."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            order = request.env['sale.order'].sudo().browse(order_id)

            if not order.exists() or order.partner_id.id != user.partner_id.id:
                return {'error': 'Order not found.'}

            items = [{
                'product_name': line.product_id.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'subtotal': line.price_subtotal,
                'image_url': f'/web/image/product.template/{line.product_id.product_tmpl_id.id}/image_256',
            } for line in order.order_line]

            return {
                'id': order.id,
                'name': order.name,
                'date': str(order.date_order),
                'status': order.order_status or 'pending',
                'items': items,
                'subtotal': order.amount_untaxed,
                'tax': order.amount_tax,
                'discount': order.discount_amount,
                'total': order.amount_total,
                'shipping_method': order.shipping_method or '',
                'payment_method': order.payment_method or '',
                'payment_status': order.payment_status or 'pending',
                'tracking_number': order.tracking_number or '',
                'tracking_url': order.tracking_url or '',
                'estimated_delivery': str(order.estimated_delivery) if order.estimated_delivery else '',
                'delivery_notes': order.delivery_notes or '',
            }
        except Exception as e:
            _logger.exception("Error fetching order detail")
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/api/v1/orders/<int:order_id>/payment', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def process_payment(self, order_id, **kwargs):
        """Process PayPal payment for an order."""
        try:
            data = request.jsonrequest
            payment_id = data.get('payment_id')
            payer_id = data.get('payer_id')

            user = request.env['res.users'].sudo().browse(request.uid)
            order = request.env['sale.order'].sudo().browse(order_id)

            if not order.exists() or order.partner_id.id != user.partner_id.id:
                return {'error': 'Order not found.'}

            # In production, verify payment with PayPal API
            order.sudo().write({
                'payment_status': 'paid',
                'payment_reference': payment_id,
                'order_status': 'confirmed',
            })

            return {
                'success': True,
                'message': 'Payment processed successfully.',
                'order_id': order.id,
                'payment_status': 'paid',
            }
        except Exception as e:
            _logger.exception("Payment processing error")
            return {'error': 'An error occurred. Please try again.'}
