# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from requests.utils import requote_uri

import logging
_logger = logging.getLogger(__name__)



class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_ids = fields.Many2many('res.company')
    requisition_type_id = fields.Many2one(string="Requisition type", comodel_name="purchase.requisition.type")
    user_id = fields.Many2one(string="Responsible", comodel_name="res.users")
    need_contract = fields.Boolean(string="Needs Contract")

class product_template(models.Model):

    _inherit = 'product.template'
    _order = 'has_partner,name'
    
    is_best_seller = fields.Boolean(string='Is Best Seller ?')
    standard_price = fields.Float(digits='Product Cost')
    available_in_crm = fields.Boolean(string="Visible in CRM")
    partner_ids = fields.Many2many(string='Partners', comodel_name='res.partner')
    has_partner = fields.Boolean(string="Has Partner", compute="get_has_partner", store=True)
    color = fields.Integer(string="Color")
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable product'),
        ], string='Product Type', default='product', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    stock_localisation_ids = fields.One2many(string="Locations",
                                             comodel_name="stock.localisation",
                                             inverse_name="product_tmpl_id")
    list_price = fields.Float(tracking=True)
    whatsapp_url = fields.Char('WhatsApp URL', compute='_compute_product_whatsapp_url', help='The full URL to access the document through the website.')
    purchase_requisition = fields.Selection(
        [('rfq', 'Create a draft purchase order'),
         ('tenders', 'Propose a call for tenders')],
        string='Procurement', default='tenders')

    def _is_quick_add_to_cart_possible(self, parent_combination=None):
        """
        It's possible to quickly add to cart if there's no optional product
        and there's only one possible combination, and no attribute is set
        to dynamic or no_variant, and no value is set to is_custom.

        :param parent_combination: combination from which `self` is an
            optional or accessory product
        :type parent_combination: recordset `product.template.attribute.value`

        :return: True if it's possible to quickly add to cart, else False
        :rtype: bool
        """
        self.ensure_one()

        if not self._is_add_to_cart_possible(parent_combination):
            _logger.info("#1")
            return False
        if len(self._get_possible_variants(parent_combination)) != 1:
            _logger.info("#2")
            return False
        if self._has_no_variant_attributes():
            _logger.info("#3")
            return False
        if self.has_dynamic_attributes():
            _logger.info("#4")
            return False
        if self._has_is_custom_values():
            _logger.info("#5")
            return False
        if self.optional_product_ids.filtered(lambda p: p._is_add_to_cart_possible(self._get_first_possible_combination())):
            _logger.info("#6")
            return False
        return True

    @api.depends('partner_ids')
    def get_has_partner(self):
        for prod in self:
            if prod.partner_ids:
                prod.has_partner = True
            else:
                prod.has_partner = False


    def _compute_product_whatsapp_url(self):
        for product in self:
            mobile = self.env.company.partner_id.mobile
            if mobile:
                mobile = mobile.replace('+','').replace(' ','')
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                product_url = '%s%s'%(base_url, product.website_url)
                url = "https://wa.me/%s?text=Hello,i would like to order %s [%s]"%(mobile,product.name,product_url)
                product.whatsapp_url = url

class ProductProduct(models.Model):

    _inherit = 'product.product'

    whatsapp_url = fields.Char('WhatsApp URL', compute='_compute_product_whatsapp_url', help='The full URL to access the document through the website.')
    image_url = fields.Char('image URL', compute='_compute_product_image_url', help='The full URL to access the document through the website.')
    standard_price = fields.Float(digits='Product Cost')

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        #if self.description_sale:
        #    name += '\n' + self.description_sale

        return name

    def _compute_product_image_url(self):
        for product in self:
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            if product.image_1024:
                image_url = '%s%s'%(base_url, self.env['website'].image_url(product,'image_1024'))
                product.image_url = requote_uri(image_url)
            else:
                product.image_url = False


    def _compute_product_whatsapp_url(self):
        for product in self:
            mobile = self.env.company.partner_id.mobile
            if mobile:
                mobile = mobile.replace('+','').replace(' ','')
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                product_url = '%s%s'%(base_url, product.website_url)
                url = "https://wa.me/%s?text=Hello,i would like to order %s [%s]"%(mobile,product.name,product_url)
                product.whatsapp_url = url

    def get_price_from_bom(self):
        return self._get_price_from_bom()

class ProductCustomerReference(models.Model):
    _name = 'product.customer.reference'
    _description = 'Product Customer Reference'

    name = fields.Many2one(string="Product", comodel_name="product.product")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    default_code = fields.Char(string="Reference")
    barcode = fields.Char(string="Barcode")
    

class ProductAddCategory(models.TransientModel):
    _name = 'product.add.category'
    _description = 'Product Add Category'


    public_categ_ids = fields.Many2many(
        'product.public.category', relation='add_product_public_category_product_template_rel',)    

    def set_product_categs(self):
        active_ids =self.env.context.get('active_ids')
        model = self.env.context.get('active_model')
        products = self.env[model].browse(active_ids)
        products.write({'public_categ_ids':[(6,0,self.public_categ_ids.ids)]})
        return True


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    cost_price = fields.Float(string="Cost", related="product_id.standard_price")
    margin = fields.Float(string="Margin", compute="get_margin")
    markup = fields.Float(string="Markup", compute="get_margin")

    def get_margin(self):
        for item in self:
            cost = item.cost_price or 1
            fixed_price = item.fixed_price or 1
            item.markup = ((fixed_price - cost) / cost)*100
            item.margin = ((fixed_price - cost) / fixed_price)*100

    
