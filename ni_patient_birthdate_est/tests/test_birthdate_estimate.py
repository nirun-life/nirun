#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestBirthdateEstimate(TransactionCase):
    def test_partner_older_than_the_module(self):
        """Odoo does not fill a False default: the column of these partners is empty,
        so it cannot be NOT NULL."""
        self.assertFalse(self.env["res.partner"]._fields["birthdate_estimate"].required)
        partner = self.env["res.partner"].create({"name": "Older", "age": 40})
        partner.flush_recordset()
        self.env.cr.execute(
            "UPDATE res_partner SET birthdate_estimate = NULL WHERE id = %s",
            [partner.id],
        )
        partner.invalidate_recordset()
        self.assertFalse(partner.birthdate_estimate)
        partner.name = "Older partner"
        partner.flush_recordset()
