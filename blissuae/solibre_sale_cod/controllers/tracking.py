#-*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class SolibreShipping(http.Controller):
    @http.route(['/track/<string:search>',
                 '/track'], type='http', auth="public", website=True)
    def track(self, search='', **post):
        sale = request.env['sale.order'].sudo().search([('name','=',search)])
        if len(sale) == 1:
            values = {'sale': sale}
            return request.render("solibre_sale_cod.tracking", values)
        return "Tracking number incorrect"

    @http.route('/geofence', type='json', auth="public", website=True, cors='*', csrf=False)
    def geofence(self, **post):
        return {'lon':25.5, 'lat':14.3, 'rad':2}

class SolibreRepair(http.Controller):
    @http.route('/set_location', auth='public', csrf=False)
    def set_location_index(self, **kw):
        _logger.info(kw)
        if not kw:
            return Response("No order found", status=412)
        lng = float(kw.get('lon'))
        lat = float(kw.get('lat'))
        msg_from = kw.get('from')
        phone = msg_from.split(':')[1]  
        track_sale = False
        name = '#####'
        _logger.info(phone)
        sale = request.env['sale.order'].sudo().search([('mobile','=',phone),
                                                        ('partner_latitude','=',0),
                                                        ('partner_longitude','=',0)])
        _logger.info(sale)
        if sale:
            sale.write({'partner_latitude':lat,
                        'partner_longitude':lng})
            track_sale = sale

        sale = request.env['sale.order'].sudo().search([('dest_mobile','=',phone),
                                                        ('dest_partner_latitude','=',0),
                                                        ('dest_partner_longitude','=',0)])
        _logger.info(sale)
        if sale:
            sale.write({'dest_partner_latitude':lat,
                        'dest_partner_longitude':lng})
            track_sale = sale
            name = track_sale.name
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = '%s/track/%s'%(base_url,track_sale and name or '')

        result = {
            "actions": [
                        {
                            "say": "Thanks, Track your order here: %s"%(url)
                        }
                    ]
            }
        headers = {'Content-Type': 'application/json'}
        _logger.info(headers)
        return Response(json.dumps(result), headers=headers)
