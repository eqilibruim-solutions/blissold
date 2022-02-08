{
    # Theme information
    'name': "Bliss",
    'description': """
    """,
    'category': 'Theme',
    'version': '1.0',
    'depends': ['website', 'web', 'website_mass_mailing', 'website_rating', 'website_sale_wishlist', 'payment'],

    # templates
    'data': [
        # 'data/website_menu.xml',
        'data/image_library.xml',
        'data/contetnt.xml',

        'views/layout.xml',
        'views/login.xml',
        'views/shop.xml',
        'views/product.xml',
        'views/my_bag.xml',
        'views/wishlist.xml',
        'views/shipping.xml',
        'views/payment.xml',
        'views/confirmation.xml',
        'views/portal_home.xml',
        'views/my_orders.xml',

        'views/assets.xml',
        'static/src/xml/product_best_sellers.xml',
        'static/src/xml/side_bar.xml',
        'static/src/xml/about_us_1.xml',
        'static/src/xml/about_us_2.xml',
        'static/src/xml/customer_care.xml',
        'views/snippets.xml',
    ],

    # demo pages
    'demo': [
        'demo/pages.xml',
    ],
    'qweb': ['static/src/xml/website_best_seller.xml',
             ],

    # Your information
    'author': "My Company",
    'website': "",
}
