# -*- coding: utf-8 -*-
import logging
import pprint
from datetime import datetime

try:
    import gpayments
except ImportError:
    pass

import werkzeug
from odoo import http
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

messages = {
    'Succeeded': _('Payment Successfully received and submitted'),
}


class P4GeeksController(http.Controller):
    def p4geeks_do_payment(self, **post):
        values = {
            'status': False,
            'message': '',
            'redirect_brt': False,
        }
        PaymentAcquirer = request.env['payment.acquirer']
        acquirer_id = PaymentAcquirer.sudo().browse(request.website.get_4geeks_payment_acquirer_id())
        try:
            gpayments.client_id = acquirer_id.p4geeks_client_id
            gpayments.client_secret = acquirer_id.p4geeks_client_secret
            gpayments.auth()  # TODO review expiration
        except:
            pass  # TODO
        exp_month, exp_year = post.get('cardExpiry').split('/')
        exp_year = '20' + exp_year
        try:
            result = gpayments.SimpleCharge.create(
                amount=post.get('amount'),
                description=post.get('reference'),
                entity_description=acquirer_id.p4geeks_entity_description,
                currency=post.get('currency'),
                credit_card_number=post.get('cardnumber'),
                credit_card_security_code_number=post.get('cardCVC'),
                exp_month=exp_month,
                exp_year=exp_year,
            )
            charge_log = result.get('charge_log')
            if charge_log['status'] == 'succeeded':
                values.update({
                    'status': True,
                    'reference': post.get('reference'),
                    'currency': charge_log['currency'],
                    'amount': charge_log['amount'],
                    'acquirer_reference': result.get('charge_id'),
                    'partner_reference': post,
                    'tx_msg': messages['Succeeded'],
                })
        except:
            raise  # TODO
        return values

    @http.route('/payment/4geeks', type='http', auth="public", website=True)
    def cardconnect_payment(self, **post):
        """ 4geeks Payment Controller """
        result = self.p4geeks_do_payment(**post)

        if not result['status']:
            _logger.error(result['message'])
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/p4geeks/modal'], type='json', auth="public", methods=['POST'], website=True)
    def p4geeks_modal(self):
        order = request.website.sale_get_order()
        acquirer_id = request.website.get_4geeks_payment_acquirer_id()
        values = {
            'return_url': '/shop/payment/validate',
            'reference': '/',
            'amount': order.amount_total,
            'currency': order.currency_id,
            '4geeks-acquirer-id': acquirer_id,
        }
        return request.env['ir.ui.view'].render_template("payment_4geeks.4geeks_template_modal", values)
