#  Copyright (c) 2026 NSTDA
"""Patient other addresses use the 'other' partner type (decision D2, #137)."""

from odoo.tests import Form, TransactionCase


class TestPatientAddress(TransactionCase):
    def test_other_address_type_and_domain(self):
        partner = self.env["res.partner"].create({"name": "Address Patient"})
        patient = self.env["ni.patient"].create(
            {"partner_id": partner.id, "identifier": "HN-ADDR-1"}
        )
        view = "ni_patient.res_partner_view_form_address"
        address_form = Form(
            self.env["res.partner"].with_context(
                default_type="other", default_ref=patient.identifier
            ),
            view=view,
        )
        address_form.name = "Home Address"
        address_form.street = "1 Main Road"
        address = address_form.save()
        self.assertEqual(address.type, "other")

        domain = patient._fields["other_address_id"].domain
        self.assertIn("'other'", domain)
        patient.other_address_id = address
        self.assertEqual(patient.other_address_id.street, "1 Main Road")
