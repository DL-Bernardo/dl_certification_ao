# 🇦🇴 Angola - DL Certification (`dl_certification_ao`)

Este módulo Odoo v17 foi desenvolvido pela **DIGITALUB** para garantir a total conformidade das empresas que operam em Angola com os requisitos fiscais exigidos pela **Administração Geral Tributária (AGT)**.

Ele realiza a certificação de faturas, geração de assinaturas criptográficas (hash), comunicação de documentos e exportação de ficheiros de auditoria fiscal (SAF-T AO).

> [!NOTE]
> Este módulo foi renomeado de `opc_certification_ao_v17` para `dl_certification_ao` para melhor alinhamento com a identidade da DIGITALUB, mantendo total compatibilidade retroativa e suporte estrutural para referências anteriores no Python.

---

## 🚀 Funcionalidades Principais

### 1. Certificação de Documentos Fiscais
* **Assinatura Digital de Faturas:** Geração automática do Hash SHA1 conforme os requisitos da AGT para garantir a inalterabilidade e integridade dos documentos.
* **Geração de Código QR:** Criação automática do QR Code obrigatório nos documentos impressos, facilitando a verificação de validade das faturas.
* **Séries e ATCUD:** Suporte para gestão de séries de faturação e validação de códigos de validação de série (ATCUD) e alertas inteligentes.
* **Segurança e Validação de Chaves:** Validação preventiva da existência da chave privada antes da assinatura, evitando falhas ocultas no processo.
* **Prevenção de Documentos Vazios:** Bloqueio inteligente que impede a validação (publicação) ou cancelamento de documentos de clientes sem linhas de artigos, evitando inconsistências no envio do SAF-T à AGT.

### 2. Exportação e Importação de SAF-T (AO)
* **SAF-T de Faturação:** Extração e exportação do ficheiro XML SAF-T (AO) completo contendo dados da empresa, clientes, produtos/serviços, tabelas de impostos e documentos comerciais.
* **SAF-T de Inventário (Stock):** Geração do ficheiro de inventário em formato XML exigido anualmente.
* **Ferramenta de Importação:** Utilitário integrado para importar dados via SAF-T externo para fins de auditoria ou migração.

### 3. Integração e Comunicação com a AGT (Pedidos AT)
* Comunicação integrada de documentos em tempo real e de forma segura.
* Gestão e sincronização de Utilizadores das Finanças para autenticação de serviços.

### 4. Configuração Avançada de Impostos e Taxonomia
* Mapeamento de impostos (IVA 23%, 14%, 7%, 5%, Isento, etc.) com códigos e motivos de isenção oficiais (SAFT Tax Code e Exemption Reason).
* Classificação taxonómica de contas e enquadramento de tipos de produtos (Mercadorias, Matérias-Primas, etc.) para o SAF-T.

---

## 📂 Estrutura do Módulo

O módulo é composto pelos seguintes diretórios e ficheiros:
- **`models/`**: Extensões do Odoo para lidar com faturas (`account.move`), impostos (`account.tax`), diários (`account.journal`), geração de hash, comunicação com a AGT e histórico.
- **`wizard/`**: Assistentes interativos para exportação/importação do SAF-T, exportação de stock, cancelamento de faturas e controle de alertas ATCUD.
- **`views/`**: Desenhos e interfaces personalizados de diários, faturas, produtos, stock e configurações.
- **`security/`**: Regras de segurança de nível de registo e permissões (ACLs).
- **`data/`**: Carga de dados iniciais recomendados (Taxonomias, Tipos de Produtos SAFT, Diários e Sequências pré-configuradas).

---

## 🛠️ Instalação e Atualização

### Pré-requisitos
* Odoo v17 (Community ou Enterprise).
* Dependências listadas no manifesto (`account`, `sale`, `stock`, `sale_stock`, `l10n_ao_account`, `web`, `base_vat`, `delivery`, `product`, `base`).

### Passos para Instalação
1. Adicione a pasta `dl_certification_ao` ao seu caminho de addons do Odoo (`addons_path`).
2. Reinicie o servidor Odoo.
3. Ative o modo de programador.
4. Vá para a aplicação **Aplicações** e clique em **Atualizar Lista de Módulos**.
5. Procure por `dl_certification_ao` e clique em **Instalar**.

---

## 📝 Histórico de Alterações / Notas de Renomeação
* **Nome Anterior:** `opc_certification_ao_v17`
* **Nome Atual:** `dl_certification_ao`
* **Referências Python:** As referências internas ao nome anterior foram atualizadas para a nova nomenclatura, mantendo anotações estruturais nos ficheiros Python para fácil rastreio.
* **Dependências Externas:** Outros módulos adicionais (ex: `dl_withholding_tax_ao` e `opc_layouts_aov17`) foram atualizados para herdar a dependência atualizada.

---

## 👥 Suporte e Autoria

* **Desenvolvido por:** DIGITALUB ANGOLA
* **Website:** [https://www.digitalub.ao](https://www.digitalub.ao)
* **Contacto:** suporte@digitalub.ao
