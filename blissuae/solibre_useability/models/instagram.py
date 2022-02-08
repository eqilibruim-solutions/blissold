from odoo import models, fields, api, exceptions, _
from lxml import html
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class InstagramPost(models.Model):
    _name = 'instagram.post'
    _description = 'Instagram Post'

    name = fields.Char(string="Name")
    image_url = fields.Char(string="Image URL")

    @api.model
    def get_feedimages(self):
        website_ids = self.env['website'].search([])
        for website_id in website_ids:
            instagram = website_id.social_instagram
            headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        
            user='vanilla.beans.store'
            user='lana_yes'
            page = requests.get('%s/channel/?__a=1'%instagram, headers=headers)
            _logger.info(page.text)
            content = json.loads(page.text)
            graphql = content['graphql']
            user = graphql['user']
            edge_owner_to_timeline_media = user['edge_owner_to_timeline_media']
            edges = edge_owner_to_timeline_media['edges']
            for edge in edges:
                count +=1
                _loger.info(edge['node'])
                image_url = edge['node'].get('display_url')
                if not self.search([('website_id','=',website_id.id),('image_url','=',image_url)]):
                    self.create({'website_id':website_id.id,
                                 'name':image_url,
                                 'image_url':image_url})
