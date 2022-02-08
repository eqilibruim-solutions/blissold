# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from odoo import models

class ThemeWeddingEcommerceUltimate02_Ultimate(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_wedding_ecommerce_ultimate_02_post_copy(self, mod):
        self.enable_view('customize_theme_ecommerce.option_shop_style_2')

