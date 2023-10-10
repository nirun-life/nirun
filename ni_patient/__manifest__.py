#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Patient",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_coding",
        "ni_identifier",
        "ni_period",
        "hr",
        "mail",
        "partner_age",
        "partner_gender",
        "partner_religion",
    ],
    "data": [
        "security/ni_patient_group.xml",
        "security/ni_patient_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ni_location_type_data.xml",
        "data/ni_encounter_admit_data.xml",
        "data/ni_encounter_arrangement_data.xml",
        "data/ni_encounter_class_data.xml",
        "data/ni_encounter_courtesy_data.xml",
        "data/ni_encounter_diet_data.xml",
        "data/ni_participant_type_data.xml",
        "data/ni_encounter_discharge_disposition_data.xml",
        "data/ni_encounter_discharge_status_data.xml",
        "wizard/ni_encounter_discharge_wizard_views.xml",
        "views/ni_location_views.xml",
        "views/ni_location_type_views.xml",
        "views/ni_encounter_location_views.xml",
        "views/ni_encounter_reason_views.xml",
        "views/ni_encounter_admit_views.xml",
        "views/ni_encounter_arrangement_views.xml",
        "views/ni_encounter_class_views.xml",
        "views/ni_encounter_courtesy_views.xml",
        "views/ni_encounter_diet_views.xml",
        "views/ni_encounter_discharge_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_participant_type_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/ni_patient_views.xml",
        "views/ni_patient_menu.xml",
        "views/ni_workflow_event_views.xml",
        "views/ni_workflow_request_views.xml",
    ],
    "demo": ["data/ni_patient_demo.xml", "data/ni_location_demo.xml"],
    "application": True,
    "auto_install": False,
    "installable": True,
}
