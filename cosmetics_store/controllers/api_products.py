import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def json_response(data, status=200):
    return Response(
        json.dumps(data, default=str),
        status=status,
        content_type='application/json'
    )


class ProductController(http.Controller):

    @http.route('/api/v1/products', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_products(self, **kwargs):
        """Get product list with pagination, filtering, and sorting."""
        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit

            domain = [('sale_ok', '=', True), ('active', '=', True)]

            # Filters
            category = kwargs.get('category')
            if category:
                domain.append(('cosmetic_category', '=', category))

            skin_type = kwargs.get('skin_type')
            if skin_type:
                domain.append(('skin_type', 'in', [skin_type, 'all']))

            brand_id = kwargs.get('brand_id')
            if brand_id:
                domain.append(('brand_id', '=', int(brand_id)))

            is_organic = kwargs.get('is_organic')
            if is_organic:
                domain.append(('is_organic', '=', True))

            min_price = kwargs.get('min_price')
            if min_price:
                domain.append(('list_price', '>=', float(min_price)))

            max_price = kwargs.get('max_price')
            if max_price:
                domain.append(('list_price', '<=', float(max_price)))

            # Sorting
            sort = kwargs.get('sort', 'name asc')
            allowed_sorts = {
                'name_asc': 'name asc',
                'name_desc': 'name desc',
                'price_asc': 'list_price asc',
                'price_desc': 'list_price desc',
                'rating': 'rating_average desc',
                'newest': 'create_date desc',
            }
            order = allowed_sorts.get(sort, 'name asc')

            products = request.env['product.template'].sudo().search(
                domain, offset=offset, limit=limit, order=order
            )
            total = request.env['product.template'].sudo().search_count(domain)

            product_list = []
            for p in products:
                image_url = f'/web/image/product.template/{p.id}/image_256'
                product_list.append({
                    'id': p.id,
                    'name': p.name,
                    'price': p.list_price,
                    'image_url': image_url,
                    'category': p.cosmetic_category or '',
                    'skin_type': p.skin_type or '',
                    'brand': p.brand_id.name if p.brand_id else '',
                    'rating': p.rating_average,
                    'review_count': p.review_count,
                    'is_organic': p.is_organic,
                    'is_vegan': p.is_vegan,
                    'in_stock': p.qty_available > 0,
                })

            return json_response({
                'products': product_list,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit,
            })
        except Exception as e:
            _logger.exception("Error fetching products")
            return json_response({'error': str(e)}, status=500)

    @http.route('/api/v1/products/<int:product_id>', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_product_detail(self, product_id, **kwargs):
        """Get detailed product information."""
        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return json_response({'error': 'Product not found'}, status=404)

            # Get shades
            shades = [{
                'id': s.id,
                'name': s.name,
                'color_code': s.color_code or '',
                'extra_price': s.extra_price,
            } for s in product.shade_ids]

            # Get reviews
            reviews = [{
                'id': r.id,
                'customer_name': r.customer_id.name,
                'rating': r.rating,
                'title': r.title or '',
                'comment': r.comment or '',
                'date': str(r.create_date),
                'is_verified': r.is_verified_purchase,
            } for r in product.review_ids.filtered(lambda r: r.is_approved)]

            image_url = f'/web/image/product.template/{product.id}/image_1024'
            data = {
                'id': product.id,
                'name': product.name,
                'price': product.list_price,
                'description': product.description_sale or '',
                'image_url': image_url,
                'category': product.cosmetic_category or '',
                'skin_type': product.skin_type or '',
                'brand': product.brand_id.name if product.brand_id else '',
                'ingredients': product.ingredients or '',
                'usage_instructions': product.usage_instructions or '',
                'volume_ml': product.volume_ml,
                'is_organic': product.is_organic,
                'is_vegan': product.is_vegan,
                'is_cruelty_free': product.is_cruelty_free,
                'rating': product.rating_average,
                'review_count': product.review_count,
                'in_stock': product.qty_available > 0,
                'shades': shades,
                'reviews': reviews,
                'is_subscription_eligible': product.is_subscription_eligible,
                'subscription_price': product.subscription_price,
            }

            return json_response(data)
        except Exception as e:
            _logger.exception("Error fetching product detail")
            return json_response({'error': str(e)}, status=500)

    @http.route('/api/v1/products/search', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def search_products(self, **kwargs):
        """Search products by keyword."""
        try:
            query = kwargs.get('q', '').strip()
            if len(query) < 2:
                return json_response({'error': 'Search query too short'}, status=400)

            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit

            domain = [
                ('sale_ok', '=', True),
                ('active', '=', True),
                '|', '|', '|',
                ('name', 'ilike', query),
                ('description_sale', 'ilike', query),
                ('ingredients', 'ilike', query),
                ('brand_id.name', 'ilike', query),
            ]

            products = request.env['product.template'].sudo().search(
                domain, offset=offset, limit=limit
            )
            total = request.env['product.template'].sudo().search_count(domain)

            product_list = [{
                'id': p.id,
                'name': p.name,
                'price': p.list_price,
                'image_url': f'/web/image/product.template/{p.id}/image_256',
                'category': p.cosmetic_category or '',
                'brand': p.brand_id.name if p.brand_id else '',
                'rating': p.rating_average,
            } for p in products]

            return json_response({
                'products': product_list,
                'total': total,
                'page': page,
                'query': query,
            })
        except Exception as e:
            _logger.exception("Error searching products")
            return json_response({'error': str(e)}, status=500)

    @http.route('/api/v1/categories', type='http', auth='none',
                methods=['GET'], csrf=False, cors='*')
    def get_categories(self, **kwargs):
        """Get all product categories."""
        try:
            categories = [
                {'key': 'skincare', 'name': 'Skincare'},
                {'key': 'makeup', 'name': 'Makeup'},
                {'key': 'haircare', 'name': 'Haircare'},
                {'key': 'fragrance', 'name': 'Fragrance'},
                {'key': 'bodycare', 'name': 'Body Care'},
                {'key': 'nailcare', 'name': 'Nail Care'},
                {'key': 'tools', 'name': 'Tools & Accessories'},
            ]
            brands = request.env['cosmetics.brand'].sudo().search([])
            brand_list = [{
                'id': b.id,
                'name': b.name,
                'is_featured': b.is_featured,
            } for b in brands]

            return json_response({
                'categories': categories,
                'brands': brand_list,
            })
        except Exception as e:
            _logger.exception("Error fetching categories")
            return json_response({'error': str(e)}, status=500)
