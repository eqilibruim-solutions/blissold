#-*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug import url_encode
import werkzeug
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json
from odoo.http import request, Response
from werkzeug.exceptions import Forbidden, NotFound
import logging

_logger = logging.getLogger(__name__)

    

class SolibreSaleCod(http.Controller):

    @http.route('/update/<string:order>/<string:state>',auth='public', csrf=False)
    def update_shipping_state(self, order=False, state=False, *kw):
        return Forbidden()

    @http.route('/new_sale_tracking',type="http", auth='public', methods=['POST'],csrf=False)
    def create_new_sale_tracking(self, **post):
        data = [post.get('order_id'),post.get('activity_id'),post.get('state_id')]
        fields = ['order_id','activity_id/id','state_id/id']
        order = request.env['sale.order'].sudo().search([('name','=',post.get('order_id'))])
        result = request.env['sale.order.tracking'].with_user(order.user_id.id).load(fields,[data])
        headers = {}
        return Response(json.dumps(result), headers=headers)


    @http.route('/delivery', auth='user')
    def index(self, **kw):
        schedules = []
        orders = schedules.mapped('order_ids')
        values = {'orders': orders}
        return request.render("solibre_sale_cod.delivery", values)


    @http.route('/deliver', auth='user')
    def deliver_redirect(self, **kw):
        url_params = {
            'model': 'sale.order',
            'action': False,
            'view_type': 'kanban',

        }
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = '%s/web?#%s' % (base_url,url_encode(url_params))
        return werkzeug.utils.redirect(url)


