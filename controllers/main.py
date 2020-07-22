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
        values = {
            'status': False,
            'message': '',
            'redirect_brt': False,
        }
        try:
            PaymentAcquirer = request.env['payment.acquirer']
            acquirer_id = PaymentAcquirer.sudo().browse(request.website.get_4geeks_payment_acquirer_id())
            print(acquirer_id)
        except:
            raise  # TODO
        return values

    @http.route('/payment/4geeks', type='http', auth="public", website=True)
    def cardconnect_payment(self, **post):
        """ 4geeks Payment Controller """
        _logger.info('Beginning 4geeks with post data %s', pprint.pformat(post))
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
