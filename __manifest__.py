# -*- coding: utf-8 -*-
{
    'name': "TLSystem",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','account'], 

    # always loaded
    'data': [
        # 'views/masterviews.xml',
        'security/security.xml',
        # 'security/sec_ms_customer.xml',
        # 'security/sec_ms_customerlocation.xml',
        # 'security/sec_ms_expense.xml',
        # 'security/sec_ms_people.xml',
        # 'security/sec_ms_productbrand.xml',
        # 'security/sec_ms_productbrandcategory.xml',
        # 'security/sec_ms_user.xml',
        'security/ir.model.access.csv',
        'views/master/tl_ms_expense_view.xml',
        'views/master/tl_ms_user_view.xml',
        'views/master/tl_ms_userapproval_view.xml',
        'views/master/tl_ms_people_view.xml',
        'views/master/tl_ms_customer_view.xml',
        'views/master/tl_ms_customerlocation_view.xml',
        'views/master/tl_ms_productbrandcategory_view.xml',
        'views/master/tl_ms_productbrand_view.xml',
        'views/master/tl_ms_modulelist_view.xml',
        'views/master/tl_ms_modulestage_view.xml',   
        'views/master/tl_ms_bankmaster_view.xml',   
        'views/master/tl_ms_bankaccount_view.xml',   
        'views/master/tl_ms_customerinherit_view.xml',  
        'views/master/tl_ms_bugreport_view.xml',
        'views/master/tl_ms_tokenhistory_view.xml', 
        'views/master/tl_ms_inheruser_view.xml', 
        'views/master/tl_ms_cuscon_view.xml', 
        
        # 'views/master/tl_ms_custom_confirmation_view.xml',  
        # 'views/master/tl_ms_res_partner_driver_view.xml', 
        # 'views/transaction/tl_tr_expenditure_view.xml',
        # 'views/transaction/tl_tr_expenditureitem_view.xml',
        'report/report.xml', 
        'report/tl_rpt_uangjalanxlsx.xml', 
        'views/transaction/tl_tr_inheraccountpaymentregister_view.xml',
        'views/transaction/tl_tr_workorder_view.xml',
        'views/transaction/tl_tr_draftwo_view.xml',
        'views/transaction/tl_tr_quotation_view.xml',
        'views/transaction/tl_tr_quotationitem_view.xml',
        'views/transaction/tl_tr_invoice_view.xml', 
        'views/transaction/tl_tr_inherinvoice_view.xml', 
        'views/transaction/tl_tr_payment_receive_view.xml', 
        'views/transaction/tl_tr_payment_allocation_view.xml', 
        'views/transaction/tl_tr_accpytregapproval_view.xml', 
        'views/transaction/tl_tr_claimaccountability_view.xml', 
        'views/transaction/tl_tr_claimaccountabilityapproval_view.xml', 
        'views/transaction/tl_tr_pertanggungjawaban_view.xml', 
        'views/transaction/tl_tr_pertanggungjawabanapproval_view.xml',
        'views/transaction/tl_tr_claimaccountabilitypendingapp_view.xml', 
        # 'wizard/uangjalan_report_view.xml', 
        # 'wizard/invoice_wizard_view.xml', 
        # 'wizard/uangjalan_report_view.xml',   
        'wizard/tl_wzd_uangjalanxlsx_view.xml', 
        'views/print/tl_ms_people_print.xml',
        'views/print/tl_tr_invoice_print.xml',
        'views/print/tl_tr_inherinvoice_print.xml',
        'views/print/tl_tr_inherinvoicedt_print.xml',
        'views/print/tl_tr_wobonputih_print.xml',
        'views/views.xml',   
        'views/css_loader.xml', 
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],  
}
