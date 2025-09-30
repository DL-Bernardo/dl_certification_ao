# -*- coding: utf-8 -*-

import odoo
from odoo import SUPERUSER_ID

def _post_init_hook(env):
    """
    This hook is called after the module is installed.
    It creates a journal for debit notes if it doesn't exist.
    """
    # Search for the journal by code
    journal = env['account.journal'].search([('code', '=', 'ND')], limit=1)
    if journal:
        return

    # Find the default receivable account for the main company, if available
    company = env.ref('base.main_company', raise_if_not_found=False) or env['res.company'].search([], limit=1)
    if not company:
        # Cannot create journal without a company
        return

    # The default_account_id for a sale journal should be an income account.
    income_account = env['account.account'].search(
        [('account_type', '=', 'income'), ('company_id', '=', company.id)],
        limit=1
    )

    if not income_account:
        # Fallback to any other income-like account if no direct income account is found
        income_account = env['account.account'].search(
            [('account_type', '=', 'income_other'), ('company_id', '=', company.id)],
            limit=1
        )

    if not income_account:
        # Cannot create journal without a default income account
        return

    # Create the journal
    env['account.journal'].create({
        'name': 'Debit Notes',
        'type': 'sale',
        'code': 'ND',
        'company_id': company.id,
        'default_account_id': income_account.id,
    })