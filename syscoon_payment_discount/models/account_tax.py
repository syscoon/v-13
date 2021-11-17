# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    syscoon_payment_discount_account = fields.Many2one('account.account', string='Payment Discount Account')