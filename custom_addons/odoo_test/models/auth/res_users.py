# -*- coding: utf-8 -*-

import pytz

from odoo import SUPERUSER_ID
from odoo import fields, api
from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    sid = fields.Char('Session ID')
    logged_in = fields.Boolean('Logged In')

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        if not password:
            raise AccessDenied()
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth():
                    user = self.search(self._get_login_domain(
                        login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get(
                        'tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        user.tz = tz
                    if user.sid and user.logged_in:
                        request.uid = user.id
                        raise AccessDenied("already_logged_in")
                    user._save_session()
                    user._update_last_login()
        except AccessDenied:
            raise
        return user.id

    def _clear_session(self):
        self.write({'sid': False, 'logged_in': False})

    def _save_session(self):
        sid = request.httprequest.session.sid
        self.with_user(SUPERUSER_ID).write({'sid': sid,
                                            'logged_in': True})
