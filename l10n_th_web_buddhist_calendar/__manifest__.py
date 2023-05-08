#  Copyright (c) 2023 NSTDA

{
    "name": "Buddhist Calendar",
    "summary": "Change display years to B.E.",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web", "mail"],
    "assets": {
        "web.assets_common": [
            (
                "replace",
                "web/static/lib/jquery.ui/jquery-ui.js",
                "l10n_th_web_buddhist_calendar/static/lib/jquery-ui/jquery-ui.js",
            ),
        ],
        "web.assets_backend": [
            "l10n_th_web_buddhist_calendar/static/src/views/calendar/data_picker/calendar_date_picker.esm.js",
            "l10n_th_web_buddhist_calendar/static/src/core/datepicker/datepicker.esm.js",
            "l10n_th_web_buddhist_calendar/static/src/views/list/list_renderer.esm.js",
            "l10n_th_web_buddhist_calendar/static/src/views/kanban/kanban_record.esm.js",
            "l10n_th_web_buddhist_calendar/static/src/views/field/date/date_field.esm.js",
            "l10n_th_web_buddhist_calendar/static/src/views/field/datetime/datetime_field.esm.js",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
