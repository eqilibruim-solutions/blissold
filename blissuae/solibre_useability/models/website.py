from odoo import models, fields, api, exceptions, _
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'
    _order = 'name'

    def sale_product_domain(self):
        res = super(Website, self).sale_product_domain()
        if self.env.company.limit_product_to_pricelist:
            pricelist = self.get_current_pricelist()
            ids = pricelist.item_ids.mapped('product_id.product_tmpl_id.id')
            res += [('id', 'in', ids)]
        partner_id = self.env.user.partner_id
        partners = partner_id | partner_id.commercial_partner_id | partner_id.commercial_partner_id.child_ids
        res += ['|',('partner_ids','=',False),('partner_ids','in',partner_id.ids)]
        return res

    def get_instagram_images(self):
        feed_images = []
        if self.social_instagram:
            instagram = self.social_instagram
            headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
            url = '%s/channel/?__a=1'%instagram
            _logger.info(url)
            page = requests.get(url, headers=headers)
            try:
                content = json.loads(page.text)
            except:
                _logger.info(page.text)
                return feed_images
            graphql = content.get('graphql')
            if graphql:
                user = graphql.get('user')
                if user:
                    edge_owner_to_timeline_media = user.get('edge_owner_to_timeline_media')
                    if edge_owner_to_timeline_media:
                        edges = edge_owner_to_timeline_media.get('edges')
                        for edge in edges:
                            node = edge.get('node')
                            feed_images.append(node.get('display_url'))
            return feed_images


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    show_pickup_location = fields.Boolean(string="Show pickup locations")
    pickup_location_id = fields.Many2one(string="Pickup Location", comodel_name="res.company")
