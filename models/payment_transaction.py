# -*- coding: utf-8 -*-
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _4geeks_form_get_tx_from_data(self, data):
        reference = data.get('reference', None)
        amount = data.get('amount', None)
        currency = data.get('currency', None)
        acquirer_reference = data.get('acquirer_reference', None)

        try:
            assert reference is not None, 'Missing `reference`'
            assert amount is not None, 'Missing `amount`'
            assert currency is not None, 'Missing `currency`'
            assert acquirer_reference is not None, 'Missing `acquirer_reference`'
        except AssertionError as e:
            raise ValidationError(e)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('Received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            raise ValidationError(error_msg)
        return tx

    def _4geeks_form_validate(self, data):
        status = data.get('status')
        res = {
            'cct_txnid': data.get('acquirer_reference'),
            'acquirer_reference': data.get('acquirer_reference'),
            'state_message': data.get('tx_msg'),
            'cct_txcurrency': data.get('currency'),
        }
        if status:
            self._set_transaction_done()
            return self.write(res)
