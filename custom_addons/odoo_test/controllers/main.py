# -*- coding: utf-8 -*-
import odoo
import odoo.modules.registry
from odoo import http, SUPERUSER_ID
from odoo.http import Controller, Response, request, route
from odoo.service import security
from odoo.tools.translate import _
from odoo.addons.web.controllers import main

import os

import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.local
import werkzeug.wrappers
import werkzeug.wsgi

import jwt
import json

from pyrate_limiter import (Duration, RequestRate,
                            Limiter, BucketFullException)

rate = RequestRate(1, Duration.SECOND * 10)
limiter = Limiter(rate)


def clear_session_history(u_sid, f_uid=False):
    path = odoo.tools.config.session_dir
    store = werkzeug.contrib.sessions.FilesystemSessionStore(
        path, session_class=odoo.http.OpenERPSession, renew_missing=True)
    session_fname = store.get_session_filename(u_sid)
    try:
        os.remove(session_fname)
        return True
    except OSError:
        pass
    return False


def token_validation(token):

    secret_key = request.env['kams.auth.config'].sudo().search(
        [], limit=1).secret_key

    try:
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
        role = data.get('role')
        email = data.get('email', 'anonym')
        return role, email
    except:
        raise ValueError('Token is invalid')


class Session(main.Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        user = request.env['res.users'].with_user(SUPERUSER_ID).search(
            [('id', '=', request.session.uid)])
        user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/clear_all_sessions', type='http', auth="none")
    def logout_all(self, redirect='/web/login', f_uid=False):
        if f_uid:
            user = request.env['res.users'].with_user(
                SUPERUSER_ID).browse(int(f_uid))
            if user:
                session_cleared = clear_session_history(user.sid, f_uid)
                if session_cleared:
                    user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)


class Home(main.Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db,
                                                   request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(
                    self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                failed_uid = request.uid
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                elif e.args[0] == "already_logged_in":
                    values['error'] = "User already logged in. Log out from " \
                                      "other devices and try again."
                    values['logout_all'] = True
                    values[
                        'failed_uid'] = failed_uid if failed_uid != SUPERUSER_ID else False
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get(
                    'error') == 'access':
                values['error'] = _('Only employee can access this database. '
                                    'Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class RootExt(odoo.http.Root):

    def get_response(self, httprequest, result, explicit_session):
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except Exception as e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise

        if isinstance(result, (bytes, str)):
            response = Response(result, mimetype='text/html')
        else:
            response = result

        save_session = (not request.endpoint) or request.endpoint.routing.get(
            'save_session', True)
        if not save_session:
            return response

        if httprequest.session.should_save:
            if httprequest.session.rotate:
                self.session_store.delete(httprequest.session)
                httprequest.session.sid = self.session_store.generate_key()
                if httprequest.session.uid:
                    httprequest.session.session_token = security.compute_session_token(
                        httprequest.session, request.env)
                httprequest.session.modified = True
            self.session_store.save(httprequest.session)
        if not explicit_session and hasattr(response, 'set_cookie'):
            response.set_cookie(
                'session_id', httprequest.session.sid, httponly=True)

        return response


root = RootExt()
odoo.http.Root.get_response = root.get_response


class OdooTest(Controller):
    @route(
        "/api/login", type="json", auth="none", csrf=False, cors="*", methods=["POST"],
    )
    def login(self, db, login, password, base_location=None):

        try:
            request.session.authenticate(db, login, password)
            session = request.env['ir.http'].session_info()
            config = request.env['kams.auth.config'].sudo().search(
                [], limit=1)
            token = jwt.encode({
                "name": session.get('name'),
                "email": session.get('email'),
                "role": "admin" if session.get('is_admin') else "user"
            }, config.secret_key, algorithm="HS256")
            data = {
                'status': 200,
                'message': 'success',
                'response': {
                    'auth_type': 'Bearer',
                    'token': token
                }
            }
            return data
        except odoo.exceptions.AccessDenied as e:
            if e.args == odoo.exceptions.AccessDenied().args:
                return {
                    'status': 400,
                    'message': 'Database name, username or password is wrong',
                }
            elif e.args[0] == "already_logged_in":
                Response.status = '403'
                return {
                    'status': 403,
                    'message': 'This user has logged in using another device',
                }

    @route(
        "/api/fetch", type="http", auth="none", csrf=False, cors="*", methods=["GET"],
    )
    def fetch(self):
        try:
            PREFIX = 'Bearer '
            headers = request.httprequest.headers
            bearer = headers.get('Authorization')
            if not bearer.startswith(PREFIX):
                raise ValueError('Invalid token type')

            role, email = token_validation(bearer[len(PREFIX):])

            if role == 'user':
                limiter.try_acquire(email)
            data = []
            get_data = request.env['kams.cache.data'].sudo().search([])
            for line in get_data:
                data.append(eval(line.name))
            return Response(
                status=200,
                content_type='application/json; charset=utf-8',
                response=json.dumps({
                    'result':
                    {
                        'status': 200,
                        'message': 'Success',
                        "response": data
                    }
                }))

        except BucketFullException:
            return Response(
                status=400,
                content_type='application/json; charset=utf-8',
                response=json.dumps({
                    'result':
                    {
                        'status': 400,
                        'message': "Too many request",
                    }
                }))

        except Exception as e:
            return Response(
                status=403,
                content_type='application/json; charset=utf-8',
                response=json.dumps({
                    'result':
                    {
                        'status': 403,
                        'message': str(e),
                    }
                }))
