from odoo import models, fields, api, exceptions, _
from odoo.osv.expression import get_unaccent_wrapper
import re
import json
import urllib
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _payment_earliest_date_search(self, cr, uid, obj, name, args, context=None):
        return[]

    def _get_amounts_and_date(self):
        '''
        Function that computes values for the followup functional fields. Note that 'payment_amount_due'
        is similar to 'credit' field on res.partner except it filters on user's company.
        '''

        return True

    #atualizat todos os clientes para (all) que nao estajam aprovisionados e termo de pagamento dif. de imediato
    def update_cron_warning_type(self):
        #partner_obj = self.env['res.partner']
        #partner_ids = partner_obj.search([('warning_type', '!=', False),'|', ('property_payment_term_id', '=', False),('property_payment_term_id.name', 'not ilike', 'imediat')])
        #partner_ids.write({'warning_type':'all'})
        return True

    @api.depends('date_birth')
    def _get_age(self):
        def compute_age_from_dates (date_birth):
            now = datetime.now()
            if (date_birth):
                delta = date.today() - date_birth
                deceased = ''
                years,days = divmod(delta.days, 365)
            else:
                years = "No DoB !"
            return years

        for partner in self:
            message = _("Age '%s'") % (compute_age_from_dates (partner.date_birth),)
            partner.age = compute_age_from_dates (partner.date_birth)

    warning_type = fields.Selection([('none', 'None'),('blocked', 'Blocked'), ('value', 'By amount'), ('date', 'By date'), ('all', 'All')], string='Credit block', required=True,  copy=False, default='none')
    credit_limit_days = fields.Integer(string="Credit days", copy=False, default='15')
    unreconciled_aml_ids = fields.One2many(comodel_name='account.move.line', inverse_name='partner_id', domain=['&', ('reconciled', '=', False), '&', ('account_id.user_type_id.type', '=', 'receivable'), ('move_id.state', '!=', 'draft')])
    payment_earliest_due_date = fields.Date(compute='_get_amounts_and_date',string = "Worst Due Date",fnct_search=_payment_earliest_date_search)
    overdue_move_id = fields.Many2one(string="Overdue move", comodel_name="account.move",compute='_get_amounts_and_date')
    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
        string='Customer Payment Terms',
        tracking=True)
    property_warehouse_id = fields.Many2one('stock.warehouse', company_dependent=True, string='Sales Warehouse')
    partner_latitude = fields.Float('Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float('Geo Longitude', digits=(16, 5))
    credit_limit = fields.Float(string="Credit Limit", tracking=True)
    over_credit = fields.Boolean('Allow Over Credit?')
    makani_number = fields.Char(string="Makani")
    stat = fields.Char(string="Stat")
    rcs = fields.Char(string="RCS")
    location_url = fields.Char(string="Location URL", compute="get_location_url")
    date_birth = fields.Date('Date of Birth')
    relation = fields.Selection(string="Relationship", selection=[('mother','Mother'),
                                                                  ('father','Father'),
                                                                  ('son','Son'),
                                                                  ('daughter','Daughter'),
                                                                  ('wife','Wife')])
    age = fields.Char(string="Age",compute="_get_age",method=True,size=32)
    nationality_country_id =  fields.Many2one(string="Nationality", comodel_name="res.country")
    pickup_location = fields.Boolean(string="is a pickup location?")
    team_id = fields.Many2one(string="Sales Team", comodel_name="crm.team")
    no_auto_invoice = fields.Boolean(string="No Auto Invoice")
    last_sale_date = fields.Datetime(string="Last Order Date")

    def update_last_sale_date(self, date=False):
        if not date:
            date = fields.Date.context_today(self)
        sales = self.env['sale.order'].search([('date_order','>=',date),('state','in',['sale','done'])], order="date_order asc")
        for sale in sales:
            sale.partner_id.last_sale_date = sale.date_order

    def _get_location_from_makani(self):
        self.ensure_one()
        if self.makani_number:
            url = 'https://www.makani.ae/MakaniPublicDataService/MakaniPublic.svc/GetMakaniDetails?makanino='
            makani_number = urllib.parse.quote_plus(self.makani_number)
            url = '%s%s'%(url,makani_number)
            result = requests.get(url)
            result = json.loads(result.text)
            result = json.loads(result)
            makani_info = result.get('MAKANI_INFO')
            if makani_info:
                return makani_info[0].get('LATLNG').split(',')

    @api.onchange('makani_number')
    def get_makani(self):
        url = 'https://www.makani.ae/MakaniPublicDataService/MakaniPublic.svc/GetMakaniDetails?makanino='
        for partner in self:
            if partner.makani_number:
                result = self._get_location_from_makani()
                if result:
                    partner.partner_latitude = result[0]
                    partner.partner_longitude = result[1]

    def geo_localize(self):
        if self.makani_number:
            result = self._get_location_from_makani()
            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner)
                })                
            return True
        else:
            return super(ResPartner, self).geo_localize()

    def get_location_url(self):
        for partner in self:
            if partner.partner_longitude and partner.partner_latitude:
                lng = partner.partner_longitude
                lat = partner.partner_latitude
                partner.location_url = 'https://www.google.com/maps/dir/Current+Location/%s,%s'%(lat,lng)
            else:
                partner.location_url = ''

    @api.onchange('credit_limit')
    def change_credit_limit(self):
        if not self.user_has_groups('account.group_account_user') and self.credit_limit:
            raise exceptions.ValidationError("Sorry you are unable to update this information") 

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        self = self.with_user(name_get_uid or self.env.uid)
        # as the implementation is in SQL, we force the recompute of fields if necessary
        self.recompute(['display_name'])
        self.flush()
        if args is None:
            args = []
        order_by_rank = self.env.context.get('res_partner_search_mode')
        if (name or order_by_rank) and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            from_str = from_clause if from_clause else 'res_partner'
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            fields = self._get_name_search_order_by_fields()

            query = """SELECT res_partner.id
                         FROM {from_str}
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR {reference} {operator} {percent}
                           OR {vat} {operator} {percent}
                           OR {mobile} {operator} {percent}

                           )

                           -- don't panic, trust postgres bitmap
                     ORDER BY {fields} {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(from_str=from_str,
                               fields=fields,
                               where=where_str,
                               operator=operator,
                               email=unaccent('res_partner.email'),
                               display_name=unaccent('res_partner.display_name'),
                               reference=unaccent('res_partner.ref'),
                               percent=unaccent('%s'),
                               vat=unaccent('res_partner.vat'),
                               mobile=unaccent('res_partner.mobile'),
                               )

            where_clause_params += [search_name]*3  # for email / display_name, reference
            where_clause_params += [re.sub('[^a-zA-Z0-9]+', '', search_name) or None]  # for vat
            where_clause_params += [search_name] # for mobile
            where_clause_params += [search_name]  # for order by
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = [row[0] for row in self.env.cr.fetchall()]

            if partner_ids:
                return models.lazy_name_get(self.browse(partner_ids))
            else:
                return []
        return super(ResPartner, self)._name_search(name, args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def send_overdue_statement(self):
        return

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        """Override for sales order.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        return

    def action_send_overdue_report(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        return
