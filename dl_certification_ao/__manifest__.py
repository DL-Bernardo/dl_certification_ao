# -*- coding: utf-8 -*-
# Formerly: opc_certification_ao_v17
{
    'name': 'Angola Fiscal Compliance & AGT Certification (InvoiceOne)',
    'summary': 'Angola Fiscal Compliance & Invoicing Certification (AGT & SAF-T AO) by InvoiceOne',
    'description': """
Core de Certificação Fiscal da DIGITALUB para o mercado de Angola.
==================================================================
* Validação e Geração de Hash de documentos fiscais (Faturas, Faturas-Recibo, Notas de Crédito).
* Configuração e extração do arquivo magnético SAF-T AO (Standard Audit File for Tax).
* Integração e suporte a tipos de produtos SAF-T e tabelas de taxonomia locais.
* Compatibilidade nativa com fluxos de Vendas, Faturamento, Stock e Guias de Transporte.
    """,
    'author': "DIGITALUB ANGOLA, LDA",
    'website': "https://www.digitalub.ao",
    'category': 'Accounting/Localizations',
    'version': '17.0.1.0.2',
    'license': 'OPL-1',  # Licença comercial proprietária para venda na Odoo Store
    'price': 749.0,     # Preço sugerido em Euros/Dólares na plataforma
    'currency': 'EUR',   # Moeda padrão da loja de aplicativos do Odoo
    
    # Dependências de módulos do sistema e localização base
    'depends': [
        'account', 
        'sale', 
        'stock', 
        'sale_stock', 
        'l10n_ao_account', 
        'web',
        'base_vat', 
        'delivery', 
        'product', 
        'base'
    ],
    
    # Arquivos XML/CSV carregados na inicialização do módulo
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'data/account_data.xml',
        'data/account_tax_data.xml',
        'data/tipos_produtos_saft.xml',
        'data/data_GT.xml',
        'data/res_lang.xml',
        'data/taxonomias_data.xml',
        'data/ir_sequence_type.xml',
        'data/sequence.xml',
        'data/journal_data.xml',
        'views/account_journal_view.xml',
        'views/report_invoice_document_view.xml',
        'views/account_move_form_view.xml',
        'views/account_move_factura_recibo_view.xml',
        'views/account_view.xml',
        'views/account_tax_view.xml',
        'views/taxonomia_view.xml',
        'views/tipo_produto_saft.xml',
        'views/account_config_settings.xml',
        'views/product_view.xml',
        'views/res_view.xml',
        'views/stock_view.xml',
        'views/pedidos_at_historico_view.xml',
        'views/utilizador_financas_view.xml',
        'wizard/exportar_stock_view.xml',
        'views/hist_saft_view.xml',
        'views/account_resequence_wizard_view.xml',
        'wizard/recall_at_view.xml',
        'wizard/alterar_guia_view.xml',
        'wizard/manual_code_view.xml',
        'wizard/import_saft_view.xml',
        'wizard/call_at_wiz_view.xml',
        'wizard/wizard_l10n_pt_saft.xml',
        'wizard/cancelar_fatura_view.xml',
        'wizard/alert_atcud_view.xml',
        'views/sale_order.xml',
        'views/menus.xml',
        'wizard/cancelar_sale_order_view.xml',
    ],
    
    # Mapeamento de mídia para vitrine do app
    'images': [
        'static/description/banner.png'
    ],
    
    'pre_init_hook': '_pre_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}