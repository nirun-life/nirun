#  Copyright (c) 2021 NSTDA

{
    "name": "Disability (Thai Localization)",
    "summary": "Thai disability observations aligned with HL7 FHIR",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_observation", "ni_coding"],
    "data": [
        "data/ni_observation_data.xml",
        "views/ni_patient_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_disability_menus.xml",
        "views/res_company_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
