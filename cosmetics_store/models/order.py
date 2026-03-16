from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_method = fields.Selection([
        ('standard', 'Standard Shipping (5-7 days)'),
        ('express', 'Express Shipping (2-3 days)'),
        ('overnight', 'Overnight Shipping'),
        ('free', 'Free Shipping'),
    ], string='Shipping Method', default='standard')

    tracking_number = fields.Char(string='Tracking Number')
    tracking_url = fields.Char(string='Tracking URL')
    estimated_delivery = fields.Date(string='Estimated Delivery')
    delivery_notes = fields.Text(string='Delivery Notes')

    coupon_code = fields.Char(string='Coupon Code')
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount', store=True)
    affiliate_id = fields.Many2one('cosmetics.affiliate', string='Referred By')
    is_subscription_order = fields.Boolean(string='Subscription Order', default=False)
    subscription_id = fields.Many2one('cosmetics.subscription', string='Subscription')

    payment_method = fields.Selection([
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
        ('cod', 'Cash on Delivery'),
    ], string='Payment Method')
    payment_reference = fields.Char(string='Payment Reference')
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], string='Payment Status', default='pending')

    order_status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], string='Order Status', default='pending', tracking=True)

    @api.depends('order_line.price_subtotal', 'coupon_code')
    def _compute_discount(self):
        for order in self:
            discount = 0.0
            if order.coupon_code:
                coupon = self.env['cosmetics.discount'].search([
                    ('code', '=', order.coupon_code),
                    ('active', '=', True),
                ], limit=1)
                if coupon:
                    if coupon.discount_type == 'percentage':
                        discount = order.amount_untaxed * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
                    if coupon.max_discount > 0:
                        discount = min(discount, coupon.max_discount)
            order.discount_amount = discount

    def action_confirm_order(self):
        self.write({'order_status': 'confirmed'})

    def action_process_order(self):
        self.write({'order_status': 'processing'})

    def action_ship_order(self):
        self.write({'order_status': 'shipped'})

    def action_deliver_order(self):
        self.write({'order_status': 'delivered'})

    def action_cancel_order(self):
        self.write({'order_status': 'cancelled'})
