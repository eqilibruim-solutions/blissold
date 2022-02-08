# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
# Some Part of This file is from Core Odoo.
# See LICENSE file for full copyright and licensing details.

import logging
import datetime
import dateutil.relativedelta as relativedelta
import functools
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID
# from odoo.addons.mail.models.mail_template import format_tz
from odoo.addons.mail.models.mail_template import format_datetime
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = ["product.public.category", "website.seo.metadata"]
    _name = 'product.public.category'


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,
        'cmp': cmp,
        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a,
                                                                      **kw),
    })
except (ImportError, IOError) as err:
    _logger.warning(err)


class ProductSeoConfig(models.Model):
    _name = 'product.seo.config'
    _description = 'Product Seo Config'

    # @api.model
    # def _default_categ_exp(self):
    #
    #     return data

    @api.model
    def _default_product_exp(self):
        icp = self.pool.get('ir.config_parameter')
        data = safe_eval(icp.get_param(self._cr, SUPERUSER_ID,
                                       'product_expr', 'False'))
        return data

    name = fields.Char("SEO Settings Name", required=True)
    model_object_field = fields.Many2one('ir.model.fields', string="Field",
                                         help="Select target field from the "
                                              "related document model.\n"
                                              "If it is a relationship field "
                                              "you will be able to select "
                                              "a target field at the "
                                              "destination of the "
                                              "relationship.")
    sub_object = fields.Many2one('ir.model', 'Sub-model', readonly=True,
                                 help="When a relationship field is selected "
                                      "as first field, this field shows "
                                      "the document model the "
                                      "relationship goes to.")
    sub_model_object_field = fields.Many2one('ir.model.fields', 'Sub-field',
                                             help="When a relationship "
                                                  "field is selected as "
                                                  "first field, this field "
                                                  "lets you select the "
                                                  "target field within the "
                                                  "destination document "
                                                  "model (sub-model).")
    null_value = fields.Char('Default Value', help="Optional value to use "
                                                   "if the target field "
                                                   "is empty")
    copyvalue = fields.Char('Placeholder Expression', help="Final placeholder "
                                                           "expression, to be "
                                                           "copy-pasted in "
                                                           "the desired "
                                                           "template field.")
    category_title_expr = fields.Char("Category Meta Title Expr.",
                                      default=lambda *a:
                                      "${object.name} | "
                                      "${object.parent_id.name} | "
                                      "${object.default_code} | "
                                      "Your Company")
    category_title_limit = fields.Integer("Title Size Limit", default=60)
    category_keyword_expr = fields.Char("Category Meta Description Expr.",
                                        default=lambda *a:
                                        "${object.name}, "
                                        "${object.parent_id.name}")
    category_keyword_limit = fields.Integer("Keyword Size Limit", default=140)
    category_desc_expr = fields.Char("Category Description Expr.",
                                     default=lambda *a:
                                     "${object.name} | "
                                     "${object.description_sale} | "
                                     "Your Company")
    category_desc_limit = fields.Integer("Description Size Limit", default=160)

    product_title_expr = fields.Char("Product Title Expr.",
                                     default=lambda *a:
                                     "${object.name} | "
                                     "${object.categ_id.name} | "
                                     "${object.default_code} | Your Company")
    product_title_limit = fields.Integer("Product Title Limit", default=60)
    product_keyword_expr = fields.Char("Product Keyword Expr.",
                                       default=lambda *a:
                                       "${object.name}, "
                                       "${object.categ_id.name}, "
                                       "${object.categ_id.parent_id.name}")
    product_keyword_limit = fields.Integer("Product Keyword Limit",
                                           default=140)
    product_desc_expr = fields.Char("Product Description Expr.",
                                    default=lambda *a:
                                    "${object.name} | "
                                    "${object.description_sale} | "
                                    "Your Company")
    product_desc_limit = fields.Integer("Product Description Limit",
                                        default=160)
    model_id = fields.Many2one('ir.model', 'Applies to',
                               help="The kind of document with with this "
                                    "template can be used")
    preview_categ_id = fields.Many2one("product.public.category")
    preview_product_id = fields.Many2one("product.template")
    preview_category_title = fields.Char("Preview Category Meta Title")
    preview_category_keyword = fields.Text("Preview Category Meta Description")
    preview_category_desc = fields.Text("Preview Category Description")
    preview_product_title = fields.Char("Preview Product Meta Title")
    preview_product_keyword = fields.Text("Preview Product Meta Description")
    preview_product_desc = fields.Text("Preview Product Description")
    categ_ids = fields.Many2many('product.public.category', 'seo_config_categ',
                                 'config_id', 'categ_id', 'Public Categories')
    product_ids = fields.Many2many('product.template', 'seo_config_prod',
                                   'config_id', 'product_id', 'Products')
    obj_name = fields.Selection(
        [('product.public.category', 'Public Category'),
         ('product.template', 'Product')], string="Object")

    def render_expr(self, template_txt, record, limit=80):
        template = mako_template_env.from_string(tools.ustr(template_txt))
        variables = {
            'format_datetime': lambda dt, tz=False, format=False, context=
            self._context: format_datetime(self.env, dt, tz, format),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }
        variables['object'] = record
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.info("Failed to render template %r using values %r" %
                         (template, variables), exc_info=True)
        return render_result[0:limit]

    @api.model
    def default_get(self, fields):
        rec = super(ProductSeoConfig, self).default_get(fields)
        categ_id = self.env['product.public.category'].search([])
        rec['preview_categ_id'] = categ_id and \
            categ_id[0] and categ_id[0].id or False
        product_id = self.env['product.template'].search([])
        rec['preview_product_id'] = product_id and \
            product_id[0] and product_id[0].id or False
        return rec

    def build_expression(self, field_name, sub_field_name, null_value):
        """Returns a placeholder expression for use in a template field,
        based on the values provided in the placeholder assistant.
        :param field_name: main field name
        :param sub_field_name: sub field name (M2O)
        :param null_value: default value if the target value is empty
        :return: final placeholder expression """
        expression = ''
        if field_name:
            expression = "${object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += "}"
        return expression

    @api.onchange('model_object_field', 'sub_model_object_field', 'null_value')
    def onchange_sub_model_object_value_field(self):
        if self.model_object_field:
            if self.model_object_field.ttype in \
                    ['many2one', 'one2many', 'many2many']:
                models = self.env['ir.model'].search([
                    ('model', '=', self.model_object_field.relation)])
                if models:
                    self.sub_object = models.id
                    self.copyvalue = self.build_expression(
                        self.model_object_field.name,
                        self.sub_model_object_field and
                        self.sub_model_object_field.name or False,
                        self.null_value or False)
            else:
                self.sub_object = False
                self.sub_model_object_field = False
                self.copyvalue = self.build_expression(
                    self.model_object_field.name, False,
                    self.null_value or False)
        else:
            self.sub_object = False
            self.copyvalue = False
            self.sub_model_object_field = False
            self.null_value = False

    @api.onchange('preview_categ_id', 'category_title_expr',
                  'category_keyword_expr', 'category_desc_expr',
                  'category_title_limit', 'category_keyword_limit',
                  'category_desc_limit')
    def onchange_preview_categ_id(self):
        self.preview_category_title = self.render_expr(
            self.category_title_expr, self.preview_categ_id,
            self.category_title_limit)
        self.preview_category_keyword = self.render_expr(
            self.category_keyword_expr, self.preview_categ_id,
            self.category_keyword_limit)
        self.preview_category_desc = self.render_expr(
            self.category_desc_expr, self.preview_categ_id,
            self.category_desc_limit)

    @api.onchange('obj_name')
    def onchange_obj_name(self):
        return {'domain': {'model_id': [('model', '=', self.obj_name)]}}

    @api.onchange('preview_product_id', 'product_title_expr',
                  'product_keyword_expr', 'product_desc_expr',
                  'product_title_limit', 'product_keyword_limit',
                  'product_desc_limit')
    def onchange_preview_product_id(self):
        self.preview_product_title = self.render_expr(
            self.product_title_expr, self.preview_product_id,
            self.product_title_limit)
        self.preview_product_keyword = self.render_expr(
            self.product_keyword_expr, self.preview_product_id,
            self.product_keyword_limit)
        self.preview_product_desc = self.render_expr(
            self.product_desc_expr, self.preview_product_id,
            self.product_desc_limit)

    def categ_seo_template_apply(self):
        for categ in self.categ_ids:
            categ.website_meta_title = self.render_expr(
                self.category_title_expr, categ, self.category_title_limit)
            categ.website_meta_keywords = self.render_expr(
                self.category_keyword_expr, categ, self.category_keyword_limit)
            categ.website_meta_description = self.render_expr(
                self.category_desc_expr, categ, self.category_desc_limit)

    def product_seo_template_apply(self):
        for product in self.product_ids:
            product.website_meta_title = self.render_expr(
                self.product_title_expr, product, self.product_title_limit)
            product.website_meta_keywords = self.render_expr(
                self.product_keyword_expr, product, self.product_keyword_limit)
            product.website_meta_description = self.render_expr(
                self.product_desc_expr, product, self.product_desc_limit)
