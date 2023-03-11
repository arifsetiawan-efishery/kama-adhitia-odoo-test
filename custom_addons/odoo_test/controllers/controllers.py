# -*- coding: utf-8 -*-
# from odoo import http


# class OdooTest(http.Controller):
#     @http.route('/odoo_test/odoo_test/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_test/odoo_test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_test.listing', {
#             'root': '/odoo_test/odoo_test',
#             'objects': http.request.env['odoo_test.odoo_test'].search([]),
#         })

#     @http.route('/odoo_test/odoo_test/objects/<model("odoo_test.odoo_test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_test.object', {
#             'object': obj
#         })
