#  Copyright (c) 2021 NSTDA

{
    "name": "Reception (Thai Localization)",
    "summary": "Thai localization for patient reception and check-in",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["ni_reception", "l10n_th_ni_patient_address", "l10n_th_ni_coverage"],
    "data": [
        "views/ni_reception_views.xml",
    ],
    "application": False,
    "auto_install": True,
    "installable": True,
}
