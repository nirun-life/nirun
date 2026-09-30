#  Copyright (c) 2025-2026 NSTDA

from odoo.tests import TransactionCase


class TestDosageFieldsMixin(TransactionCase):
    """ni.medication.dosage.fields.mixin._get_view must resolve every
    <group name="..."/> placeholder into real content, with no leftover
    empty placeholder left in the arch."""

    def _assert_resolved(self, model, *expected_snippets):
        arch = self.env[model].get_view(view_type="form")["arch"]
        for snippet_name in expected_snippets:
            self.assertNotIn(
                f'name="{snippet_name}" />',
                arch,
                f"{model}: {snippet_name} placeholder was not resolved",
            )
        return arch

    def test_dosage_own_form_resolves_timing_and_administration(self):
        arch = self._assert_resolved(
            "ni.medication.dosage",
            "dosage_fields",
            "dosage_administration_fields",
        )
        self.assertIn('name="dosage_display"', arch)
        self.assertIn('name="meal_offset"', arch)
        self.assertIn('name="route_id"', arch)
        # dosage IS the template, so it never gets the page-level content
        self.assertNotIn('name="dosage_tmpl_id"', arch)

    def test_request_form_resolves_full_page_content(self):
        # dosage_fields/dosage_administration_fields are nested placeholders
        # inside request's own dosage_page_content donor content - both
        # levels must resolve
        arch = self._assert_resolved(
            "ni.medication.request",
            "dosage_page_content",
            "dosage_fields",
            "dosage_administration_fields",
        )
        self.assertIn('name="dosage_display"', arch)
        self.assertIn('name="meal_offset"', arch)
        self.assertIn('name="route_id"', arch)
        self.assertIn('name="dosage_tmpl_id"', arch)
        self.assertIn("save_dosage_as_template", arch)
