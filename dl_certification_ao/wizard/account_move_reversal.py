import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        """ Set reason cancel on credit note """
        res = super()._prepare_default_reversal(move)
        type = 'Anulação'

        refund_method = ''
        if hasattr(self, 'refund_choice'):
            refund_method = self.refund_choice
        elif hasattr(self, 'refund_method'):
            # Fallback for older/custom versions
            refund_method = self.refund_method
        else:
            _logger.warning("Could not determine refund method: 'refund_choice' or 'refund_method' not found on account.move.reversal wizard.")

        if refund_method == 'refund':
            type = 'Rectificação'

        new_origin = ''
        contador = 0
        for moves in self.move_ids:
            contador = contador + 1
            if moves.name:
                if contador > 1:
                    new_origin += str(moves.journal_id.saft_inv_type) + ' ' + str(moves.name) + ', '
                else:
                    new_origin += str(moves.journal_id.saft_inv_type) + ' ' + str(moves.name)
        res.update({
            'reason_cancel': self.reason,
            'invoice_origin': new_origin,
            'ref': type,
        })
        return res