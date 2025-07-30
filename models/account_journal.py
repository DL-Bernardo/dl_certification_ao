# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

prefixo_journal_type = {'cash': 'CSH', 'bank': 'BNK', 'sale': 'VD', 'purchase': 'CP', 'general': 'DIV'}


class AccountJournal(models.Model):
    _inherit = "account.journal"

    self_billing = fields.Boolean(string="Auto-Facturação",
                                  help="Assinale, se este diário se destina a registar Auto-facturação. As facturas "
                                       "emitidas em substituição dos fornecedores, ao abrigo de acordos de "
                                       "auto-facturação, são assinaladas como tal no SAFT",
                                  copy=False)
    transaction_type = fields.Selection([('N', 'Normal'),
                                         ('R', 'Regularizações'),
                                         ('A', 'Apur. Resultados'),
                                         ('J', 'Ajustamentos')],
                                        string="Tipo de Lançamento",
                                        help="Categorias para classificar os movimentos contabilísticos ao exportar "
                                             "o SAFT",
                                        default="N",
                                        copy=False)
    saft_inv_type = fields.Selection([('FT', 'Factura'),
                                      ('FR', 'Factura Recibo'),
                                      ('ND', 'Nota de débito'),
                                      ('VD', 'Venda a Dinheiro'),
                                      ('AA', 'Alienação de Activos'),
                                      ('DA', 'Devolução de Activos'),
                                      ('FS', 'Fatura Simplificada'),
                                      ('receipt', 'Recibo'),
                                      ('payment', 'Pagamento'),
                                      ('RC', 'Recibo Emitido'),
                                      ('AR', 'Aviso de Cobrança/Recibo'),
                                      ('RG', 'Outros Recibos Emitidos')],
                                     string="Tipo de Documento",
                                     help="Categorias para classificar os documentos comerciais, na exportação do SAFT",
                                     default="FT",
                                     copy=False)
    por_defeito = fields.Boolean(string="Diário por defeito", copy=False)
    manual = fields.Boolean(string="Faturação Manual", copy=False)
    integrado = fields.Boolean(string="Integrado", help="Documentos integrados de outra aplicação", copy=False)
    paga_me = fields.Boolean(string="Pagamento Automático",
                             help="Selecionar isto se quer que as faturas no Diário de VDs seja automaticamente pago",
                             default=False, copy=False)
    allow_date = fields.Boolean(string="Verificar Periodo", default=True, copy=False)

    @api.constrains('code')
    def _check_code(self):
        for journal in self:
            if not journal.code.isalnum():
                journal.code = re.sub('[^A-Za-z0-9]', '', journal.code)
            if len(self.search([('code', '=', journal.code), ('company_id', '=', self.env.user.company_id.id),
                                ('id', '!=', journal.id)])) > 0:
                if self.env.context.get('defcopy'):
                    ctx = self.env.context.copy()
                    del ctx['defcopy']
                    journal.code = journal.with_context(ctx).generate_code()
                else:
                    raise ValidationError('Este código já existe noutro diário')
        return True

    @api.constrains('type')
    def _check_type(self):
        for journal in self:
            if journal.type in ['sale', 'purchase'] and not journal.refund_sequence:
                raise ValidationError('O diário tem de ter sequência de reembolso')
        return True

    @api.onchange('code')
    def _onchange_code(self):
        for journal in self:
            if journal.code:
                journal.code = re.sub('[^A-Za-z0-9]', '', journal.code)

    def copy(self, default=None):
        ctx = self.env.context.copy()
        ctx['defcopy'] = True
        return super(AccountJournal, self.with_context(ctx)).copy(default)

    def generate_code(self):
        for journal in self:
            if self.search([('code', '=', journal.code), ('company_id', '=', self.env.user.company_id.id)]):
                for num in range(1, 100):
                    journal_code = prefixo_journal_type[journal.type] + str(num)
                    if not self.env['account.journal'].search(
                            [('code', '=', journal_code), ('company_id', '=', self.env.user.company_id.id)], limit=1):
                        return journal_code
        return journal.code

    def write(self, vals):
        for journal in self:
            if 'manual' in vals or 'integrado' in vals:
                total = self.env['account.payment'].search_count([('journal_id', '=', journal.id)])
                total += self.env['account.move'].search_count([('journal_id', '=', journal.id)])
                if 'manual' in vals and total > 0:
                    raise ValidationError(_('Não pode definir o diário como manual, '
                                            'pois este já entra em faturas ou recibos.'))
                if 'integrado' in vals and total > 0:
                    raise ValidationError(_('Não pode definir o diário como integrado, '
                                            'pois este já entra em faturas ou recibos.'))
        return super(AccountJournal, self).write(vals)

    def action_open_sequence_wizard(self):
        self.ensure_one()
        return {
            'name': _('Configurar Sequências'),
            'type': 'ir.actions.act_window',
            'res_model': 'set.journal.sequences.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_journal_id': self.id,
            }
        }