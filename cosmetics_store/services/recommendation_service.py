import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class RecommendationService:
    """AI-powered recommendation service for cosmetics products.

    Implements collaborative filtering and content-based recommendation
    algorithms for personalized product suggestions.
    """

    @staticmethod
    def get_collaborative_recommendations(env, customer_id, limit=10):
        """Get recommendations based on similar customers' purchases.

        Algorithm: Find customers who bought similar products, then recommend
        products those customers bought that the current customer hasn't.

        Args:
            env: Odoo environment
            customer_id: res.partner ID
            limit: Maximum recommendations

        Returns:
            product.template recordset
        """
        # Get current customer's purchased products
        customer_orders = env['sale.order'].sudo().search([
            ('partner_id', '=', customer_id),
            ('state', '=', 'sale'),
        ])

        customer_products = set()
        for order in customer_orders:
            for line in order.order_line:
                if line.product_id:
                    customer_products.add(line.product_id.product_tmpl_id.id)

        if not customer_products:
            return env['product.template']

        # Find similar customers (who bought same products)
        similar_orders = env['sale.order.line'].sudo().search([
            ('product_id.product_tmpl_id', 'in', list(customer_products)),
            ('order_id.partner_id', '!=', customer_id),
            ('order_id.state', '=', 'sale'),
        ])

        similar_customer_ids = set(
            line.order_id.partner_id.id for line in similar_orders
        )

        # Get products those similar customers bought
        product_scores = defaultdict(int)
        similar_customer_orders = env['sale.order.line'].sudo().search([
            ('order_id.partner_id', 'in', list(similar_customer_ids)),
            ('order_id.state', '=', 'sale'),
        ])

        for line in similar_customer_orders:
            product_id = line.product_id.product_tmpl_id.id
            if product_id not in customer_products:
                product_scores[product_id] += 1

        # Sort by score and return top products
        sorted_products = sorted(
            product_scores.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        product_ids = [pid for pid, _ in sorted_products]
        return env['product.template'].sudo().browse(product_ids)

    @staticmethod
    def get_content_based_recommendations(env, customer_id, limit=10):
        """Get recommendations based on product attributes matching customer profile.

        Uses customer's skin type, preferred brands, and purchase history
        to recommend products with matching attributes.

        Args:
            env: Odoo environment
            customer_id: res.partner ID
            limit: Maximum recommendations

        Returns:
            list of dicts with keys: product (recordset), score (float), and reason (str)
        """
        customer = env['res.partner'].sudo().browse(customer_id)
        if not customer.exists():
            return []

        domain = [('sale_ok', '=', True), ('active', '=', True)]
        recommendations = []

        # Skin type matching
        if customer.skin_type:
            skin_products = env['product.template'].sudo().search(
                domain + [('skin_type', 'in', [customer.skin_type, 'all'])],
                limit=limit * 2,
            )
            for product in skin_products:
                score = 0.7
                if product.brand_id and product.brand_id in customer.preferred_brands:
                    score += 0.2
                if product.is_organic:
                    score += 0.05
                if product.rating_average >= 4.0:
                    score += 0.05
                recommendations.append({
                    'product': product,
                    'score': min(score, 1.0),
                    'reason': 'skin_type',
                })

        # Preferred brand products
        if customer.preferred_brands:
            brand_products = env['product.template'].sudo().search(
                domain + [('brand_id', 'in', customer.preferred_brands.ids)],
                limit=limit,
            )
            for product in brand_products:
                recommendations.append({
                    'product': product,
                    'score': 0.6,
                    'reason': 'preferred_brand',
                })

        # Deduplicate by product ID, keep highest score
        seen = {}
        for rec in sorted(recommendations, key=lambda r: r['score'], reverse=True):
            pid = rec['product'].id
            if pid not in seen:
                seen[pid] = rec

        return list(seen.values())[:limit]

    @staticmethod
    def segment_customers(env):
        """Segment customers based on purchase behavior and profile.

        Returns customer segments for targeted marketing.

        Segments:
        - high_value: Customers with high total spend
        - frequent: Customers with many orders
        - new: Customers with first order in last 30 days
        - at_risk: Customers who haven't ordered in 60+ days
        - subscription: Customers with active subscriptions

        Args:
            env: Odoo environment

        Returns:
            dict with segment name -> list of partner IDs
        """
        from datetime import datetime, timedelta

        segments = {
            'high_value': [],
            'frequent': [],
            'new': [],
            'at_risk': [],
            'subscription': [],
        }

        # Get all customers with orders
        partners = env['res.partner'].sudo().search([
            ('customer_rank', '>', 0),
        ])

        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        for partner in partners:
            orders = env['sale.order'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'sale'),
            ])

            if not orders:
                continue

            total_spend = sum(o.amount_total for o in orders)
            order_count = len(orders)
            last_order_date = max(o.date_order for o in orders)

            # High value (top spenders)
            if total_spend > 500:
                segments['high_value'].append(partner.id)

            # Frequent buyers
            if order_count >= 5:
                segments['frequent'].append(partner.id)

            # New customers
            first_order_date = min(o.date_order for o in orders)
            if first_order_date and first_order_date >= thirty_days_ago:
                segments['new'].append(partner.id)

            # At risk (no recent orders)
            if last_order_date and last_order_date < sixty_days_ago:
                segments['at_risk'].append(partner.id)

        # Subscription customers
        active_subs = env['cosmetics.subscription'].sudo().search([
            ('status', '=', 'active'),
        ])
        segments['subscription'] = list(set(
            sub.customer_id.id for sub in active_subs
        ))

        return segments
