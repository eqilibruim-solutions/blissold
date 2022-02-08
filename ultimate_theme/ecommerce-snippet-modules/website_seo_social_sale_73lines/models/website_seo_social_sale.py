# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'website.seo.metadata']


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'website.seo.metadata']


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'website.seo.metadata']
