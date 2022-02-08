# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from odoo import models

class ThemeJewelleryEcommerceUltimate02_Ultimate(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_jewellery_ecommerce_ultimate_02_post_copy(self, mod):
        self.enable_view('customize_theme_business.option_header_5')
        # self.enable_view('customize_theme_business.option_font_button_08_variables')
        # self.enable_view('customize_theme_business.option_font_title_07_variables')
        self.enable_view('customize_theme_business.option_input_2')
        self.enable_view('customize_theme_business.option_mid_header_default')
        self.enable_view('customize_theme_business.option_nav_transparent_font_default')
        # self.enable_view('customize_theme_business.option_font_navbar_08_variables')
        self.enable_view('customize_theme_business.option_nav_hover_top_border')
        self.enable_view('nav_side_menu_business.option_side_nav_1')
        self.enable_view('customize_theme_business.option_layout_default_container_variables')
        # self.enable_view('customize_theme_business.option_font_body_08_variables')
        self.enable_view('customize_theme_ecommerce.option_shop_style_2')


