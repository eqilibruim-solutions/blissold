# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import models


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'website.seo.metadata']


class BlogBlog(models.Model):
    _name = 'blog.blog'
    _inherit = ['blog.blog', 'website.seo.metadata']
