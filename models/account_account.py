# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = "account.account"
    _parent_name = "parent_id"  # Necessário para a hierarquia funcionar nas tree views
    _parent_store = True

    active = fields.Boolean(string="Active", default=True)

    tipo_conta = fields.Selection([
        ('GR', 'GR - Conta de 1.º grau da contabilidade geral'),
        ('GA', 'GA - Conta agregadora ou integradora da contabilidade geral'),
        ('GM', 'GM - Conta de movimento da contabilidade geral'),
        ('AR', 'AR - Conta de 1.º grau da contabilidade analítica'),
        ('AA', 'AA - Conta agregadora ou integradora da contabilidade analítica'),
        ('AM', 'AM - Conta de movimento da contabilidade analítica')],
        string="Grupo da conta", required=True, default="GM", copy=False)

    parent_id = fields.Many2one('account.account', string="Conta Pai")
    parent_id = fields.Many2one('account.account', string="Conta Pai", ondelete='cascade')
    parent_path = fields.Char(index=True)
    children_ids = fields.One2many('account.account', 'parent_id', string='Contas Filhas')
    taxonomia_id = fields.Many2one('taxonomia', string='Taxonomia')
    code = fields.Char(size=10, required=True, index=True)

    # Atualiza tipo de conta automaticamente ao criar
    @api.model
    def create(self, vals):
        if 'code' in vals and not vals.get('parent_id'):
            for i in range(1, 10):
                parent_code = vals['code'][:-i]
                if parent_code:
                    parent = self.env['account.account'].search([('code', '=', parent_code)], limit=1)
                    if parent:
                        vals['parent_id'] = parent.id
                        break

        if vals.get('parent_id') is False:
            vals['tipo_conta'] = "GR"

        account = super(AccountAccount, self).create(vals)

        if account.parent_id:
            account.parent_id.tipo_conta = 'GA'

            siblings = self.env['account.account'].search([
                ('code', '=like', account.code + '%'),
                ('parent_id', '=', account.parent_id.id),
                ('id', '!=', account.id)
            ])
            siblings.write({'parent_id': account.id})

        return account

    def write(self, vals):
        parent_changed = 'parent_id' in vals
        res = super(AccountAccount, self).write(vals)

        if parent_changed:
            for account in self:
                if not account.parent_id:
                    account.tipo_conta = "GR"
                else:
                    account.parent_id.tipo_conta = 'GA'

        return res