# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from odoo import _
from odoo.exceptions import UserError

def hash(self, integrado, manual, datadocumento, datasistema, number, identi, numHash, antigoHash, totalbruto):
    # Ambiente Windows ou integrado → ignora hash
    if sys.platform == "win32" or integrado:
        return {'hash': '', 'hash_date': datasistema, 'hash_control': '0'}

    # Caminhos
    hash_dir = "/opt/hashDir/"
    chave_privada = "/opt/hashDir/ChavePrivadaAO.pem"
    Path(hash_dir).mkdir(parents=True, exist_ok=True)

    # Validação básica
    if not all([datadocumento, datasistema, number, totalbruto]):
        raise UserError(_("Dados incompletos para geração do hash."))

    # Formatando valores
    datasistema_fmt = str(datasistema).replace(" ", "T")
    totalbruto_fmt = "{:.2f}".format(float(totalbruto)).replace(",", ".")
    entrada_txt = f"{datadocumento};{datasistema_fmt};{number};{totalbruto_fmt};"
    if numHash > 0:
        if not antigoHash:
            raise ValueError("Erro ao gerar hash: Hash anterior em falta para documento sequencial.")
        entrada_txt += antigoHash

    # Gravar conteúdo no ficheiro txt
    txt_path = os.path.join(hash_dir, f"{identi}.txt")
    with open(txt_path, "w") as f:
        f.write(entrada_txt)

    # Assinatura RSA
    sha1_path = os.path.join(hash_dir, f"{identi}.sha1")
    b64_path = os.path.join(hash_dir, f"{identi}.b64")
    try:
        subprocess.run(['openssl', 'dgst', '-sha1', '-sign', chave_privada, '-out', sha1_path, txt_path], check=True)
        subprocess.run(['openssl', 'enc', '-base64', '-in', sha1_path, '-out', b64_path, '-A'], check=True)
    except subprocess.CalledProcessError as e:
        raise UserError(_("Erro ao gerar assinatura digital: %s") % e)

    # Ler resultado final
    with open(b64_path, "r") as f:
        novohash = f.read().strip()

    # Construir valores
    values = {'hash': novohash, 'hash_date': datasistema}
    if manual:
        values['hash_control'] = f"1-{self.journal_id.saft_inv_type}M {self.origin or ''}"
    else:
        values['hash_control'] = "1"

    # Log opcional no chatter
    self.message_post(body=f"Hash SAFT gerado: {novohash}")

    return values
