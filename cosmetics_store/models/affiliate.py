from odoo import models, fields, api
from odoo.exceptions import ValidationError
import uuid


class CosmeticsAffiliate(models.Model):
    _name = 'cosmetics.affiliate'
    _description = 'Affiliate / Referral Partner'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'total_earnings desc'

    name = fields.Char(string='Affiliate Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    referral_code = fields.Char(string='Referral Code', required=True, copy=False,
                                default=lambda self: str(uuid.uuid4())[:8].upper())

    commission_rate = fields.Float(string='Commission Rate (%)', default=10.0)
    status = fields.Selection([
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ], string='Status', default='pending', tracking=True)

    total_referrals = fields.Integer(string='Total Referrals',
                                     compute='_compute_stats', store=True)
    total_earnings = fields.Float(string='Total Earnings',
                                  compute='_compute_stats', store=True)
    pending_payout = fields.Float(string='Pending Payout',
                                  compute='_compute_stats', store=True)

    referral_ids = fields.One2many('cosmetics.affiliate.referral', 'affiliate_id',
                                   string='Referrals')
    payout_ids = fields.One2many('cosmetics.affiliate.payout', 'affiliate_id',
                                 string='Payouts')

    bank_account = fields.Char(string='Bank Account / PayPal Email')
    notes = fields.Text(string='Notes')

    @api.depends('referral_ids', 'referral_ids.commission_amount',
                 'referral_ids.status', 'payout_ids', 'payout_ids.amount')
    def _compute_stats(self):
        for affiliate in self:
            referrals = affiliate.referral_ids
            affiliate.total_referrals = len(referrals)
            affiliate.total_earnings = sum(
                r.commission_amount for r in referrals if r.status == 'confirmed'
            )
            total_paid = sum(p.amount for p in affiliate.payout_ids if p.status == 'paid')
            affiliate.pending_payout = affiliate.total_earnings - total_paid

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        for record in self:
            if record.commission_rate < 0 or record.commission_rate > 50:
                raise ValidationError("Commission rate must be between 0% and 50%.")

    def action_approve(self):
        self.write({'status': 'active'})

    def action_suspend(self):
        self.write({'status': 'suspended'})


class AffiliateReferral(models.Model):
    _name = 'cosmetics.affiliate.referral'
    _description = 'Affiliate Referral'
    _order = 'create_date desc'

    affiliate_id = fields.Many2one('cosmetics.affiliate', string='Affiliate',
                                   required=True, ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string='Referred Customer', required=True)
    order_id = fields.Many2one('sale.order', string='Order')
    order_amount = fields.Float(string='Order Amount')
    commission_amount = fields.Float(string='Commission Amount')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')

    @api.onchange('order_id')
    def _onchange_order(self):
        if self.order_id:
            self.order_amount = self.order_id.amount_total
            self.commission_amount = (
                self.order_amount * self.affiliate_id.commission_rate / 100
            )


class AffiliatePayout(models.Model):
    _name = 'cosmetics.affiliate.payout'
    _description = 'Affiliate Payout'
    _order = 'create_date desc'

    affiliate_id = fields.Many2one('cosmetics.affiliate', string='Affiliate',
                                   required=True, ondelete='cascade')
    amount = fields.Float(string='Amount', required=True)
    payment_method = fields.Selection([
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ], string='Payment Method', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ], string='Status', default='pending')
    payment_reference = fields.Char(string='Payment Reference')
    notes = fields.Text(string='Notes')
