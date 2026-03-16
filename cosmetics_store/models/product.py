from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Cosmetic-specific fields
    skin_type = fields.Selection([
        ('all', 'All Skin Types'),
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('normal', 'Normal'),
    ], string='Skin Type', default='all')

    ingredients = fields.Text(string='Ingredients')
    usage_instructions = fields.Text(string='Usage Instructions')
    volume_ml = fields.Float(string='Volume (ml)')
    is_organic = fields.Boolean(string='Organic Product', default=False)
    is_vegan = fields.Boolean(string='Vegan Product', default=False)
    is_cruelty_free = fields.Boolean(string='Cruelty Free', default=False)

    cosmetic_category = fields.Selection([
        ('skincare', 'Skincare'),
        ('makeup', 'Makeup'),
        ('haircare', 'Haircare'),
        ('fragrance', 'Fragrance'),
        ('bodycare', 'Body Care'),
        ('nailcare', 'Nail Care'),
        ('tools', 'Tools & Accessories'),
    ], string='Cosmetic Category')

    brand_id = fields.Many2one('cosmetics.brand', string='Brand')
    shade_ids = fields.One2many('product.shade', 'product_id', string='Available Shades')
    rating_average = fields.Float(string='Average Rating', compute='_compute_rating', store=True)
    review_count = fields.Integer(string='Review Count', compute='_compute_rating', store=True)
    review_ids = fields.One2many('product.review', 'product_id', string='Reviews')
    is_subscription_eligible = fields.Boolean(string='Subscription Eligible', default=False)
    subscription_price = fields.Float(string='Subscription Price')

    @api.depends('review_ids.rating')
    def _compute_rating(self):
        for product in self:
            reviews = product.review_ids
            if reviews:
                product.rating_average = sum(reviews.mapped('rating')) / len(reviews)
                product.review_count = len(reviews)
            else:
                product.rating_average = 0.0
                product.review_count = 0

    @api.constrains('volume_ml')
    def _check_volume(self):
        for record in self:
            if record.volume_ml < 0:
                raise ValidationError("Volume cannot be negative.")

    @api.constrains('subscription_price')
    def _check_subscription_price(self):
        for record in self:
            if record.is_subscription_eligible and record.subscription_price <= 0:
                raise ValidationError(
                    "Subscription price must be positive for subscription-eligible products."
                )


class CosmeticsBrand(models.Model):
    _name = 'cosmetics.brand'
    _description = 'Cosmetic Brand'

    name = fields.Char(string='Brand Name', required=True)
    logo = fields.Binary(string='Logo')
    description = fields.Text(string='Description')
    website = fields.Char(string='Website')
    country_id = fields.Many2one('res.country', string='Country of Origin')
    product_ids = fields.One2many('product.template', 'brand_id', string='Products')
    is_featured = fields.Boolean(string='Featured Brand', default=False)
    active = fields.Boolean(default=True)


class ProductShade(models.Model):
    _name = 'product.shade'
    _description = 'Product Shade/Color Variant'

    name = fields.Char(string='Shade Name', required=True)
    color_code = fields.Char(string='Color Code (Hex)')
    product_id = fields.Many2one('product.template', string='Product', ondelete='cascade')
    image = fields.Binary(string='Shade Image')
    extra_price = fields.Float(string='Extra Price', default=0.0)
    active = fields.Boolean(default=True)


class ProductReview(models.Model):
    _name = 'product.review'
    _description = 'Product Review'
    _order = 'create_date desc'

    product_id = fields.Many2one('product.template', string='Product',
                                 required=True, ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    rating = fields.Float(string='Rating', required=True)
    title = fields.Char(string='Review Title')
    comment = fields.Text(string='Comment')
    is_verified_purchase = fields.Boolean(string='Verified Purchase', default=False)
    is_approved = fields.Boolean(string='Approved', default=False)

    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if record.rating < 1 or record.rating > 5:
                raise ValidationError("Rating must be between 1 and 5.")
