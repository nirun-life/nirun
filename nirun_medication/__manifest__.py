#  Copyright (c) 2021 Piruin P.

{
    "name": "Medications",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun", "nirun_patient"],
    "data": [
        "security/medication_group.xml",
        "security/ir.model.access.csv",
        "data/ni.medication.form.csv",
        "data/ni.quantity.unit.csv",
        "data/ni.medication.statement.category.csv",
        "views/medication_form_views.xml",
        "views/medication_ingredient_views.xml",
        "views/medication_views.xml",
        "views/medication_statement_views.xml",
        "views/medication_menus.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
