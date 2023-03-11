# -*- coding: utf-8 -*-

from odoo import models, fields


class ImporttHistory(models.Model):

    _name = 'kams.import.history'
    _description = "Import History"
    _rec_name = 'file_name'
    _order = "id desc"

    file = fields.Binary('File')
    file_name = fields.Char('File Name')
    import_file_name = fields.Char('Imported File Name')
    start_date = fields.Char('Import Start At')
    end_date = fields.Char('Import End At')

    total_success_count = fields.Integer('Success')
    total_failed_count = fields.Integer('Failed')
