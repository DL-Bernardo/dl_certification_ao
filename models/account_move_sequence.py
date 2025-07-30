# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountMoveSequence(models.Model):
    _name = 'account.move.sequence'
    _description = 'Account Move Sequence'

    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
    ], string='Move Type', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)