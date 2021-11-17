# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
from dateutil.relativedelta import relativedelta


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    use_with_discount = fields.Boolean('Use With Payment Discount', 
        help='If checkd, the Odoo standard for splitting the invoice amount will be desabled.')

    def compute(self, value, date_ref=False, currency=None):
        result = super(AccountPaymentTerm, self).compute(value, date_ref=False, currency=None)
        if self.use_with_discount:
            date_ref = date_ref or fields.Date.context_today(self)
            amount = value
            result = []
            if not currency and self.env.context.get('currency_id'):
                currency = self.env['res.currency'].browse(self.env.context['currency_id'])
            elif not currency:
                currency = self.env.company.currency_id
            for line in self.line_ids:
                if line.value == 'balance':
                    amt = currency.round(amount)
                    next_date = fields.Date.from_string(date_ref)
                    if line.option == 'day_after_invoice_date':
                        next_date += relativedelta(days=line.days)
                        if line.day_of_the_month > 0:
                            months_delta = (line.day_of_the_month < next_date.day) and 1 or 0
                            next_date += relativedelta(day=line.day_of_the_month, months=months_delta)
                    elif line.option == 'after_invoice_month':
                        next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                        next_date = next_first_date + relativedelta(days=line.days - 1)
                    elif line.option == 'day_following_month':
                        next_date += relativedelta(day=line.days, months=1)
                    elif line.option == 'day_current_month':
                        next_date += relativedelta(day=line.days, months=0)
                    result.append((fields.Date.to_string(next_date), amt))
        return result
            