# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.http import request
import requests
import json
import werkzeug
import base64

import logging
_logger = logging.getLogger(__name__)

import datetime
from odoo.addons.phone_validation.tools import phone_validation

from odoo.addons.website_sale.controllers import main

SITEMAP_CACHE_TIME = datetime.timedelta(hours=1)

class WebsiteStockPage(http.Controller):

    @http.route(['/stock/link'], type='http', auth="public", website=True)
    def stock_link(self, **post):
        values = {}
        return request.render("solibre_useability.stock_link", values)

    @http.route('/pay/<string:res_model>/<string:access_token>', type='http', auth="public")
    def open_payment_line(self, res_model,access_token, **post):
        values = {}
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        order = request.env[res_model].sudo().search([('access_token','=',access_token)],limit=1)
        if res_model == 'sale.order':
            if order.amount_total > sum(order.invoice_ids.mapped('amount_total')):
                return werkzeug.utils.redirect(order._get_share_url())
            else:
                invoices = order.invoice_ids.filtered(lambda i:i.state in ('open','posted'))

                if invoices:
                    for invoice in invoices:
                        return werkzeug.utils.redirect(invoice._get_share_url())
        return werkzeug.utils.redirect(order._get_share_url())
            # url = '%s/website_payment/pay?reference=%s&amount=%s&currency_id=%s&partner_id=%s&order_id=%s&access_token=%s' % (base_url, order.name, order.amount_total, order.currency_id.id, order.partner_id.id, order.id, order.access_token)
        # return werkzeug.utils.redirect(order._get_share_url())


class WebsiteSale(main.WebsiteSale):
    @http.route(['/shop/update_delivery_location'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_delivery_location(self, **post):
        order = request.website.sale_get_order()
        pickup_location_id = int(post['pickup_location'])
        order.write({'pickup_location_id': pickup_location_id})


    def _get_search_order(self, post):
        res = super(WebsiteSale, self)._get_search_order(post)
        res = 'is_best_seller desc,has_partner desc,' + res
        return res

    def checkout_form_validate(self, mode, all_form_values, data):

        error = dict()
        error_message = []

        if data.get("mobile"):
            data["mobile"] = data.get("mobile").strip()

        standard_error, standard_error_message = super(WebsiteSale, self).checkout_form_validate(
            mode, all_form_values, data
        )

        error.update(standard_error)
        error_message += standard_error_message

        if data.get("mobile"):
            try:
                phone = data.get("mobile")
                country = request.env["res.country"].sudo().browse(data.get("country_id"))
                data["mobile"] = phone_validation.phone_format(
                    phone,
                    country.code if country else None,
                    country.phone_code if country else None,
                    force_format="INTERNATIONAL",
                    raise_exception=True,
                )
            except Exception as e:
                error["mobile"] = "error"
                error_message.append(e.args[0])

        return error, error_message

    @http.route('/fbfeed.xml', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def fbfeed_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        View = request.env['ir.ui.view'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return Attachment.create({
                'datas': base64.b64encode(content),
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })
        dom = [('url', '=', '/fbfeed-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)
        if sitemap:
            # Check if stored version is still valid
            create_date = fields.Datetime.from_string(sitemap.create_date)
            delta = datetime.datetime.now() - create_date
            if delta < SITEMAP_CACHE_TIME:
                content = base64.b64decode(sitemap.datas)

        if not content:
            # Remove all sitemaps in ir.attachments as we're going to regenerated them
            dom = [('type', '=', 'binary'), '|', ('url', '=like', '/fbfeed-%d-%%.xml' % current_website.id),
                   ('url', '=', '/fbfeed-%d.xml' % current_website.id)]
            sitemaps = Attachment.search(dom)
            sitemaps.unlink()

            pages = 0
            products = request.env['product.product'].search([('is_published','=',True)])
            if products:
                values = {
                    'products': products,
                    'company_id': request.env.company,
                    'url_root': request.httprequest.url_root[:-1],
                }
                items = View.render_template('solibre_useability.fbfeed_items', values)
                if items:
                    values = {
                        'content': items,
                        'company_id': request.env.company,
                        'url_root': request.httprequest.url_root[:-1],
                    }
                    content = View.render_template('solibre_useability.fbfeed_xml', values)
                    content = content.decode().replace('url','link')
                    content = content.replace('image_link', 'g:image_link')
                    content = content.replace('price', 'g:price')
                    content = content.replace('shipping', 'g:shipping')
                    content = content.replace('country', 'g:country')
                    content = content.replace('service', 'g:service')
                    content = content.replace('availability', 'g:availability')
                    content = content.encode()
                    last_sitemap = create_sitemap('/fbfeed-%d-%d.xml' % (current_website.id, pages), content)

        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route('/googlefeed.xml', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def googlefeed_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        View = request.env['ir.ui.view'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return Attachment.create({
                'datas': base64.b64encode(content),
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })
        dom = [('url', '=', '/googlefeed-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)
        if sitemap:
            # Check if stored version is still valid
            create_date = fields.Datetime.from_string(sitemap.create_date)
            delta = datetime.datetime.now() - create_date
            if delta < SITEMAP_CACHE_TIME:
                content = base64.b64decode(sitemap.datas)
        if not content:
            # Remove all sitemaps in ir.attachments as we're going to regenerated them
            dom = [('type', '=', 'binary'), '|', ('url', '=like', '/googlefeed-%d-%%.xml' % current_website.id),
                   ('url', '=', '/googlefeed-%d.xml' % current_website.id)]
            sitemaps = Attachment.search(dom)
            sitemaps.unlink()

            pages = 0
            category = request.env.ref('solibre_useability.Googlefeed').id
            products = request.env['product.product'].search([('is_published', '=', True), ('public_categ_ids', 'child_of', int(category))])
            if not products:
                products = request.env['product.product'].search([('is_published', '=', True)])
            if products:
                values = {
                    'products': products,
                    'company_id': request.env.company,
                    'url_root': request.httprequest.url_root[:-1],
                }
                items = View.render_template('solibre_useability.googlefeed_items', values)
                if items:
                    values = {
                            'content': items,
                            'company_id': request.env.company,
                            'url_root': request.httprequest.url_root[:-1],}
                    content = View.render_template('solibre_useability.googlefeed_xml', values)
                    content = content.decode().replace('url', 'link')
                    content = content.replace('image_link', 'g:image_link')
                    content = content.replace('price', 'g:price')
                    content = content.replace('shipping', 'g:shipping')
                    content = content.replace('country', 'g:country')
                    content = content.replace('service', 'g:service')
                    content = content.replace('availability', 'g:availability')
                    content = content.encode()
                    last_sitemap = create_sitemap('/googlefeed-%d-%d.xml' % (current_website.id, pages), content)

        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route('/instagramfeed', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def instagramfeed_index(self, **kwargs):
        instagram = request.website.social_instagram
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        from lxml import html
        user='vanilla.beans.store'
        user='lana_yes'
        page = requests.get('%s/channel/?__a=1'%instagram, headers=headers)
        content = json.loads(page.text)
        graphql = content['graphql']
        user = graphql['user']
        edge_owner_to_timeline_media = user['edge_owner_to_timeline_media']
        edges = edge_owner_to_timeline_media['edges']
        count = 0
        body = """<body>"""
        for edge in edges:
            count +=1
            image_url = edge['node'].get('display_url')
            body += '<img src="%s" style="width:25%%"/>'%image_url
        body += """</body>"""
        return request.make_response(body,{
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Methods': 'GET',
            })
