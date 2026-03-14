#  Copyright (c) 2023 NSTDA


from odoo import api, fields, models


class BloodGroupMixin(models.AbstractModel):
    _name = "ni.observation.bloodgroup.mixin"
    _description = "Blood Group Mixin"

    blood_abo = fields.Many2one(
        "ni.observation.value.code",
        "ABO",
        domain=lambda self: [
            ("type_ids", "=", self.env.ref("ni_observation.type_blood_abo").id),
        ],
    )
    blood_rh = fields.Many2one(
        "ni.observation.value.code",
        "RH",
        domain=lambda self: [
            ("type_ids", "=", self.env.ref("ni_observation.type_blood_rh").id)
        ],
    )
    blood_group = fields.Char(compute="_compute_blood_group")

    @api.depends("blood_abo", "blood_rh")
    def _compute_blood_group(self):
        for rec in self:
            bg = rec.blood_abo.name or None
            if bg and rec.blood_rh:
                bg = "{}{}".format(bg, rec.blood_rh.abbr)
            rec.blood_group = bg
