# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path
from odoo import _
from odoo.exceptions import UserError
from . import sale_order
from datetime import datetime


def hash_sale_order(self, integrado, manual, datadocumento, datasistema, number,
                    identi, numHash, antigoHash, totalbruto):
    _logger = getattr(self, '_logger', None)

    # Se datasistema não for passado, usar hora do sistema
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

    # Windows ou integrado → ignora hash
    if sys.platform == "win32" or integrado:
        return {'hash': '', 'hash_date': datasistema, 'hash_control': '0'}

    move = self  # alias

    # --- Determinar tipo de documento (OR, PP, NE, FC) ---
    saft_type = move.type_doc or "OR"

    # --- Procurar o documento anterior usando ordenação natural ---
    import re

    def natural_sort_key(so):
        s = so.name or ''
        if not s: return []
        return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', s)]

    # Procurar todos os candidatos da mesma série
    domain = [
        ('company_id', '=', move.company_id.id),
        ('type_doc', '=', saft_type),
        ('certificated', '=', True),
        ('id', '!=', move.id),
        ('hash', 'not in', [False, '']),
    ]
    candidate_orders = self.env['sale.order'].search(domain)

    # Filtrar e ordenar para encontrar o predecessor
    current_so_key = natural_sort_key(move)
    predecessors = [so for so in candidate_orders if natural_sort_key(so) < current_so_key]

    prev_hash = ""
    prev_move_id = None
    prev_move_name = None
    if predecessors:
        predecessors.sort(key=natural_sort_key)
        prev_move = predecessors[-1]
        prev_hash = "".join((prev_move.hash or "").split())
        prev_move_id = prev_move.id
        prev_move_name = f"{prev_move.type_doc} {prev_move.name}"

    # Caminhos
    hash_dir = "/opt/hashDir/"
    chave_privada = "/opt/hashDir/ChavePrivadaAO.pem"
    Path(hash_dir).mkdir(parents=True, exist_ok=True)

    if not all([datadocumento, datasistema, number, totalbruto is not None]):
        raise UserError(_("Dados incompletos para geração do hash."))

    # --- Preparar dados para o hash ---
    # Garantir que datadocumento tem apenas a data no formato YYYY-MM-DD
    if isinstance(datadocumento, datetime):
        datadocumento_fmt = datadocumento.strftime("%Y-%m-%d")
    else:
        datadocumento_fmt = str(datadocumento)[:10]
    # Formatação
    datasistema_fmt = datasistema.strftime("%Y-%m-%dT%H:%M:%S")
    totalbruto_fmt = "{:.2f}".format(float(totalbruto)).replace(",", ".")

    # Importante: concatenar o tipo + número
    numero_completo = f"{saft_type} {number}"

    entrada_txt = f"{datadocumento_fmt};{datasistema_fmt};{numero_completo};{totalbruto_fmt};"
    if prev_hash:
        entrada_txt += prev_hash

    # Debug
    if _logger:
        _logger.info(
            "[DEBUG HASH SALE] Série=%s, atual=%s, anterior=%s (id=%s)",
            saft_type, numero_completo, prev_move_name, prev_move_id
        )
        _logger.info(f"[DEBUG HASH SALE] numHash={numHash}, antigoHash={repr(antigoHash)}")
        _logger.info(f"[DEBUG HASH SALE] String para assinar: '{entrada_txt}'")
    self.message_post(body=f"[DEBUG HASH SALE] Série={saft_type}, atual={numero_completo}, anterior={prev_move_name} (id={prev_move_id})")
    self.message_post(body=f"[DEBUG HASH SALE] String para assinar: '{entrada_txt}'")

    # Escrever ficheiro
    txt_path = os.path.join(hash_dir, f"{identi}.txt")
    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
    #with open(txt_path, "w", newline="") as f:
        f.write(entrada_txt)

    # Assinar
    sha1_path = os.path.join(hash_dir, f"{identi}.sha1")
    b64_path = os.path.join(hash_dir, f"{identi}.b64")
    try:
        subprocess.run(['openssl', 'dgst', '-sha1', '-sign', chave_privada, '-out', sha1_path, txt_path], check=True)
        subprocess.run(['openssl', 'enc', '-base64', '-in', sha1_path, '-out', b64_path, '-A'], check=True)
    except subprocess.CalledProcessError as e:
        raise UserError(_("Erro ao gerar assinatura digital (sale.order): %s") % e)

    with open(b64_path, "r") as f:
        novohash = "".join((f.read() or "").split())

    values = {'hash': novohash, 'hash_date': datasistema}
    values['hash_control'] = f"1-{saft_type}M {move.origin or ''}" if manual else "1"

    self.message_post(body=f"[DEBUG HASH SALE] Hash gerado: {novohash}")
    if _logger:
        _logger.info(f"[DEBUG HASH SALE] Hash gerado: {novohash}")

    return values