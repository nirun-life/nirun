# Copyright (c) 2026 NSTDA

{
    "name": "Web Speech Dictation",
    "summary": "Dictate into multiline text and HTML fields",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "author": "NSTDA",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "/web_speech_dictation/static/src/dictation/dictation_controller.js",
            "/web_speech_dictation/static/src/dictation/dictation_modal.js",
            "/web_speech_dictation/static/src/dictation/dictation_modal.xml",
            "/web_speech_dictation/static/src/dictation/dictation_modal.scss",
            "/web_speech_dictation/static/src/fields/text_field_dictation.js",
            "/web_speech_dictation/static/src/fields/text_field_dictation.xml",
            (
                "after",
                "web_editor/static/src/js/backend/html_field.js",
                "/web_speech_dictation/static/src/fields/html_field_dictation.js",
            ),
            "/web_speech_dictation/static/src/fields/html_field_dictation.xml",
            "/web_speech_dictation/static/src/fields/text_field_dictation.scss",
        ],
        "web.qunit_suite_tests": [
            "/web_speech_dictation/static/tests/**/*.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
