import json
import logging

from odoo import http
from odoo.http import request, Response

from .api_auth import authenticate, _verify_token, json_response

_logger = logging.getLogger(__name__)


class RecommendationController(http.Controller):

    @http.route('/api/v1/recommendations', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_recommendations(self, **kwargs):
        """Get personalized product recommendations."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            rec_model = request.env['cosmetics.ai.recommendation'].sudo()

            recommendations = rec_model.generate_recommendations(
                user.partner_id.id, limit=10
            )

            rec_list = [{
                'id': rec.id,
                'product_id': rec.product_id.id,
                'product_name': rec.product_id.name,
                'price': rec.product_id.list_price,
                'image_url': f'/web/image/product.template/{rec.product_id.id}/image_256',
                'score': rec.score,
                'reason': rec.reason,
            } for rec in recommendations]

            return {'recommendations': rec_list}
        except Exception as e:
            _logger.exception("Error getting recommendations")
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/api/v1/recommendations/skincare', type='json', auth='none',
                methods=['GET'], csrf=False, cors='*')
    @authenticate
    def get_skincare_routine(self, **kwargs):
        """Get AI-powered skincare routine suggestions."""
        try:
            user = request.env['res.users'].sudo().browse(request.uid)
            rec_model = request.env['cosmetics.ai.recommendation'].sudo()

            routine = rec_model.get_skincare_suggestions(user.partner_id.id)

            return {'routine': routine}
        except Exception as e:
            _logger.exception("Error getting skincare suggestions")
            return {'error': 'An error occurred. Please try again.'}

    @http.route('/api/v1/recommendations/trending', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_trending(self, **kwargs):
        """Get trending products (public endpoint)."""
        try:
            limit = min(int(kwargs.get('limit', 10)), 50)

            products = request.env['product.template'].sudo().search([
                ('sale_ok', '=', True),
                ('active', '=', True),
            ], order='rating_average desc, create_date desc', limit=limit)

            product_list = [{
                'id': p.id,
                'name': p.name,
                'price': p.list_price,
                'image_url': f'/web/image/product.template/{p.id}/image_256',
                'rating': p.rating_average,
                'review_count': p.review_count,
                'category': p.cosmetic_category or '',
            } for p in products]

            return json_response({'trending': product_list})
        except Exception as e:
            _logger.exception("Error fetching trending products")
            return json_response({'error': 'Internal server error'}, status=500)
