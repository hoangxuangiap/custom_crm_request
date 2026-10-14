{
    "name": "Custom CRM Request",
    "version": "19.0.1.0.0",
    "summary": "Manage customer requests, CRM opportunities and quotations",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "product",
        "sale_management",
        "sale_crm",
        "hr",
    ],
    'data': [
        'security/crm_request_security.xml',
        'security/ir.model.access.csv',
        'wizard/import_request_wizard_views.xml',
        'views/crm_customer_request_views.xml',
        'views/crm_lead_views.xml',
        'views/menus.xml',
    ],
    "installable": True,
    "application": True,
}
