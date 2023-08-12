#  Copyright (c) 2023 NSTDA

from lxml import etree

from odoo import api, fields, models


class BloodGroupMixin(models.AbstractModel):
    _name = "ni.observation.bloodgroup.mixin"
    _description = "Blood Group Mixin"

    blood_abo = fields.Many2one("ni.observation.value.code", "ABO")
    blood_rh = fields.Many2one("ni.observation.value.code", "RH")
    blood_group = fields.Char(compute="_compute_blood_group")

    @api.depends("blood_abo", "blood_rh")
    def _compute_blood_group(self):
        for rec in self:
            bg = rec.blood_abo.name or None
            if bg and rec.blood_rh:
                bg = "{}{}".format(bg, rec.blood_rh.abbr)
            rec.blood_group = bg

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        Alternative way to enforce domain filter with external id reference
        """
        res = super(BloodGroupMixin, self).get_view(view_id, view_type, **options)
        if view_type == "form":
            doc = etree.XML(res["arch"])
            abo_field = doc.xpath("//field[@name='blood_abo']")
            if abo_field:
                type_abo = self.env.ref("ni_observation.type_blood_abo")
                if type_abo.exists():
                    abo_field[0].attrib["domain"] = (
                        "[('type_id', '=', %s)]" % type_abo.id
                    )

            rh_field = doc.xpath("//field[@name='blood_rh']")
            if rh_field:
                rh_field[0].attrib["domain"] = "[('id', 'in', ['%d', '%d'])]" % (
                    self.env.ref("ni_observation.code_positive").id,
                    self.env.ref("ni_observation.code_negative").id,
                )
            res["arch"] = etree.tostring(doc)
        return res
