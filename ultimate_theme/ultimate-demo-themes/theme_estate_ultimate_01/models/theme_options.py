# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from odoo import models

class ThemeEstateUltimate01_Ultimate(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_estate_ultimate_01_post_copy(self, mod):
        self.enable_view('customize_theme_business.option_header_1')
        self.enable_view('customize_theme_business.option_input_1')
        self.enable_view('customize_theme_business.option_layout_default_container_variables')
        