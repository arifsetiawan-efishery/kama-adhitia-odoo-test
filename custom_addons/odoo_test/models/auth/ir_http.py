
from odoo import models, http, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls
import werkzeug.utils


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        if request.env.user.email:
            result['email'] = request.env.user.email
        return result

    @classmethod
    def _authenticate(cls, auth_method='user'):
        try:
            if request.session.uid:
                uid = request.session.uid
                user_pool = request.env['res.users'].with_user(
                    SUPERUSER_ID).browse(uid)

                def _update_user(u_sid, u_uid):
                    if u_uid and u_sid:
                        query = """update res_users set sid = '%s',
                                       logged_in = 'TRUE' where id = %s
                                       """ % (u_sid, u_uid)
                        request.env.cr.execute(query)

                sid = request.session.sid
                request_params = request.params.copy()
                if 'options' in request_params and 'bus_inactivity' in \
                        request_params['options']:
                    if uid and user_pool.sid and sid != user_pool.sid:
                        _update_user(sid, uid)
                else:
                    if not user_pool.sid and \
                            not user_pool.logged_in:
                        _update_user(sid, uid)
        except Exception:
            pass

        try:
            if request.session.uid:
                try:
                    request.session.check_security()
                except (AccessDenied, http.SessionExpiredException):
                    request.session.logout(keep_db=True)
            if request.uid is None:
                method = "_auth_method_%s" % auth_method.routing['auth']
                getattr(cls, method)()
        except (AccessDenied, http.SessionExpiredException,
                werkzeug.exceptions.HTTPException):
            raise
        except Exception:
            raise AccessDenied()
        return auth_method
