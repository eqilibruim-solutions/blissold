# -- encoding: utf-8 --
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': "Theme Wedding Ultimate 02",
    'description': "Theme Wedding Ultimate 02 By 73Lines",
    'category': "Theme",
    'author': "73lines",
    'summury': "Theme Wedding Ultimate 02 ",
    'Website': "https://www.73lines.com",
    'version': "13.0.1.0",
    'depends': ["ultimate_website_tools_business","business_snippets_blocks_blog","business_snippet_blocks_crm"],
    'data':[
        "views/assets.xml",
#         "views/customize_modal.xml",
        "views/templates.xml",
        "views/theme_data.xml",
        "views/image_library.xml"
    ],
     'images': [
         'static/description/wedding_ultimate_02_screenshot.png',
    ],
     'license': "OPL-1",
}