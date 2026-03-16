import json
import logging

from odoo import http
from odoo.http import request

from .api_auth import authenticate, json_response

_logger = logging.getLogger(__name__)


class SubscriptionController(http.Controller):

    @http.route('/api/v1/subscriptions/plans', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_plans(self, **kwargs):
        """Get available subscription plans."""
        try:
            plans = request.env['cosmetics.subscription.plan'].sudo().search([
                ('is_active', '=', True),
            ])

            plan_list = [{
                'id': plan.id,
                'name': plan.name,
                'description': plan.description or '',
                'price': plan.price,
                'duration_months': plan.duration_months,
                'max_products': plan.max_products,
            } for plan in plans]

            return json_response({'plans': plan_list})
        except Exception as e:
            _logger.exception("Error fetching subscription plans")
            return json_response({'error': str(e)}, status=500)

    @http.route('/api/v1/subscriptions', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_subscriptions(self, **kwargs):
        """Get user's subscriptions."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            subscriptions = request.env['cosmetics.subscription'].sudo().search([
                ('customer_id', '=', user.partner_id.id),
            ])

            sub_list = [{
                'id': sub.id,
                'name': sub.name,
                'plan': sub.plan_id.name,
                'status': sub.status,
                'start_date': str(sub.start_date),
                'next_billing_date': str(sub.next_billing_date) if sub.next_billing_date else '',
                'price': sub.recurring_price,
                'products': [{
                    'id': p.id,
                    'name': p.name,
                    'image_url': f'/web/image/product.template/{p.id}/image_256',
                } for p in sub.product_ids],
            } for sub in subscriptions]

            return {'subscriptions': sub_list}
        except Exception as e:
            _logger.exception("Error fetching subscriptions")
            return {'error': str(e)}

    @http.route('/api/v1/subscriptions/create', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def create_subscription(self, **kwargs):
        """Create a new subscription."""
        try:
            data = json.loads(request.httprequest.data)
            plan_id = data.get('plan_id')

            if not plan_id:
                return {'error': 'Plan ID is required.'}

            plan = request.env['cosmetics.subscription.plan'].sudo().browse(plan_id)
            if not plan.exists() or not plan.is_active:
                return {'error': 'Invalid plan.'}

            user = request.env['res.users'].sudo().browse(request.uid)

            subscription = request.env['cosmetics.subscription'].sudo().create({
                'name': f"{plan.name} - {user.partner_id.name}",
                'customer_id': user.partner_id.id,
                'plan_id': plan.id,
            })

            subscription.action_activate()

            return {
                'success': True,
                'subscription_id': subscription.id,
                'message': 'Subscription created successfully!',
            }
        except Exception as e:
            _logger.exception("Error creating subscription")
            return {'error': str(e)}

    @http.route('/api/v1/subscriptions/<int:sub_id>/cancel', type='json', auth='none',
                methods=['POST'], csrf=False, cors='*')
    @authenticate
    def cancel_subscription(self, sub_id, **kwargs):
        """Cancel a subscription."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            subscription = request.env['cosmetics.subscription'].sudo().browse(sub_id)

            if not subscription.exists() or subscription.customer_id.id != user.partner_id.id:
                return {'error': 'Subscription not found.'}

            subscription.action_cancel()

            return {
                'success': True,
                'message': 'Subscription cancelled.',
            }
        except Exception as e:
            _logger.exception("Error cancelling subscription")
            return {'error': str(e)}
