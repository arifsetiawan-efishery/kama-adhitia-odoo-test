# -*- coding: utf-8 -*-

from odoo import models, fields, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class ImportUsers(models.TransientModel):

    _name = 'kams.import.users'
    _description = "Import Users"

    name = fields.Char('File name')
    file = fields.Binary('File')

    def import_data(self):
        self.ensure_one()

        now_time = datetime.now() + timedelta(seconds=5)
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        user_time_zone = datetime.strftime(pytz.utc.localize(
            datetime.strptime(datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S'),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),
            DEFAULT_SERVER_DATETIME_FORMAT)

        cron_obj = self.env['ir.cron']
        process = self.env['kams.import.process'].create({
            'file': self.file,
            'filename': user_time_zone + ' - ' + self.name,
            'user_id': self._uid,
            'status': 'process',
        })

        model_id = self.env['ir.model'].search(
            [('model', '=', 'res.users')])
        cron_data = {
            'name': "Import Users" + ' - ' + user_time_zone,
            'code': 'model.import_data(%s)' % process.id,
            'nextcall': now_time,
            'numbercall': -1,
            'user_id': self._uid,
            'model_id': model_id.id,
            'state': 'code',
        }

        cron = cron_obj.sudo().create(cron_data)
        process.cron_id = cron.id
        self.env.user.notify_success(
            message='The import process is started on background, You will be notify shortly once the import process will be finished.', title='Background Import Success', sticky=False)
