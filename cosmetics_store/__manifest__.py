{
    'name': 'Cosmetics Store',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Complete e-commerce system for selling cosmetic products',
    'description': """
        Cosmetics Store Management System
        ==================================
        A comprehensive e-commerce platform for cosmetic products featuring:
        - Product management with cosmetic-specific attributes
        - Subscription boxes (monthly cosmetic boxes)
        - Affiliate/referral system
        - Discount and coupon management
        - Customer management with skin profiles
        - Order management with shipping integration
        - Analytics dashboards
        - REST API for mobile app integration
        - AI-powered product recommendations
    """,
    'author': 'Cosmetics Store',
    'website': 'https://www.cosmetics-store.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'stock',
        'account',
        'website_sale',
        'mail',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_category_data.xml',
        'views/product_views.xml',
        'views/order_views.xml',
        'views/customer_views.xml',
        'views/subscription_views.xml',
        'views/discount_views.xml',
        'views/affiliate_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cosmetics_store/static/src/css/dashboard.css',
            'cosmetics_store/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
