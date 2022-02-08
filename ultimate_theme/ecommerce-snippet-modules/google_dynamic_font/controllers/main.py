# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
import base64
from lxml import etree
import requests

from odoo import http
from odoo.http import request
from odoo.addons.web_editor.controllers.main import Web_Editor

google_font_base_url = 'https://fonts.googleapis.com/css?family='
tmp_font_file_href = '/google_dynamic_font/static/src/scss/primary_font_variables.scss'
font_var = {
    'title': '$o-theme-headings-font-number',
    'body': '$o-theme-font-number',
    'button': '$o-theme-buttons-font-number',
    'navbar': '$o-theme-navbar-font-number'
}


class GoogleDymanicFont(Web_Editor):

    def create_model_data(self, rec):
        try:
            IrModelData = request.env['ir.model.data']
            data = IrModelData.search([('model', '=', rec._name), ('res_id', '=', rec.id)])
            if data:
                data.write({})
            else:
                IrModelData.create({
                    'name': rec.display_name,
                    'model': rec._name,
                    'res_id': rec.id,
                    'module': 'web_studio',
                })
        except:
            pass

    def save_scss_index(self, name, index):
        IrAttachment = request.env["ir.attachment"]
        IrUiView = request.env["ir.ui.view"]

        view_to_xpath = request.env.ref('website._assets_primary_variables', False)
        scss_url = '/website/static/src/scss/options/fonts/option_font_%s_%s_variables.scss' % (name, index)
        file_name = 'option_font_%s_%s_variables.scss' % (name, index)

        custom_attachment = self.get_custom_attachment(scss_url)
        datas = base64.b64encode(('%s: %s;' % (font_var[name], int(index))).encode("utf-8"))
        if custom_attachment:
            custom_attachment.write({"datas": datas})
        else:
            new_attach = {
                'name': file_name,
                'type': "binary",
                'mimetype': "text/scss",
                'datas': datas,
                'datas_fname': scss_url.split("/")[-1],
                'url': scss_url,
            }
            IrAttachment.create(new_attach)
        # view = IrUiView.search([('key', '=', 'option_font_%s_%s_variables' % (name, index))], limit=1)
        view = request.env.ref('web_studio.option_font_%s_%s_variables' % (name, index), False)
        if not view:
            new_view = {
                'name': 'option_font_%s_%s_variables' % (name, index),
                'key': 'web_studio.option_font_%s_%s_variables' % (name, index),
                'mode': "extension",
                'website_id': False,
                'active': False,
                'inherit_id': view_to_xpath.id,
                'arch': """<?xml version="1.0"?>
<data inherit_id="%(inherit_xml_id)s" active="False">
    <xpath expr="//link[last()]" position="after">
        <link rel="stylesheet" type="text/scss" href="%(url)s"/>
    </xpath>
</data>""" % {
                    'inherit_xml_id': view_to_xpath.xml_id,
                    'url': scss_url
                }
            }
            new_view.update(self.save_scss_view_hook())
            v = IrUiView.create(new_view)
            v.write({'website_id': False})
            self.create_model_data(v)
        request.env["ir.qweb"].clear_caches()

    def create_options(self, index):
        def _get_xml(idx, xpath_xmlid):
            xml = '''
                <data inherit_id="%(xpath_xmlid)s">
                    <xpath expr="//list[@id='theme_customize_content_fonts_title']/opt[last()]" position="after">
                        <opt data-xmlid="web_studio.option_font_title_%(str_index)s_variables" data-font="%(index)s"/>
                    </xpath>
                    <xpath expr="//list[@id='theme_customize_content_fonts_body']/opt[last()]" position="after">
                        <opt data-xmlid="web_studio.option_font_body_%(str_index)s_variables" data-font="%(index)s"/>
                    </xpath>
                    <xpath expr="//list[@id='theme_customize_content_fonts_button']/opt[last()]" position="after">
                        <opt data-xmlid="web_studio.option_font_button_%(str_index)s_variables" data-font="%(index)s"/>
                    </xpath>
                    <xpath expr="//list[@id='theme_customize_content_fonts_navbar']/opt[last()]" position="after">
                        <opt data-xmlid="web_studio.option_font_navbar_%(str_index)s_variables" data-font="%(index)s"/>
                    </xpath>
                </data>
            ''' % {
                'str_index': idx,
                'index': int(idx),
                'xpath_xmlid': xpath_xmlid,
            }
            return xml

        view = request.env.ref('google_dynamic_font.theme_customize', False)
        IrUiView = request.env["ir.ui.view"]
        if view:
            f_view = IrUiView.search([('key', '=', 'web_studio.theme_customize'), ('website_id', '=', request.website.id)], limit=1)
            if f_view:
                root = etree.fromstring(f_view.arch_base)
                tree = etree.fromstring(_get_xml(index, view.id))
                tmp = tree.findall('.//xpath')
                for t in tmp:
                    root.append(t)
                content = etree.tostring(root).decode('utf-8')
                f_view.write({
                    'arch_base': content
                })
            else:
                new_view = {
                    'name': 'theme_customize',
                    'key': 'web_studio.theme_customize',
                    'mode': "extension",
                    'inherit_id': view.id,
                    'arch': """
                            %(content)s
                        """ % {
                        'content': _get_xml(index, view.id),
                    }
                }
                new_view.update(self.save_scss_view_hook())
                IrUiView.create(new_view)
        request.env["ir.qweb"].clear_caches()

    def _is_exists_font(self, font):
        # return parameters (exist / index / content)
        def _get_index(content):
            count = content.count('append')
            index = 7
            if count >= 3:
                index = int(count / 3) + 7
            return index

        datas = ''
        custom_url = self._make_custom_scss_file_url(tmp_font_file_href, 'web.assets_common')
        attachment = self.get_custom_attachment(custom_url)
        if attachment:
            datas = base64.b64decode((attachment.datas).decode("utf-8")).decode('utf-8')
            if font in datas:
                return (True, False, datas)
            else:
                return (False, _get_index(datas), datas)
        return (False, _get_index(''), datas)

    @http.route(['/web/add_google_font'], type='json', website=True, auth="user")
    def add_google_font(self, url=None):
        if url:
            if google_font_base_url in url:
                r = requests.get(url)
                if r.status_code == 200:
                    font = url.split('=')[1]
                    name = font.split(':')[0].replace('+', ' ')
                    is_exists, index, datas = self._is_exists_font(font)
                    if not is_exists:
                        datas = datas + '''
$o-theme-fonts: append($o-theme-fonts, ('%s', sans-serif));
$o-theme-font-urls: append($o-theme-font-urls, '%s');
$o-theme-font-names: append($o-theme-font-names, '%s');''' % (name, font, name)
                        self.save_scss(tmp_font_file_href, 'web.assets_common', datas)
                        option_name = ['title', 'body', 'navbar', 'button']
                        for t in option_name:
                            self.save_scss_index(t, str(index).zfill(2))
                        self.create_options(str(index).zfill(2))
                        return {'success': 'font added successfully'}
                    else:
                        return {'error': 'Font Already exits.....!'}
                else:
                    return  {'error': 'Please Enter Valid Google Font URL.'}
        return {'error': 'Please Enter Valid Google Font URL.'}

    @http.route(['/web/remove_google_font'], type='json', website=True, auth="user")
    def remove_google_font(self, xmlid=None):
        def _get_remove_xml(xpath_xml_id):
            return '''
            
                <xpath expr="//opt[@data-xmlid='%(xmlid)s']" position="replace" />
            
            ''' % {'xmlid': xpath_xml_id}
    
        IrUiView = request.env["ir.ui.view"]
        tmp = xmlid.split('.')
        if len(tmp) > 1:
            view = self.get_custom_view(tmp[1])
            if view:
                view.write({'active': False})

        option_view = IrUiView.search([('key', '=', 'web_studio.theme_customize'), ('website_id', '=', request.website.id)], limit=1)
        if option_view:
            root = etree.fromstring(option_view.arch_base)
            tree = etree.fromstring(_get_remove_xml(xmlid))
            root.append(tree)
            content = etree.tostring(root).decode('utf-8')
            try:
                option_view.write({
                    'arch': content
                })
            except:
                return False
            request.env["ir.qweb"].clear_caches()
            return True
        return False
