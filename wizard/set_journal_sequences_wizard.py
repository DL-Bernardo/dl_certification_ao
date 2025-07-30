# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SetJournalSequencesWizard(models.TransientModel):
    _name = 'set.journal.sequences.wizard'
    _description = 'Wizard para configurar sequências dos diários'

    journal_id = fields.Many2one('account.journal', string='Diário', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequência Faturas')
    refund_sequence_id = fields.Many2one('ir.sequence', string='Sequência Reembolsos')

    def set_sequences(self):
        self.ensure_one()
        _logger.info("Setting sequences from the wizard.")

        sequence_model = self.env['account.move.sequence']
        company = self.env.company

        if self.sequence_id:
            # Faturas
            existing = sequence_model.search([
                ('journal_id', '=', self.journal_id.id),
                ('move_type', '=', 'out_invoice'),
                ('company_id', '=', company.id)
            ])
            if existing:
                existing.write({'sequence_id': self.sequence_id.id})
            else:
                sequence_model.create({
                    'journal_id': self.journal_id.id,
                    'move_type': 'out_invoice',
                    'sequence_id': self.sequence_id.id,
                    'company_id': company.id
                })

        if self.refund_sequence_id:
            # Reembolsos (notas de crédito)
            existing = sequence_model.search([
                ('journal_id', '=', self.journal_id.id),
                ('move_type', '=', 'out_refund'),
                ('company_id', '=', company.id)
            ])
            if existing:
                existing.write({'sequence_id': self.refund_sequence_id.id})
            else:
                sequence_model.create({
                    'journal_id': self.journal_id.id,
                    'move_type': 'out_refund',
                    'sequence_id': self.refund_sequence_id.id,
                    'company_id': company.id
                })