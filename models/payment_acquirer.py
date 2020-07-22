# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[
            ('4geeks', '4Geeks'),
        ],
    )
