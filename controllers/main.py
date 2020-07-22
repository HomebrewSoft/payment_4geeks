# -*- coding: utf-8 -*-
import logging
import pprint
from datetime import datetime

import werkzeug
from odoo import http
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

Error1 = _(
    "Cardconnect Errors 1: cardconnect Payment Gateway Currently not Configure for this Currency pls Connect Your Shop Provider !!!")
Error2 = _("Cardconnect Errors 2: Authentication Error: API keys are incorrect.")
Error3 = _("Cardconnect Errors 3: Authorization Error: not authorized to perform the attempted action.")
Error4 = _("Cardconnect Errors 4: Issue occure while generating clinet token, pls contact your shop provider.")
Error5 = _("Cardconnect Errors 5: Default 'Merchant Account ID' not found.")
Error6 = _("Cardconnect Errors 6: Transaction not Found.")
Error7 = _("Cardconnect Errors 7: Error occured while payment processing or Some required data missing.")
Error8 = _("Cardconnect Errors 8: Validation error occured. Please contact your administrator.")
Error9 = _(
    "Cardconnect Errors 9: Payment has been recevied on cardconnect end but some error occured during processing the order.")
Error10 = _("Cardconnect Errors 10: Unknow Error occured. Unable to validate the cardconnect payment.")
SuccessMsg = _("Payment Successfully recieved and submitted for settlement.")


class P4GeeksController(http.Controller):
    def p4geeks_do_payment(self, **post):
        order, reference, tx = request.website.sale_get_order(), post.get('reference'), None
        values = {
            'status': False,
            'message': '',
            'redirect_brt': False,
        }
        try:
            PaymentAcquirer = request.env['payment.acquirer']
            acquirere_id = \
                request.env['ir.model.data'].get_object_reference('payment_cardconnect_cr', 'payment_acquirer_cconnect')[1]

            acquirer_credential = PaymentAcquirer.sudo().browse(acquirere_id)

            # environment = acquirer_credential.environment
            merchant_id = acquirer_credential.cconnect_merchant_account
            cconnect_url = acquirer_credential.cconnect_url
            cconnect_user = acquirer_credential.cconnect_user
            cconnect_pwd = acquirer_credential.cconnect_pwd
            customer_obj = order.partner_id
            if reference:
                tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
            if tx:
                result = {  # TODO
                    'respstat': 'A',
                    'amount': '750',
                    'token': 'supertoken',
                }
                if result.get('respstat') == "A":
                    values.update({
                        'status': True if result.get('respstat') == "A" else False,
                        'reference': reference,
                        'currency': post.get('currency'),
                        'amount': result.get('amount'),
                        'acquirer_reference': result.get('token'),
                        'partner_reference': post,
                        'tx_msg': SuccessMsg
                    })
                    _logger.info('Cardconnect form_feedback with values %s', pprint.pformat(values))  # debug
                    res = request.env['payment.transaction'].sudo().form_feedback(values, 'cardconnect')
                    if not res:
                        tx.sudo()._set_transaction_error(Error8)
                        values.update({
                            'status': False,
                            'redirect_brt': False,
                            'message': Error8,
                        })
                else:
                    values.update({
                        'status': False,
                        'reference': reference,
                        'currency': post.get('currency'),
                        'amount': result.get('amount'),
                        'acquirer_reference': result.get('token'),
                        'partner_reference': post,
                        'tx_msg': "Payment Failed"
                    })
                    _logger.info('Cardconnect form_feedback with values %s', pprint.pformat(values))  # debug
                    res = request.env['payment.transaction'].sudo().form_feedback(values, 'cardconnect')
                    if not res:
                        tx.sudo()._set_transaction_error(Error8)
                        values.update({
                            'status': False,
                            'redirect_brt': False,
                            'message': Error8,
                        })
            elif not tx:
                values.update({'status': False, 'redirect_brt': True, 'message': Error6})
            else:
                # more condition can we added
                values.update({'status': False, 'redirect_brt': True, 'message': Error7})
        except Exception as e:
            _logger.error(
                "************Cardconnect exception occured ******************** \n 'cardconnect_payment' ------- exception=%r",
                e)  # debug
            if reference:
                tx = request.env['payment.transaction'].search([('reference', '=', reference)])

            if tx and values['status']:
                tx.sudo().write({
                    'cct_txnid': values['acquirer_reference'],
                    'acquirer_reference': values['acquirer_reference'],
                    'state': 'error',
                    'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'state_message': Error9,
                })
                values.update({'status': False, 'redirect_brt': True, 'message': Error9})
            elif tx and not values['status']:
                tx.sudo()._set_transaction_error(Error1)
                values.update({'status': False, 'redirect_brt': True, 'message': e or Error1})
            elif not tx:
                values.update({'status': False, 'redirect_brt': True, 'message': Error6})
            else:
                values.update({'status': False, 'redirect_brt': True, 'message': Error10})
        return values

    @http.route('/payment/4geeks', type='http', auth="public", website=True)
    def cardconnect_payment(self, **post):
        """ 4geeks Payment Controller """
        _logger.info('Beginning 4geeks with post data %s', pprint.pformat(post))  # debug
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
            'p4geeks-acquirer-id': acquirer_id,
        }
        return request.env['ir.ui.view'].render_template("payment_4geeks.4geeks_template_modal", values)
