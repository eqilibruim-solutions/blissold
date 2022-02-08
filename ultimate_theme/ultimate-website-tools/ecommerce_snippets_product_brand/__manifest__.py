# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Ecommerce Snippets Product Brand',
    'description': 'Ecommerce Snippets Product Brand',
    'category': "Ecommerce",
    'author': "73Lines",
    'website': "https://www.73lines.com/",
    'version': "13.0.1.0.1",
        'depends': [

        # Default Modules
        'website_sale',
        'carousel_slider_73lines',
        'snippet_product_brand_carousel_73lines',
        'business_snippet_blocks_core',
        # 73lines Depend Modules

        # Don't forget to see README file in order to how to install
        # In order to install complete theme, uncomment the following.
        # Dependent modules are supplied in a zip file along with the theme,
        # if you have not received it,please contact us
        # at enquiry@73lines.com with proof of your purchase.
        ###############################################################



        ###############################################################

    ],
    'data': [
        'views/assets.xml',
        'views/brand_carousel/brand_carousel_1.xml',
        'views/brand_carousel/brand_carousel_2.xml',
        'views/brand_carousel/brand_carousel_3.xml',
        'views/brand_carousel/brand_carousel_4.xml',
        'views/brand_carousel/brand_carousel_5.xml',
        'views/brand_carousel/brand_carousel_6.xml',
        'views/brand_carousel/brand_carousel_7.xml',
        'views/brand_carousel/brand_carousel_8.xml',
        'views/brand_carousel/brand_carousel_9.xml',
    ],
    'images': [
        # 'static/description/pamela-ecommerce-banner.png',
    ],
    # 'price': 50,
    # 'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': '',
    'application': True
}
