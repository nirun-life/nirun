#  Copyright (c) 2025-2026 NSTDA
from lxml import etree

from odoo.tests import TransactionCase

PLACEHOLDERS = ("dosage_page_content", "dosage_fields", "dosage_administration_fields")


class TestDosageFieldsMixin(TransactionCase):
    """ni.medication.dosage.fields.mixin._get_view must resolve every
    <group name="..."/> placeholder into real content, with no leftover
    empty placeholder left in the arch."""

    def _get_arch(self, model):
        arch = self.env[model].get_view(view_type="form")["arch"]
        tree = etree.fromstring(arch)
        for name in PLACEHOLDERS:
            self.assertFalse(
                tree.xpath(f"//*[@name='{name}' and not(node())]"),
                f"{model}: {name} placeholder was not resolved",
            )
        return arch

    def test_dosage_own_form_resolves_timing_and_administration(self):
        arch = self._get_arch("ni.medication.dosage")
        self.assertIn('name="dosage_display"', arch)
        self.assertIn('name="meal_offset"', arch)
        self.assertIn('name="route_id"', arch)
        # dosage IS the template, so it never gets the page-level content
        self.assertNotIn('name="dosage_tmpl_id"', arch)

    def test_page_content_forms_resolve_full_page_content(self):
        # dosage_fields/dosage_administration_fields are nested placeholders
        # inside the dosage_page_content donor content - both levels must resolve
        for model in (
            "ni.medication.request",
            "ni.medication.dispense",
            "ni.medication.statement",
            "ni.medication.suggest.line",
        ):
            with self.subTest(model=model):
                arch = self._get_arch(model)
                self.assertIn('name="dosage_display"', arch)
                self.assertIn('name="meal_offset"', arch)
                self.assertIn('name="route_id"', arch)
                self.assertIn('name="dosage_tmpl_id"', arch)
