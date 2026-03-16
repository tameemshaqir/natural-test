from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AIRecommendation(models.Model):
    _name = 'cosmetics.ai.recommendation'
    _description = 'AI Product Recommendation'
    _order = 'score desc'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True,
                                  ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Recommended Product',
                                 required=True)
    score = fields.Float(string='Recommendation Score', default=0.0)
    reason = fields.Selection([
        ('purchase_history', 'Based on Purchase History'),
        ('skin_type', 'Based on Skin Type'),
        ('trending', 'Trending Product'),
        ('similar_customers', 'Similar Customers Bought'),
        ('complementary', 'Complementary Product'),
        ('seasonal', 'Seasonal Recommendation'),
    ], string='Recommendation Reason')
    is_active = fields.Boolean(string='Active', default=True)
    clicked = fields.Boolean(string='Clicked', default=False)
    purchased = fields.Boolean(string='Purchased', default=False)

    @api.model
    def generate_recommendations(self, customer_id, limit=10):
        """Generate AI-powered product recommendations for a customer."""
        customer = self.env['res.partner'].browse(customer_id)
        if not customer.exists():
            return []

        recommendations = []

        # Skin type based recommendations
        if customer.skin_type:
            skin_products = self.env['product.template'].search([
                ('skin_type', 'in', [customer.skin_type, 'all']),
                ('sale_ok', '=', True),
            ], limit=limit)
            for product in skin_products:
                recommendations.append({
                    'customer_id': customer_id,
                    'product_id': product.id,
                    'score': 0.8,
                    'reason': 'skin_type',
                })

        # Purchase history based recommendations
        past_orders = self.env['sale.order'].search([
            ('partner_id', '=', customer_id),
            ('state', '=', 'sale'),
        ])
        purchased_categories = set()
        purchased_product_ids = set()
        for order in past_orders:
            for line in order.order_line:
                if line.product_id and line.product_id.categ_id:
                    purchased_categories.add(line.product_id.categ_id.id)
                    purchased_product_ids.add(line.product_id.product_tmpl_id.id)

        if purchased_categories:
            similar_products = self.env['product.template'].search([
                ('categ_id', 'in', list(purchased_categories)),
                ('id', 'not in', list(purchased_product_ids)),
                ('sale_ok', '=', True),
            ], limit=limit)
            for product in similar_products:
                recommendations.append({
                    'customer_id': customer_id,
                    'product_id': product.id,
                    'score': 0.7,
                    'reason': 'purchase_history',
                })

        # Trending products
        trending = self.env['product.template'].search([
            ('sale_ok', '=', True),
            ('rating_average', '>=', 4.0),
        ], order='rating_average desc', limit=limit)
        for product in trending:
            recommendations.append({
                'customer_id': customer_id,
                'product_id': product.id,
                'score': 0.6,
                'reason': 'trending',
            })

        # Deduplicate and sort by score
        seen = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda r: r['score'], reverse=True):
            if rec['product_id'] not in seen:
                seen.add(rec['product_id'])
                unique_recs.append(rec)
            if len(unique_recs) >= limit:
                break

        # Clear old recommendations
        self.search([('customer_id', '=', customer_id)]).unlink()

        # Create new recommendations
        created = self.create(unique_recs)
        return created

    @api.model
    def get_skincare_suggestions(self, customer_id):
        """AI-based skincare routine suggestions."""
        customer = self.env['res.partner'].browse(customer_id)
        if not customer.exists():
            return {}

        routine = {
            'morning': [],
            'evening': [],
            'weekly': [],
        }

        skin_type = customer.skin_type or 'normal'

        # Morning routine categories
        morning_categories = ['cleanser', 'toner', 'serum', 'moisturizer', 'sunscreen']
        for category_name in morning_categories:
            products = self.env['product.template'].search([
                ('skin_type', 'in', [skin_type, 'all']),
                ('name', 'ilike', category_name),
                ('sale_ok', '=', True),
            ], limit=2)
            for product in products:
                routine['morning'].append({
                    'step': category_name.capitalize(),
                    'product_id': product.id,
                    'product_name': product.name,
                    'price': product.list_price,
                })

        # Evening routine
        evening_categories = ['cleanser', 'toner', 'serum', 'night cream', 'eye cream']
        for category_name in evening_categories:
            products = self.env['product.template'].search([
                ('skin_type', 'in', [skin_type, 'all']),
                ('name', 'ilike', category_name),
                ('sale_ok', '=', True),
            ], limit=2)
            for product in products:
                routine['evening'].append({
                    'step': category_name.capitalize(),
                    'product_id': product.id,
                    'product_name': product.name,
                    'price': product.list_price,
                })

        return routine
