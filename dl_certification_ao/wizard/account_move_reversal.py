import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        """ Set reason cancel on credit note and ensure origin is set """
        res = super()._prepare_default_reversal(move)
        
        # Determine the reason from the wizard
        reason = getattr(self, 'reason', '') or _('Retificação / Anulação')
        
        # Determine origin document number
        origin_doc = move.internal_number or move.name or ''
        # AGT usually needs the type prefix (FT, FR, etc.)
        if move.journal_id.saft_inv_type and origin_doc and not origin_doc.startswith(move.journal_id.saft_inv_type):
            origin_doc = f"{move.journal_id.saft_inv_type} {origin_doc}"

        res.update({
            'reason_cancel': reason[:64],
            'invoice_origin': origin_doc,
            'invoice_origin_id': move.id,
            'ref': reason,
        })
        if hasattr(move, 'fr_payment_journal_id') and move.fr_payment_journal_id:
            res['fr_payment_journal_id'] = move.fr_payment_journal_id.id
            
        return res