# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    payment_discount_withhold = fields.Integer('Payment Discount Withhold')
    payment_discount_default_income_account_id = fields.Many2one('account.account', 
        string='Default Income Discount Account')
    payment_discount_default_expense_account_id = fields.Many2one('account.account', 
        string='Default Expense Discount Account')
