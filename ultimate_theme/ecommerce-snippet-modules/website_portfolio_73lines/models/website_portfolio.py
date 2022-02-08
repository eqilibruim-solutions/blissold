# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WebsitePortfolio(models.Model):
    _name = 'website.portfolio'
    # _inherit = ['carousel.slider']
    _description = 'Website Portfolio'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    date = fields.Date(string='Create Date', required=True)
    portfolio_image = fields.Binary(string='Portfolio Image')
    subtitle = fields.Char(string='Subtitle', translate=True)
    portfolio_desc = fields.Html(string='Description', translate=True)
    port_categ_id = fields.Many2one('portfolio.category',
                                    string='Portfolio Category', required=True)
    technology = fields.Char(string='Technology')
    external_link = fields.Char(string='External Link')

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Portfolio name already exists !'), ]


class PortfolioCategory(models.Model):
    _name = 'portfolio.category'
    # _inherit = ['carousel.slider']
    _description = 'Website Portfolio Category'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Portfolio Category already exists !'), ]
