# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

import base64
import random
import re
from datetime import datetime, timedelta
from odoo import api, fields, models, modules,tools
import logging
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.modules.module import get_resource_path
from odoo.http import request
from ast import literal_eval



class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    category_breadcrumbs_banner = fields.Binary(string='Category Breadcrumbs Banner')

    def get_categories(self):
        category_ids = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        res = {
            'categories': category_ids,
        }
        return res

# For Breadcrumbs On Shop Page

class Website(models.Model):
    _inherit = 'website'

    shop_breadcrumbs_banner_website = fields.Binary('Banner')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        image_path = get_resource_path('customize_theme_ecommerce','static/src/imgs', 'banner_imgs-2.png')
        if not self.shop_breadcrumbs_banner_website:
            with tools.file_open(image_path, 'rb') as f:
                self.shop_breadcrumbs_banner_website = base64.b64encode(f.read())

    shop_breadcrumbs_banner_website = fields.Binary('Banner', related="website_id.shop_breadcrumbs_banner_website",readonly=False)


