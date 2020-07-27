# -*- coding: utf-8 -*-
import logging
import pprint
from datetime import datetime, timedelta

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
    'Succeeded': _('Payment Successfully received and submitted.'),
    'TransactionNotFoundError': _('Transaction not found.'),
    'InternalError': _('There is an internal error, please contact the administrator.'),
    'ValidationError': _('We can not confirm your payment, please contact the administrator.'),
    'PaymentError': _('There was an error in your payment; if you think is a mistake ,please contact the administrator.'),
}


class P4GeeksController(http.Controller):
    token_expiration = None

    def authenticate(self, client_id, client_secret):
        now = datetime.now()
        if not self.token_expiration or self.token_expiration <= now:
            gpayments.client_id = client_id
            gpayments.client_secret = client_secret
            auth = gpayments.auth()
            self.token_expiration = now + timedelta(seconds=auth.data['expires_in'])

    def p4geeks_do_payment(self, **post):
        reference = post.get('reference')
        tx = None
        values = {
            'status': False,
            'message': '',
            'redirect_brt': False,
        }

        PaymentAcquirer = request.env['payment.acquirer']
        acquirer_id = PaymentAcquirer.sudo().browse(request.website.get_4geeks_payment_acquirer_id())

        if reference:
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])

        if not tx:
            values.update({'status': False, 'message': messages['TransactionNotFoundError']})
            return values

        try:
            self.authenticate(acquirer_id.p4geeks_client_id, acquirer_id.p4geeks_client_secret)
            _logger.debug('Authenticated')
        except (AttributeError, gpayments.oauth_error.InvalidClientError) as e:
            _logger.error('Can not authenticate %s', e)
            values.update({'status': False, 'message': messages['InternalError']})
            tx.sudo()._set_transaction_error(messages['InternalError'])
            return values

        exp_month, exp_year = post.get('cardExpiry').split('/')
        exp_year = '20' + exp_year

        try:
            result = gpayments.SimpleCharge.create(
                amount=post.get('amount'),
                description=reference,
                entity_description=acquirer_id.p4geeks_entity_description,
                currency=post.get('currency'),
                credit_card_number=post.get('cardnumber'),
                credit_card_security_code_number=post.get('cardCVC'),
                exp_month=exp_month,
                exp_year=exp_year,
            )
            _logger.debug('Payment processed in API: %s', pprint.pformat(result))
        except gpayments.error.InvalidRequestError as e:
            _logger.debug('PaymentError: %s', e)
            tx.sudo()._set_transaction_error(messages['PaymentError'])
            values.update({'status': False, 'message': messages['PaymentError']})
            return values

        charge_log = result.get('charge_log')
        if charge_log['status'] == 'succeeded':
            values.update({
                'status': True,
                'reference': reference,
                'currency': charge_log['currency'].upper(),
                'amount': charge_log['amount'],
                'acquirer_reference': result.get('charge_id'),
                'partner_reference': post,
                'tx_msg': messages['Succeeded'],
            })

            _logger.debug('Processing form_feedback with values %s', pprint.pformat(values))
            res = request.env['payment.transaction'].sudo().form_feedback(values, '4geeks')
            if not res:
                tx.sudo()._set_transaction_error(messages['ValidationError'])
                values.update({
                    'status': False,
                    'message': messages['ValidationError'],
                })
        else:
            values.update({
                'status': False,
                'reference': reference,
                'currency': post.get('currency'),
                'amount': result.get('amount'),
                'acquirer_reference': result.get('charge_id'),
                'partner_reference': post,
                'tx_msg': messages['PaymentError'],
            })

            res = request.env['payment.transaction'].sudo().form_feedback(values, '4geeks')
            if not res:
                tx.sudo()._set_transaction_error(messages['ValidationError'])
                values.update({
                    'message': messages['ValidationError'],
                })
        return values

    @http.route('/payment/4geeks', type='http', auth="public", website=True)
    def p4geeks_payment(self, **post):
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
