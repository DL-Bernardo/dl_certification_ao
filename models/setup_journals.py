# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _create_journals(env):
    """
    This hook is used to ensure that the ND, FR, and NC journals are created for all companies.
    It will run after the module is installed or updated.
    """
    companies = env['res.company'].search([])
    for company in companies:
        journal_model = env['account.journal'].with_company(company)

        # Check for Nota de Débito (ND)
        if not journal_model.search([('code', '=', 'ND')]):
            _logger.info(f"Creating 'Nota de Débito' journal for company: {company.name}")
            journal_model.create({
                'name': 'Nota de Débito',
                'code': 'ND',
                'type': 'sale',
                'refund_sequence': True,
                'saft_inv_type': 'ND',
                'allow_date': False,
                'company_id': company.id,
            })

        # Check for Fatura-Recibo (FR)
        if not journal_model.search([('code', '=', 'FR')]):
            _logger.info(f"Creating 'Fatura-Recibo' journal for company: {company.name}")
            journal_model.create({
                'name': 'Fatura-Recibo',
                'code': 'FR',
                'type': 'sale',
                'saft_inv_type': 'FR',
                'refund_sequence': True,
                'company_id': company.id,
            })

        # Check for Nota de Crédito (NC)
        if not journal_model.search([('code', '=', 'NC')]):
            _logger.info(f"Creating 'Nota de Crédito' journal for company: {company.name}")
            journal_model.create({
                'name': 'Nota de Crédito',
                'code': 'NC',
                'type': 'sale',
                'saft_inv_type': 'NC',
                'refund_sequence': True,
                'company_id': company.id,
            })