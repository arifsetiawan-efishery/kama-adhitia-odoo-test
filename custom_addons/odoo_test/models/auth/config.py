# -*- coding: utf-8 -*-

from odoo import models, fields


class AuthConfig(models.Model):

    _name = 'kams.auth.config'
    _description = "Token Configuration"
    _order = "id desc"

    name = fields.Char('Name')
    secret_key = fields.Char('Secret Key')
