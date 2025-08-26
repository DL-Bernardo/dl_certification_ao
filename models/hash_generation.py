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

    # --- SEMPRE descobrir o hash anterior no mesmo diário/mov. ---
    prev_hash = ""
    prev_move = self.env['account.move'].search([
        ('journal_id', '=', self.journal_id.id),
        ('company_id', '=', self.company_id.id),
        ('state', '=', 'posted'),
        ('move_type', '=', self.move_type),
        ('id', '!=', self.id),
        ('hash', '!=', False),
        ('hash', '!=', ''),
        ('hash_date', '<', datasistema),  # encadear por data de sistema
    ], order='hash_date desc, id desc', limit=1)

    # fallback caso hash_date ainda não exista em dados antigos
    if not prev_move:
        prev_move = self.env['account.move'].search([
            ('journal_id', '=', self.journal_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('move_type', '=', self.move_type),
            ('id', '<', self.id),
            ('hash', '!=', False),
            ('hash', '!=', ''),
        ], order='id desc', limit=1)

    if prev_move:
        prev_hash = prev_move.hash or ""
        # remover espaços/quebras de linha/eventuais tabs
        prev_hash = "".join(prev_hash.split())

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
    # Registos seguintes: acrescentar o hash anterior (sem ';' no fim)
    if prev_hash:
        entrada_txt += prev_hash

    # Logs de diagnóstico
    prev_len = len(prev_hash) if prev_hash else 0
    prev_tail = prev_hash[-8:] if prev_hash else ""
    if _logger:
        _logger.info(f"[DEBUG HASH] numHash={numHash}, antigoHash(param)={repr(antigoHash)}")
        _logger.info(f"[DEBUG HASH] prev_move_id={prev_move.id if prev_move else None}, prev_hash_len={prev_len}, prev_hash_tail={prev_tail}")
        _logger.info(f"[DEBUG HASH] InvoiceNo usado: {number}")
        _logger.info(f"[DEBUG HASH] String para assinar: '{entrada_txt}'")
    self.message_post(body=f"[DEBUG HASH] numHash={numHash}, antigoHash(param)={repr(antigoHash)}")
    self.message_post(body=f"[DEBUG HASH] prev_move_id={prev_move.id if prev_move else None}, prev_hash_len={prev_len}, prev_hash_tail={prev_tail}")
    self.message_post(body=f"[DEBUG HASH] InvoiceNo usado: {number}")
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
        novohash = "".join((f.read() or "").split())  # garantir sem quebras/esp.

    values = {'hash': novohash, 'hash_date': datasistema}
    values['hash_control'] = f"1-{self.journal_id.saft_inv_type}M {self.origin or ''}" if manual else "1"

    self.message_post(body=f"[DEBUG HASH] Hash gerado: {novohash}")
    if _logger:
        _logger.info(f"[DEBUG HASH] Hash gerado: {novohash}")

    return values