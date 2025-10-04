# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
from pathlib import Path
from odoo import _
from odoo.exceptions import UserError
from datetime import datetime

def hash_stock_picking(self, integrado, manual, datadocumento, datasistema, number,
                       identi, numHash, antigoHash, totalbruto):
    _logger = getattr(self, '_logger', None)

    if not datasistema:
        datasistema = datetime.now()
    elif isinstance(datasistema, str):
        try:
            datasistema = datetime.fromisoformat(datasistema)
        except ValueError:
            try:
                datasistema = datetime.strptime(datasistema, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                datasistema = datetime.now()

    if sys.platform == "win32" or integrado:
        return {'hash': '', 'hash_date': datasistema, 'hash_control': '0'}

    move = self  # alias for stock.picking

    # --- Determinar hash anterior usando ordenação natural ---
    def natural_sort_key(record):
        s = record.name or ''
        if not s: return []
        return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', s)]

    # --- Determinar série SAFT (código curto, ex: GR, GT, etc.) ---
    saft_type_value = move.picking_type_id
    saft_type = getattr(move.picking_type_id, "saft_doc_type", None) or "GR"

    #saft_type_field = 'picking_type_id'
    #saft_type_value = move.picking_type_id
    #saft_type = saft_type_value.name or 'STOCK'

    domain = [
        ('company_id', '=', move.company_id.id),
        ('picking_type_id', '=', saft_type_value.id),
        ('state', '=', 'done'),
        ('id', '!=', move.id),
        ('hash', 'not in', [False, '']),
    ]
    candidate_docs = self.env['stock.picking'].search(domain)

    current_key = natural_sort_key(move)
    predecessors = [doc for doc in candidate_docs if natural_sort_key(doc) < current_key]

    prev_hash = ""
    prev_move_id = None
    prev_move_name = None
    if predecessors:
        predecessors.sort(key=natural_sort_key)
        prev_move = predecessors[-1]
        prev_hash = "".join((prev_move.hash or "").split())
        prev_move_id = prev_move.id
        prev_move_name = prev_move.name

    # --- Preparar dados para o hash ---
    # Garantir que datadocumento tem apenas a data no formato YYYY-MM-DD
    if isinstance(datadocumento, datetime):
        datadocumento_fmt = datadocumento.strftime("%Y-%m-%d")
    else:
        datadocumento_fmt = str(datadocumento)[:10]

    datasistema_fmt = datasistema.strftime("%Y-%m-%dT%H:%M:%S")
    totalbruto_fmt = "{:.2f}".format(float(totalbruto)).replace(",", ".")

    # Número completo no formato SAFT: "Série + espaço + number"
    numero_completo = f"{saft_type} {number}"

    entrada_txt = f"{datadocumento_fmt};{datasistema_fmt};{numero_completo};{totalbruto_fmt};"
    if prev_hash:
        entrada_txt += prev_hash

    # Debug
    if _logger:
        _logger.info(
            "[DEBUG HASH STOCK] Série=%s, atual=%s, anterior=%s (id=%s)",
            saft_type, numero_completo, prev_move_name, prev_move_id
        )
        _logger.info(f"[DEBUG HASH STOCK] String para assinar: '{entrada_txt}'")
    self.message_post(body=f"[DEBUG HASH STOCK] Série={saft_type}, atual={numero_completo}, anterior={prev_move_name} (id={prev_move_id})")
    self.message_post(body=f"[DEBUG HASH STOCK] String para assinar: '{entrada_txt}'")

    # --- Assinatura ---
    hash_dir = "/opt/hashDir/"
    chave_privada = "/opt/hashDir/ChavePrivadaAO.pem"
    Path(hash_dir).mkdir(parents=True, exist_ok=True)

    txt_path = os.path.join(hash_dir, f"{identi}.txt")
    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(entrada_txt)

    sha1_path = os.path.join(hash_dir, f"{identi}.sha1")
    b64_path = os.path.join(hash_dir, f"{identi}.b64")
    try:
        subprocess.run(['openssl', 'dgst', '-sha1', '-sign', chave_privada, '-out', sha1_path, txt_path], check=True)
        subprocess.run(['openssl', 'enc', '-base64', '-in', sha1_path, '-out', b64_path, '-A'], check=True)
    except subprocess.CalledProcessError as e:
        raise UserError(_("Erro ao gerar assinatura digital (stock.picking): %s") % e)

    with open(b64_path, "r") as f:
        novohash = "".join((f.read() or "").split())

    values = {'hash': novohash, 'hash_date': datasistema}
    values['hash_control'] = f"1-{saft_type}M {move.origin or ''}" if manual else "1"

    self.message_post(body=f"[DEBUG HASH STOCK] Hash gerado: {novohash}")
    if _logger:
        _logger.info(f"[DEBUG HASH STOCK] Hash gerado: {novohash}")

    return values