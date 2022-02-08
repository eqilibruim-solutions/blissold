# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Business Snippets Blocks Blog',
    'description': 'Business Snippets Blocks Blog',
    'version': '13.0.1.0.1',
    'category': "Business",
    'author': "73Lines",
    'website': 'https://www.73lines.com/',
    'depends': [

        # Default Modules
        'website_blog',
        'carousel_slider_73lines',
        'snippet_blog_carousel_73lines',
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
    ],
    'images': [
        # 'static/description/pamela-ecommerce-banner.png',
    ],
    'price': 150,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': '',
    'application': True
}
