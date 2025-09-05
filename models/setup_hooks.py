# -*- coding: utf-8 -*-

import logging
from odoo import api

_logger = logging.getLogger(__name__)

def _pre_init_hook(env):
    """
    This hook is used to clean up stale ir.model.data records from previous
    failed installations. This ensures that the journals defined in the XML
    data file can be created correctly on a new installation attempt.
    """
    # The env passed to a pre-init hook is already sudoed.
    module_name = 'opc_certification_ao_v17'

    journal_xml_ids = [
        'opc_journal_ft',
        'opc_journal_nd',
        'opc_journal_fr',
        'opc_journal_nc',
    ]

    for xml_id_name in journal_xml_ids:
        # Search for the external ID
        data = env['ir.model.data'].search([
            ('module', '=', module_name),
            ('name', '=', xml_id_name)
        ])
        if data:
            _logger.warning(
                f"Found existing ir.model.data record for {xml_id_name}. "
                "This might be a stale record from a previous failed installation. "
                "Deleting it to ensure a clean installation."
            )
            data.unlink()

    # No return value is needed for pre-init hooks.