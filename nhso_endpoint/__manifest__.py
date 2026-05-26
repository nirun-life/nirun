#  Copyright (c) 2023 NSTDA

{
    "name": "NHSO Endpoint",
    "summary": "NHSO Endpoint Service",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "depends": ["hs", "hv"],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "views/res_company_nhso_endpoint_views.xml",
        "views/res_config_settings_views.xml",
        "views/hs_person_views.xml",
        "views/hs_house_survey_member_views.xml",
        "views/hs_health_screening_views.xml",
        "views/hv_home_visit_views.xml",
        "views/hs_person_smartcard_views.xml",
        "views/hs_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nhso_endpoint/static/src/widget/*",
        ]
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
