from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    skin_type = fields.Selection([
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('normal', 'Normal'),
    ], string='Skin Type')

    skin_concerns = fields.Many2many('cosmetics.skin.concern', string='Skin Concerns')
    date_of_birth = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ], string='Gender')

    loyalty_points = fields.Integer(string='Loyalty Points', default=0)
    loyalty_tier = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], string='Loyalty Tier', compute='_compute_loyalty_tier', store=True)

    wishlist_ids = fields.Many2many('product.template', string='Wishlist')
    referral_code = fields.Char(string='Referral Code')
    referred_by = fields.Many2one('res.partner', string='Referred By')
    subscription_ids = fields.One2many('cosmetics.subscription', 'customer_id', string='Subscriptions')
    review_ids = fields.One2many('product.review', 'customer_id', string='Reviews')

    preferred_brands = fields.Many2many('cosmetics.brand', string='Preferred Brands')
    allergies = fields.Text(string='Known Allergies')
    firebase_token = fields.Char(string='Firebase Push Token')

    @api.depends('loyalty_points')
    def _compute_loyalty_tier(self):
        for partner in self:
            points = partner.loyalty_points
            if points >= 10000:
                partner.loyalty_tier = 'platinum'
            elif points >= 5000:
                partner.loyalty_tier = 'gold'
            elif points >= 1000:
                partner.loyalty_tier = 'silver'
            else:
                partner.loyalty_tier = 'bronze'

    def add_loyalty_points(self, points):
        self.ensure_one()
        self.loyalty_points += points


class SkinConcern(models.Model):
    _name = 'cosmetics.skin.concern'
    _description = 'Skin Concern'

    name = fields.Char(string='Concern', required=True)
    description = fields.Text(string='Description')
