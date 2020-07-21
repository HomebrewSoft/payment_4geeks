# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
