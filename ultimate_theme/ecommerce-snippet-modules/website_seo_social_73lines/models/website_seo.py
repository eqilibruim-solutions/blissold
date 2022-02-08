# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Website(models.Model):
    _inherit = "website"

    def get_canonical_url(self, req=None):
        return req.url


class SeoMetadata(models.AbstractModel):
    _inherit = 'website.seo.metadata'

    website_image_url = fields.Text("Website Image", translate=True)
    website_og_title = fields.Char("Website og title", translate=True)
    website_og_description = fields.Text("Website og description",
                                         translate=True)
    website_og_locale = fields.Text("Website og Locale", translate=True)
    website_og_type = fields.Text("Website og Type", translate=True)
    website_og_url = fields.Text("Website og URL", translate=True)
    website_og_site_name = fields.Text("Website og Site Name", translate=True)
    website_og_image = fields.Text("Website og Image", translate=True)
    website_og_article_publisher = fields.Text("Website Article Publisher",
                                               translate=True)
    website_twitter_card = fields.Text("Website Twitter Card", translate=True)
    website_twitter_description = fields.Text("Website Twitter Description",
                                              translate=True)
    website_twitter_title = fields.Text("Website Twitter Title",
                                        translate=True)
    website_twitter_site = fields.Text("Website Twitter Site", translate=True)
    website_twitter_domain = fields.Text("Website Twitter Domain",
                                         translate=True)
    website_twitter_image_src = fields.Text("Website Image Src",
                                            translate=True)
    website_twitter_creator = fields.Text("Website Twitter Creator",
                                          translate=True)
    website_gplus_title = fields.Text("Website Google+ Title", translate=True)
    website_gplus_description = fields.Text("Website Google+ Description",
                                            translate=True)
    website_gplus_image = fields.Text("Website Goolge+ Image", translate=True)

    @api.onchange('website_og_title')
    def _on_change_title(self):
        if self.website_og_title:
            self.website_og_title = self.website_og_title
            self.website_twitter_title = self.website_og_title
            self.website_gplus_title = self.website_og_title

    @api.onchange('website_og_description')
    def _on_change_description(self):
        if self.website_og_description:
            self.website_og_description = self.website_og_description
            self.website_twitter_description = self.website_og_description
            self.website_gplus_description = self.website_og_description

    @api.onchange('website_image_url')
    def _on_change_image_url(self):
        if self.website_image_url:
            self.website_og_image = self.website_image_url
            self.website_twitter_image_src = self.website_image_url
            self.website_gplus_image = self.website_image_url


class View(models.Model):
    _name = "ir.ui.view"
    _inherit = ["ir.ui.view", "website.seo.metadata"]
