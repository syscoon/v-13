# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class syscoonPaymentDiscountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_discount_withhold = fields.Integer(related='company_id.payment_discount_withhold', readonly=False)
    payment_discount_default_income_account_id = fields.Many2one(
        related='company_id.payment_discount_default_income_account_id', readonly=False)
    payment_discount_default_expense_account_id = fields.Many2one(
        related='company_id.payment_discount_default_expense_account_id', readonly=False)