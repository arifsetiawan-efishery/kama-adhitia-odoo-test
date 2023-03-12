# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    sid = fields.Char('API id')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if res:
            if self.sid:
                invoice = super(SaleOrder, self)._create_invoices(final=True)
                invoice.action_post()
                context = self._context.copy()
                context['active_model'] = 'account.move'
                context['active_ids'] = invoice.ids
                wizard = self.env['account.payment.register'].sudo(
                ).with_context(context).create({})
                wizard.sudo()._create_payments()
        return True
