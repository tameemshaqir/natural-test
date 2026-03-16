from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class CosmeticsSubscription(models.Model):
    _name = 'cosmetics.subscription'
    _description = 'Cosmetics Subscription Box'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Subscription Name', required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)

    plan_id = fields.Many2one('cosmetics.subscription.plan', string='Plan', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    next_billing_date = fields.Date(string='Next Billing Date')
    end_date = fields.Date(string='End Date')

    product_ids = fields.Many2many('product.template', string='Included Products')
    order_ids = fields.One2many('sale.order', 'subscription_id', string='Orders')
    total_orders = fields.Integer(string='Total Orders', compute='_compute_total_orders')

    recurring_price = fields.Float(string='Recurring Price', related='plan_id.price')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    @api.depends('order_ids')
    def _compute_total_orders(self):
        for sub in self:
            sub.total_orders = len(sub.order_ids)

    def action_activate(self):
        self.ensure_one()
        self.write({
            'status': 'active',
            'next_billing_date': self.start_date + relativedelta(months=1),
        })

    def action_pause(self):
        self.write({'status': 'paused'})

    def action_cancel(self):
        self.write({'status': 'cancelled', 'end_date': fields.Date.today()})

    def action_renew(self):
        self.ensure_one()
        if self.status == 'active':
            self.next_billing_date = self.next_billing_date + relativedelta(months=1)

    @api.model
    def _cron_process_subscriptions(self):
        """Cron job to process due subscriptions."""
        today = fields.Date.today()
        due_subscriptions = self.search([
            ('status', '=', 'active'),
            ('next_billing_date', '<=', today),
        ])
        for subscription in due_subscriptions:
            subscription._create_subscription_order()
            subscription.action_renew()

    def _create_subscription_order(self):
        self.ensure_one()
        order_vals = {
            'partner_id': self.customer_id.id,
            'is_subscription_order': True,
            'subscription_id': self.id,
        }
        order = self.env['sale.order'].create(order_vals)
        for product in self.product_ids:
            self.env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': product.product_variant_id.id,
                'product_uom_qty': 1,
                'price_unit': product.subscription_price or product.list_price,
            })
        return order


class SubscriptionPlan(models.Model):
    _name = 'cosmetics.subscription.plan'
    _description = 'Subscription Plan'

    name = fields.Char(string='Plan Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Price', required=True)
    duration_months = fields.Integer(string='Duration (Months)', default=0,
                                     help='0 = unlimited')
    max_products = fields.Integer(string='Max Products per Box', default=5)
    is_active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Plan Image')

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError("Price must be positive.")
