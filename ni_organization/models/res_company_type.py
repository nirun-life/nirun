#  Copyright (c) 2023 NSTDA
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CompanyType(models.Model):
    _name = "res.company.type"
    _inherit = "ni.coding"
    _description = "Organization Type"
    _parent_store = True

    parent_id = fields.Many2one("res.company.type", index=True, ondelete="set null")
    parent_path = fields.Char(index=True)

    company_ids = fields.One2many("res.company", "type_id")
    company_count = fields.Integer(compute="_compute_company_count", store=True)

    @api.depends("company_ids")
    def _compute_company_count(self):
        for rec in self:
            rec.company_count = len(rec.company_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )

    def init(self):
        # res.company.type_id is required and defaults to the first type, but
        # the module data is loaded after the tables are created: the companies
        # that exist at install time would stay empty and the NOT NULL
        # constraint would fail. Create the base type of
        # data/res_company_type_data.xml now; the data file still owns its values.
        if self.search([], limit=1):
            return
        system = self.env.ref("ni_coding.system_hl7", raise_if_not_found=False)
        self._load_records(
            [
                {
                    "xml_id": "ni_organization.type_prov",
                    "values": {
                        "name": "Healthcare Provider",
                        "code": "prov",
                        "system_id": system.id if system else False,
                    },
                    "noupdate": True,
                }
            ]
        )
