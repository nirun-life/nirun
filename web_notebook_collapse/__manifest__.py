#  Copyright (c) 2023 NSTDA

{
    "name": "Notebook Collapse",
    "summary": "Add collapse to Notebook Module",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA, DADOS, Harit, Kawin",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web", "web_notebook_advance"],
    "assets": {
        "web.assets_backend": [
            "/web_notebook_collapse/static/lib/masonry/masonry.pkgd.js",
            "/web_notebook_collapse/static/src/views/form/notebook.xml",
            "/web_notebook_collapse/static/src/views/form/notebook.esm.js",
            "/web_notebook_collapse/static/src/views/form/notebook.scss",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
