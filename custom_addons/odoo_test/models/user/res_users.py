# -*- coding: utf-8 -*-

from odoo import models, _
import base64
import tempfile
import csv
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import os
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def import_data(self, process_id=False):
        if process_id:
            process = self.env[
                'kams.import.process'].browse(process_id)
            total_success_import_record = 0
            total_failed_record = 0
            list_of_failed_record = ''
            file_name = str(process.filename)
            try:
                if not process.file or not file_name.lower().endswith(('.csv')):
                    list_of_failed_record += "Please Select an .csv or its compatible file to Import." + os.linesep
                    _logger.error(
                        "Please Select an .csv or its compatible file to Import.")
                file_path = tempfile.gettempdir() + '/import.csv'
                f = open(file_path, 'wb+')
                f.write(base64.decodestring(process.file))
                f.close()

                state = False
                detail = ""
                dict = csv.DictReader(open(file_path))
                dict_line = [line for line in dict]
                for count, line in enumerate(dict_line, start=1):
                    try:
                        self.env['res.users'].create({
                            'name': line.get('name'),
                            'login': line.get('email'),
                            'password': line.get('password'),
                        })
                        state = True
                        total_success_import_record += 1
                    except Exception as e:
                        total_failed_record += 1
                        detail = str(e)
                        list_of_failed_record += str(line) + \
                            ': ' + detail + os.linesep
                        _logger.error("Error at %s" % str(line))
                        self._cr.rollback()

                    finally:
                        self.env['kams.import.process.detail'].create({
                            'name': f"{count}. {'Success' if state else 'Failed'} Created User {line.get('name')} {(': '+ detail) if not state else ''}",
                            'process_id': process_id,
                        })
                        self._cr.commit()

            except Exception as e:
                list_of_failed_record += str(e)

            try:
                file_data = base64.b64encode(
                    list_of_failed_record.encode('utf-8'))
                process.status = 'imported'

                datetime_object = datetime.strptime(
                    str(process.create_date), '%Y-%m-%d %H:%M:%S.%f')

                start_date = datetime.strftime(
                    datetime_object, DEFAULT_SERVER_DATETIME_FORMAT)
                self._cr.commit()
                now_time = datetime.now()
                user_tz = self.env.user.tz or str(pytz.utc)
                local = pytz.timezone(user_tz)
                start_date_in_user_tz = datetime.strftime(pytz.utc.localize(
                    datetime.strptime(str(start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                    local), DEFAULT_SERVER_DATETIME_FORMAT)
                end_date_in_user_tz = datetime.strftime(pytz.utc.localize(
                    now_time).astimezone(local),
                    DEFAULT_SERVER_DATETIME_FORMAT)

                self.env['kams.import.history'].create({
                    'total_success_count': total_success_import_record,
                    'total_failed_count': total_failed_record,
                    'file': file_data,
                    'file_name': f'logs_background_process_{datetime.strftime(pytz.utc.localize(now_time).astimezone(local),"%m-%d-%Y")}.txt',
                    'import_file_name': process.filename,
                    'start_date': start_date_in_user_tz,
                    'end_date': end_date_in_user_tz,
                })

                message = "Import process is completed. Check in Imported History if all the users have" \
                    " been imported correctly. </br></br> Imported File: %s </br>" \
                    "Imported by: %s" % (
                        process.filename, process.user_id.name)
                self.env.user.notify_success(
                    message=message, title='Process Done', sticky=True)
                self._cr.commit()

            except Exception as e:
                process.status = 'failed'
                _logger.error(e)
                self.env.user.notify_warning(
                    message=str(e), title='Process Failed', sticky=True)
                self._cr.commit()

    def remove_finish_import_crons(self):
        process = self.env['kams.import.process'].search(
            ['|', ('status', '=', 'imported'), ('status', '=', 'failed')])
        for list_process in process:
            if list_process.cron_id:
                list_process.cron_id.unlink()
