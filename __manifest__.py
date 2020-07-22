# -*- coding: utf-8 -*-
{
    'name': 'Payment 4Geeks',
    'version': '0.1.0',
    'author': 'HomebrewSoft',
    'website': 'https://gitlab.com/HomebrewSoft/{project}/payment_4geeks',
    'depends': [
        'payment',
        'payment_cardconnect_cr',
    ],
    'data': [
        # security
        # data
        'data/payment_acquirer.xml',
        # reports
        # views
        'templates/assets.xml',
        'templates/modal.xml',
    ],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
