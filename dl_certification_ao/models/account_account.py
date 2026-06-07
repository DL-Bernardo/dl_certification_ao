# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class AccountAccount(models.Model):
    _inherit = "account.account"
    _parent_name = "parent_id"
    _parent_store = True

    # --- Fields from dl_certification_ao (formerly opc_certification_ao_v17) ---
    active = fields.Boolean(string="Active", default=True)

    tipo_conta = fields.Selection([
        ('GR', 'GR - Conta de 1.º grau da contabilidade geral'),
        ('GA', 'GA - Conta agregadora ou integradora da contabilidade geral'),
        ('GM', 'GM - Conta de movimento da contabilidade geral'),
        ('AR', 'AR - Conta de 1.º grau da contabilidade analítica'),
        ('AA', 'AA - Conta agregadora ou integradora da contabilidade analítica'),
        ('AM', 'AM - Conta de movimento da contabilidade analítica')],
        string="Grupo da conta", required=True, default="GM", copy=False)

    parent_id = fields.Many2one('account.account', string="Conta Pai", ondelete='cascade')
    parent_path = fields.Char(index=True)
    children_ids = fields.One2many('account.account', 'parent_id', string='Contas Filhas')
    taxonomia_id = fields.Many2one('taxonomia', string='Taxonomia')
    code = fields.Char(size=10, required=True, index=True)


    # --- Field modifications from l10n_ao_account ---
    account_type = fields.Selection(selection_add=[('view', 'View')], ondelete={'view': 'cascade'})
    internal_group = fields.Selection(selection_add=[('view', 'View')], ondelete={'view': 'cascade'})


    # --- Methods from dl_certification_ao (formerly opc_certification_ao_v17) ---
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

    # --- Methods from l10n_ao_account ---
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        always_show_cases = (
            self._context.get('show_view_accounts') or
            self._is_specific_case_that_needs_views()
        )
        if always_show_cases:
            return super()._search(domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)
        
        if not self._contains_view_account_filter(domain):
            domain = expression.AND([domain, [('account_type', '!=', 'view')]])
        
        return super()._search(domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)
    
    
    @api.model
    def _contains_view_account_filter(self, domain):
        for element in domain:
            if isinstance(element, (list, tuple)) and len(element) == 3:
                field, operator, value = element
                if field == 'account_type':
                    if operator == '=' and value == 'view':
                        return True
                    elif operator == '!=' and value == 'view':
                        return True
                    elif operator == 'in' and isinstance(value, (list, tuple)) and 'view' in value:
                        return True
                    elif operator == 'not in' and isinstance(value, (list, tuple)) and 'view' not in value:
                        return True
            elif isinstance(element, (list, tuple)):
                if self._contains_view_account_filter(element):
                    return True
        return False

    
    def _is_specific_case_that_needs_views(self):
        if self._context.get('check_translations'):
            return True
        
        if self._context.get('print_chart_of_accounts'):
            return True
            
        return False
