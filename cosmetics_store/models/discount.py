from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CosmeticsDiscount(models.Model):
    _name = 'cosmetics.discount'
    _description = 'Discount / Coupon'
    _order = 'create_date desc'

    name = fields.Char(string='Discount Name', required=True)
    code = fields.Char(string='Coupon Code', required=True, copy=False)
    description = fields.Text(string='Description')

    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
        ('buy_x_get_y', 'Buy X Get Y'),
    ], string='Discount Type', required=True, default='percentage')

    discount_value = fields.Float(string='Discount Value')
    max_discount = fields.Float(string='Maximum Discount Amount',
                                help='0 = no limit')
    min_order_amount = fields.Float(string='Minimum Order Amount', default=0)

    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    usage_limit = fields.Integer(string='Total Usage Limit', default=0,
                                 help='0 = unlimited')
    usage_count = fields.Integer(string='Times Used', default=0, readonly=True)
    per_customer_limit = fields.Integer(string='Per Customer Limit', default=1)

    applicable_products = fields.Many2many('product.template', string='Applicable Products')
    applicable_categories = fields.Many2many('product.category', string='Applicable Categories')

    active = fields.Boolean(string='Active', default=True)
    is_public = fields.Boolean(string='Public Coupon', default=False,
                               help='Visible to all customers')

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
            ])
            if existing:
                raise ValidationError("Coupon code must be unique.")

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date <= record.start_date:
                raise ValidationError("End date must be after start date.")

    @api.constrains('discount_value')
    def _check_discount_value(self):
        for record in self:
            if record.discount_type == 'percentage' and (
                record.discount_value <= 0 or record.discount_value > 100
            ):
                raise ValidationError("Percentage discount must be between 0 and 100.")
            elif record.discount_type == 'fixed' and record.discount_value <= 0:
                raise ValidationError("Fixed discount must be positive.")

    def validate_coupon(self, order_amount, customer_id=None):
        self.ensure_one()
        now = fields.Datetime.now()
        if not self.active:
            return {'valid': False, 'message': 'Coupon is inactive.'}
        if now < self.start_date or now > self.end_date:
            return {'valid': False, 'message': 'Coupon has expired.'}
        if self.usage_limit > 0 and self.usage_count >= self.usage_limit:
            return {'valid': False, 'message': 'Coupon usage limit reached.'}
        if order_amount < self.min_order_amount:
            return {
                'valid': False,
                'message': f'Minimum order amount is {self.min_order_amount}.',
            }
        return {'valid': True, 'message': 'Coupon is valid.'}

    def apply_discount(self, order_amount):
        self.ensure_one()
        if self.discount_type == 'percentage':
            discount = order_amount * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            discount = self.discount_value
        elif self.discount_type == 'free_shipping':
            discount = 0
        else:
            discount = 0
        if self.max_discount > 0:
            discount = min(discount, self.max_discount)
        self.usage_count += 1
        return discount
