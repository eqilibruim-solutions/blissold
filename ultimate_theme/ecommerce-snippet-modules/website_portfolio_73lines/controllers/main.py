# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class WebsitePortfolio(http.Controller):
    @http.route(['/portfolio'], type='http', auth="public", website=True)
    def portfolios(self, **post):
        port_obj = request.env['website.portfolio']
        port_categ_obj = request.env['portfolio.category']
        posts = port_obj.search([])
        categ = port_categ_obj.search([])
        return request.render("website_portfolio_73lines.latest_portfolios", {
            'posts': posts,
            'categ': categ,
        })

    @http.route([
        "/portfolio/<model('portfolio.category'):website_portfolio_categ>/"
        "<model('website.portfolio'):website_portfolio>"],
        type='http', auth="public", website=True)
    def portfolios_details(self, website_portfolio, website_portfolio_categ,
                           enable_editor=None, **post):
        return request.render("website_portfolio_73lines.detail_portfolio", {
            'portfolio': website_portfolio,
        })
