# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Products Carousel Slider',
    'summary': 'Allows to drag & drop 2 types of product carousel '
               'sliders in website'
               '1.) Product Carousel Slider'
               '2.) Product Mini Carousel Slider',
    'description': 'Allows to drag & drop 2 types of product carousel '
                   'sliders in website'
                   '1.) Product Carousel Slider'
                   '2.) Product Mini Carousel Slider',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'data': [
        'data/filter_data.xml',
        'views/assets.xml',
        'views/product_view.xml',
        'views/product_carousel.xml',
        'views/product_mini_carousel.xml',
        'views/product_tab_carousel.xml',
    ],
    'depends': ['carousel_slider_73lines', 'website_sale_wishlist'],
    'images': [
        'static/description/snippet_product_carousel.jpg',
    ],
    'installable': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
