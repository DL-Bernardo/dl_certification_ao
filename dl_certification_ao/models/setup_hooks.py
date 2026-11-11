# -*- coding: utf-8 -*-

import logging
from odoo import api

_logger = logging.getLogger(__name__)

def _pre_init_hook(cr_or_env):
    """
    This hook is used to clean up stale ir.model.data records from previous
    failed installations, or map existing database journals to the module's
    XML IDs to prevent duplicate code ValidationErrors during installation.
    """
    from odoo import SUPERUSER_ID
    env = cr_or_env if hasattr(cr_or_env, 'company') else api.Environment(cr_or_env, SUPERUSER_ID, {})
    module_name = 'dl_certification_ao'

    journal_xml_ids = {
        'opc_journal_ft': 'FT',
        'opc_journal_fr': 'FR',
        'opc_journal_nc': 'NC',
    }

    for xml_id_name, code in journal_xml_ids.items():
        # Search for existing journal in the database with the same code
        existing_journal = env['account.journal'].search([
            ('code', '=', code),
            ('company_id', '=', env.company.id)
        ], limit=1)

        # Search for the external ID
        data = env['ir.model.data'].search([
            ('module', '=', module_name),
            ('name', '=', xml_id_name)
        ])

        if existing_journal:
            # If the journal exists, map the XML ID to it
            if data:
                data.write({
                    'model': 'account.journal',
                    'res_id': existing_journal.id,
                    'noupdate': True,
                })
            else:
                env['ir.model.data'].create({
                    'module': module_name,
                    'name': xml_id_name,
                    'model': 'account.journal',
                    'res_id': existing_journal.id,
                    'noupdate': True,
                })
            _logger.info(f"Mapped existing journal '{code}' to XML ID '{module_name}.{xml_id_name}'")
        else:
            # If it does not exist, clean up any stale XML ID record
            if data:
                _logger.warning(
                    f"Found existing ir.model.data record for {xml_id_name} but journal does not exist. "
                    "Deleting it to ensure a clean installation."
                )
                data.unlink()

    # No return value is needed for pre-init hooks.