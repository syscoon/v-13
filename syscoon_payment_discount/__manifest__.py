# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'syscoon Payment Discount',
    'version': '13.0.0.0.2',
    'depends': ['account'],
    'author': 'syscoon GmbH',
    'license': 'OPL-1',
    'website': 'https://syscoon.com',
    'summary': 'Module that allows to have discount directy at payment of supplier invoices',
    'description': """""",
    'category': 'Accounting',
    'data': [
        'views/account_move.xml',
        'views/account_payment_term.xml',
        'views/account_tax.xml',
        'views/res_config_settings.xml',
        'views/account_payment_views.xml',
    ],
    'active': False,
    'installable': True
}
