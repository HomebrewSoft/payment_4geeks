# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[
            ('4geeks', '4Geeks'),
        ],
    )
    p4geeks_client_id = fields.Char(
        string='Client ID',
        required_if_provider='4geeks',
        groups='base.group_user',
    )
    p4geeks_client_secret = fields.Char(
        string='Client Secret',
        required_if_provider='4geeks',
        groups='base.group_user',
    )
    p4geeks_entity_description = fields.Char(
        string='Entity Description',
        required_if_provider='4geeks',
        groups='base.group_user',
    )
