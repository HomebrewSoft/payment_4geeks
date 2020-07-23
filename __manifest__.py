# -*- coding: utf-8 -*-
{
    'name': 'Payment 4Geeks',
    'version': '0.1.0',
    'author': 'HomebrewSoft',
    'website': 'https://gitlab.com/HomebrewSoft/misc/payment_4geeks',
    'depends': [
        'payment',
        'website',
    ],
    'data': [
        # security
        # templates
        'templates/assets.xml',
        'templates/checkout_s2s_form.xml',
        'templates/form.xml',
        'templates/modal.xml',
        # data
        'data/payment_acquirer.xml',
        # reports
        # views
        'views/payment_acquirer.xml',
    ],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
    'external_dependencies': {
        'python': [
            'gpayments',
        ],
    },
}
