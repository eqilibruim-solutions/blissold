# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from odoo import models

class ThemeTeaEcommerceUltimate01_Ultimate(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_tea_ecommerce_ultimate_01_post_copy(self, mod):
        self.enable_view('customize_theme_ecommerce.option_shop_style_1')


