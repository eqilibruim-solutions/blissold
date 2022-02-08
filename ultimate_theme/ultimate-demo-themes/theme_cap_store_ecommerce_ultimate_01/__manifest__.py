# -- encoding: utf-8 --
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': "Theme Cap Store Ecommerce Ultimate 01",
    'description': "Theme Cap Store Ecommerce Ultimate 01 By 73Lines",
    'category': "Theme",
    'author': "73lines",
    'summury': "Theme Cap Store Ecommerce Ultimate 01 ",
    'Website': "https://www.73lines.com",
    'version': "13.0.1.0",
    'depends': ["ultimate_website_tools_business",
                "ultimate_website_tools_ecommerce",
                "business_snippets_blocks_blog",
                "business_snippet_blocks_crm",
                "snippet_product_category_dynamic_73lines"],
    'data':[
        "views/assets.xml",
#         "views/customize_modal.xml",
        "views/templates.xml",
        "views/theme_data.xml",
        "views/image_library.xml"
    ],
     'images': [
         'static/description/cap_store_ecommerce_ultimate_01_screenshot.png',
    ],

     'license': "OPL-1",
}