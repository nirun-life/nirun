#  Copyright (c) 2023 NSTDA

{
    "name": "Notebook Advance",
    "summary": "Add more attribute for notebook such as orientation, page > icon, counter",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA, DADOS, Harit, Kawin",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "/web_notebook_advance/static/src/views/form/form_compiler.esm.js",
            "/web_notebook_advance/static/src/core/notebook/notebook.xml",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
