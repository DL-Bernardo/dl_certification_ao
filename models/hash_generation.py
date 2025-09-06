# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path
from odoo import _
from odoo.exceptions import UserError

def hash(self, integrado, manual, datadocumento, datasistema, number, identi, numHash, antigoHash, totalbruto):
    _logger = getattr(self, '_logger', None)

    # Windows ou integrado → ignora hash
    if sys.platform == "win32" or integrado:
        return {'hash': '', 'hash_date': datasistema, 'hash_control': '0'}

    move = self  # alias para clareza

    # --- Determinar hash anterior por ordem numérica ---
    prev_hash = ""
    saft_type = move.journal_id.saft_inv_type or 'FT'

    prev_move = self.env['account.move'].search([
        ('journal_id', '=', move.journal_id.id),
        ('company_id', '=', move.company_id.id),
        ('state', '=', 'posted'),
        ('journal_id.saft_inv_type', '=', saft_type),
        ('id', '!=', move.id),
        ('name', '<', move.name),  # encadeamento sequencial
        ('hash', '!=', False),
        ('hash', '!=', ''),
    ], order='name desc', limit=1)

    if prev_move:
        prev_hash = "".join((prev_move.hash or "").split())
        prev_move_id = prev_move.id
        prev_move_name = prev_move.name
    else:
        prev_hash = ""
        prev_move_id = None
        prev_move_name = None

    # Caminhos
    hash_dir = "/opt/hashDir/"
    chave_privada = "/opt/hashDir/ChavePrivadaAO.pem"
    Path(hash_dir).mkdir(parents=True, exist_ok=True)

    # Validação básica
    if not all([datadocumento, datasistema, number, totalbruto is not None]):
        raise UserError(_("Dados incompletos para geração do hash."))

    # Formatação dos campos
    datasistema_fmt = str(datasistema).replace(" ", "T")
    totalbruto_fmt = "{:.2f}".format(float(totalbruto)).replace(",", ".")

    # Mensagem base (1º registo termina em ';')
    entrada_txt = f"{datadocumento};{datasistema_fmt};{number};{totalbruto_fmt};"
    if prev_hash:
        entrada_txt += prev_hash

    # Logs de diagnóstico
    if _logger:
        _logger.info(
            "[DEBUG HASH] Série=%s, atual=%s, anterior=%s (id=%s)",
            saft_type, move.name, prev_move_name, prev_move_id
        )
        _logger.info(f"[DEBUG HASH] numHash={numHash}, antigoHash(param)={repr(antigoHash)}")
        _logger.info(f"[DEBUG HASH] String para assinar: '{entrada_txt}'")
    self.message_post(body=f"[DEBUG HASH] Série={saft_type}, atual={move.name}, anterior={prev_move_name} (id={prev_move_id})")
    self.message_post(body=f"[DEBUG HASH] String para assinar: '{entrada_txt}'")

    # Escrever ficheiro a assinar (sem newline no fim)
    txt_path = os.path.join(hash_dir, f"{identi}.txt")
    with open(txt_path, "w", newline="") as f:
        f.write(entrada_txt)

    # Assinar (RSA/SHA1, PKCS#1 v1.5) e converter para Base64 numa só linha
    sha1_path = os.path.join(hash_dir, f"{identi}.sha1")
    b64_path = os.path.join(hash_dir, f"{identi}.b64")
    try:
        subprocess.run(['openssl', 'dgst', '-sha1', '-sign', chave_privada, '-out', sha1_path, txt_path], check=True)
        subprocess.run(['openssl', 'enc', '-base64', '-in', sha1_path, '-out', b64_path, '-A'], check=True)
    except subprocess.CalledProcessError as e:
        raise UserError(_("Erro ao gerar assinatura digital: %s") % e)

    with open(b64_path, "r") as f:
        novohash = "".join((f.read() or "").split())

    values = {'hash': novohash, 'hash_date': datasistema}
    values['hash_control'] = f"1-{move.journal_id.saft_inv_type}M {move.origin or ''}" if manual else "1"

    self.message_post(body=f"[DEBUG HASH] Hash gerado: {novohash}")
    if _logger:
        _logger.info(f"[DEBUG HASH] Hash gerado: {novohash}")

    return values