# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from odoo import models

class ThemeFashionAccessoriesEcommerceUltimate01_Ultimate(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_fashion_accessories_ecommerce_ultimate_01_post_copy(self, mod):
        self.enable_view('customize_theme_business.option_header_6')
        # self.enable_view('website.option_font_button_02_variables')
        # self.enable_view('website.option_font_title_04_variables')
        self.enable_view('customize_theme_business.option_input_1')
        self.enable_view('customize_theme_business.option_nav_color_primary')
        self.enable_view('customize_theme_business.option_nav_transparent_font_white')
        # self.enable_view('website.option_font_navbar_02_variables')
        self.enable_view('nav_side_menu_business.option_side_nav_1')
        self.enable_view('customize_theme_business.option_layout_default_container_variables')
        self.enable_view('customize_theme_business.option_mid_header_default')
        # self.enable_view('website.option_font_body_02_variables')
        self.enable_view('customize_theme_ecommerce.option_shop_style_3')
