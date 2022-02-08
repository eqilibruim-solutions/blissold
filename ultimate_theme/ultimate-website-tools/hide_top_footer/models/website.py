
from odoo import api, fields, models, tools

class Page(models.Model):
    _inherit = 'website.page'

    header_hide = fields.Boolean()
    footer_hide = fields.Boolean()
