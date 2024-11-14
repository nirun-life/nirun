#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class ObservationType(models.Model):
    _name = "ni.observation.type"
    _description = "Observation Type"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.observation.type", index=True, ondelete="restrict")
    parent_path = fields.Char(index=True, unaccent=False)

    category_id = fields.Many2one("ni.observation.category", index=True)
    min = fields.Float()
    max = fields.Float(default=100.0)
    unit_id = fields.Many2one("uom.uom", index=True, required=False)
    ref_range_ids = fields.One2many(
        "ni.observation.reference.range", "type_id", "Reference Range"
    )
    ref_range_count = fields.Integer(compute="_compute_ref_range_count", store=True)
    value_type = fields.Selection(
        [
            ("char", "Char"),
            ("float", "Float"),
            ("int", "Integer"),
            ("code_id", "Code"),
            ("code_ids", "Multi-Code"),
        ],
        default="float",
    )
    value_code_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_observation_type_value_code_rel",
        "type_id",
        "value_id",
    )
    compare = fields.Selection(
        [
            ("low", "Lower is better"),
            ("high", "Higher is better"),
        ],
        default=None,
    )

    compute = fields.Boolean(
        default=False, help="Type value by compute from other ob type not by user input"
    )

    @api.depends("ref_range_ids")
    def _compute_ref_range_count(self):
        ref_range = self.env["ni.observation.reference.range"].sudo()
        read = ref_range.read_group(
            [("type_id", "in", self.ids)], ["type_id"], ["type_id"]
        )
        data = {res["type_id"][0]: res["type_id_count"] for res in read}
        for rec in self:
            rec.ref_range_count = data.get(rec.id, 0)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    def copy_data(self, default=None):
        default = default or {}
        if "ref_range_ids" not in default and self.ref_range_ids:
            default["ref_range_ids"] = [
                fields.Command.create(r.copy_data({"type_id": None})[0])
                for r in self[0].ref_range_ids
            ]
        return super().copy_data(default)
