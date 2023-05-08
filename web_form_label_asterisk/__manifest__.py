#  Copyright (c) 2023 NSTDA

{
    "name": "Asterisk Label",
    "summary": "Add asterisk to Required field's label",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "/web_form_label_asterisk/static/src/views/form/form_label.xml",
            "/web_form_label_asterisk/static/src/views/form/form_label.esm.js",
            "/web_form_label_asterisk/static/src/views/form/form_label.scss",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
