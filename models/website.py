# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_4geeks_payment_acquirer_id(self):
        IrModelData = self.env['ir.model.data']
        acquirer_id = IrModelData.sudo().get_object_reference('payment_4geeks', 'payment_acquirer_4geeks')[1]
        return acquirer_id or 0
