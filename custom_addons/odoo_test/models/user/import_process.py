# -*- coding: utf-8 -*-

from odoo import models, fields


class ImporttProcess(models.Model):

    _name = 'kams.import.process'
    _description = 'Import Process'
    _rec_name = 'filename'
    _order = "id desc"

    file = fields.Binary('File')
    filename = fields.Char('Filename')
    user_id = fields.Many2one("res.users", "Imported by")
    cron_id = fields.Many2one('ir.cron', "Background Process")
    status = fields.Selection([('process', 'In Progress'),
                               ('imported', 'Imported'), ('failed', 'Failed')],
                              default='process')
    log_ids = fields.One2many(
        'kams.import.process.detail', 'process_id', string='Logs')

    log_count = fields.Integer("Log count", compute="_compute_log_count")

    def action_show_logs(self):
        return {
            "name": "Logs",
            "view_mode": "tree",
            "res_model": "kams.import.process.detail",
            "type": "ir.actions.act_window",
            "domain": [["process_id", "=", self.id]],
        }

    def _compute_log_count(self):
        self._cr.execute(
            "SELECT COUNT(*) FROM kams_import_process_detail WHERE process_id=(%s);", [
                str(self.id)]
        )
        self.log_count = self._cr.dictfetchone()["count"]


class ImporttProcessDetail(models.Model):

    _name = 'kams.import.process.detail'
    _description = 'Import Process Detail'

    name = fields.Text('Log')
    process_id = fields.Many2one('kams.import.process', string='Process')
