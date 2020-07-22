# -*- coding: utf-8 -*-
{
    'name': 'Payment 4Geeks',
    'version': '0.1.0',
    'author': 'HomebrewSoft',
    'website': 'https://gitlab.com/HomebrewSoft/{project}/payment_4geeks',
    'depends': [
        'payment',
    ],
    'data': [
        # security
        # data
        'data/payment_acquirer.xml',
        # reports
        # templates
        'templates/assets.xml',
        'templates/modal.xml',
        # views
        'views/payment_acquirer.xml',
    ],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
    'external_dependencies': {
        'python': ['gpayments'],
    },
}
