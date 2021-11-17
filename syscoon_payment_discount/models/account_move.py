# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_discount_date = fields.Date('Discount Date', compute='_compute_discount', compute_sudo=True, readonly=False)
    payment_discount_percent = fields.Float('Discount', compute='_compute_discount', compute_sudo=True, readonly=False)
    payment_discount_amount_total = fields.Monetary('Discounted Amount', compute='_compute_discount', currency_field='company_currency_id', compute_sudo=True, readonly=False)
    payment_discount_amount_total_currency = fields.Monetary(string='Discounted Amount in Currency', compute='_compute_discount', compute_sudo=True, readonly=False)
    payment_actual_payment_line = fields.Many2one('account.payment.term.line', compute='_compute_discount', store=True, compute_sudo=True, readonly=False)

    @api.depends('invoice_date_due', 'invoice_payment_term_id')
    def _compute_discount(self):
        for rec in self:
            rec.payment_actual_payment_line = False
            payment_lines = []
            for pl in rec.invoice_payment_term_id.line_ids:
                payment_date = fields.Date.from_string(rec.invoice_date or fields.date.today()) + relativedelta(days=pl.days + self.env.company.payment_discount_withhold)
                if payment_date >= fields.Date.today():
                    payment_lines.append({
                        'pl': pl.id,
                        'date': payment_date,
                    })
            if payment_lines:
                rec.payment_actual_payment_line = min(payment_lines, key=lambda x:x['date'])['pl']
            if rec.invoice_payment_state == 'not_paid':
                if rec.payment_actual_payment_line:
                    vals = rec.compute_payment_discount(rec.payment_actual_payment_line)
                    if vals:
                        rec.payment_discount_date = vals['payment_date']
                        rec.payment_discount_percent = vals['discount']
                        rec.payment_discount_amount_total = vals['total_discounted_amount']
                        rec.payment_discount_amount_total_currency = vals['total_discounted_amount_currency']
                    else:
                        rec.payment_discount_date = False
                        rec.payment_discount_percent = False
                        rec.payment_discount_amount_total = False
                        rec.payment_discount_amount_total_currency = False
                else:
                    rec.payment_discount_date = False
                    rec.payment_discount_percent = False
                    rec.payment_discount_amount_total = False
                    rec.payment_discount_amount_total_currency = False
            else:
                rec.payment_discount_date = False
                rec.payment_discount_percent = False
                rec.payment_discount_amount_total = False
                rec.payment_discount_amount_total_currency = False

    def compute_payment_discount(self, payment_line):
        vals = False
        payment_date = fields.Date.from_string(self.invoice_date or fields.date.today()) + relativedelta(days=payment_line.days + self.env.company.payment_discount_withhold)
        if payment_line.value == 'percent':
            total_discount_amount = total_discount_amount_currency = 0.0
            for line in self.line_ids.filtered(lambda l: l.amount_residual != False):
                if line.payment_discount_amount:
                    total_discount_amount += line.payment_discount_amount
                if line.payment_disocunt_amount_currency:
                    if self.type in ['out_invoice', 'out_refund']:
                        total_discount_amount_currency -= line.payment_disocunt_amount_currency
                    elif self.type in ['in_invoice', 'in_refund']:
                        total_discount_amount_currency += line.payment_disocunt_amount_currency or total_discount_amount
            total_discounted_amount = self.amount_residual_signed - total_discount_amount
            total_discounted_amount_currency = self.amount_residual + total_discount_amount_currency
            vals = {
                'payment_date': payment_date,
                'discount': payment_line.value_amount,
                'total_discounted_amount': total_discounted_amount,
                'total_discounted_amount_currency': total_discounted_amount_currency,
            }
        return vals


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_discount_amount = fields.Monetary('Discount Amount', compute='_compute_discount', currency_field='company_currency_id', compute_sudo=True, store=True)
    payment_disocunt_amount_currency = fields.Monetary(string='Discount Amount in Currency', compute='_compute_discount', compute_sudo=True, store=True)

    @api.depends('move_id.invoice_date_due', 'move_id.invoice_payment_term_id', 'move_id.payment_actual_payment_line', 'move_id.state')
    def _compute_discount(self):
        for line in self.filtered(lambda l: l.amount_residual >= 0):
            vals = {
                'discount_amount': 0.0,
                'discount_amount_currency': 0.0,
            }
            if line.move_id.invoice_payment_state == 'not_paid' and line.amount_residual != 0:
                computed_vals = line.compute_payment_discount(line.move_id.payment_actual_payment_line)
                if computed_vals:
                    vals = computed_vals
            line.payment_discount_amount = vals['discount_amount']
            line.payment_disocunt_amount_currency = vals['discount_amount_currency']
        
    def compute_payment_discount(self, payment_line):
        vals = False
        if payment_line.value == 'percent':
            discount_amount = self.move_id.currency_id.round(self.amount_residual * payment_line.value_amount / 100)
            discount_amount_currency = self.move_id.currency_id.round(self.amount_residual_currency * payment_line.value_amount / 100)
            if not discount_amount_currency:
                discount_amount_currency = discount_amount
            vals = {
                'discount_amount': discount_amount,
                'discount_amount_currency': discount_amount_currency,
            }
        return vals

