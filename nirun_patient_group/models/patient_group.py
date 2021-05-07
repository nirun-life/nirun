#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class PatientGroup(models.Model):
    _name = "ni.patient.group"
    _description = "Patient Group"
    _inherit = ["coding.base"]
    _order = "display_name"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=False,
        index=True,
        default=lambda self: self.env.company,
    )
    display_name = fields.Char(compute="_compute_display_name", store=True, index=True)
    is_section = fields.Boolean(
        default=False, help="Is this group designed to be parent of other group"
    )
    parent_id = fields.Many2one(
        "ni.patient.group", "Section", domain="[('is_section', '=', True)]"
    )
    child_ids = fields.One2many("ni.patient.group", "parent_id")

    select = fields.Selection(
        [("single", "Single"), ("multi", "multi")],
        default="multi",
        help="Mode of select in groups with same parent",
    )
    user_select = fields.Boolean(
        default=True,
        help="Should user be able to select this group or system "
        "assign patient to group by some condition",
    )
    patient_ids = fields.Many2many(
        "ni.patient",
        "ni_patient_group_rel",
        "group_id",
        "patient_id",
        string="Members",
    )
    patient_count = fields.Integer(compute="_compute_patient_count", store=True)

    def name_get(self):
        return [(rec.id, rec.display_name) for rec in self]

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name or ""
            if rec.parent_id:
                name = "{} , {}".format(rec.parent_id.name, rec.name)
            rec.display_name = name

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for rec in self:
            if rec.parent_id:
                rec.select = rec.parent_id.select

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                _("Error! You cannot create recursive locations.")
            )

    @api.depends("is_section")
    @api.onchange("is_section")
    def _onchange_is_section(self):
        for rec in self:
            if rec.is_section:
                rec.user_select = False
                rec.parent_id = None

    def write(self, vals):
        # make section group inactive to hide from SearchPanel
        section = vals.get("is_section")
        if section:
            vals.update({"active": False})
        return super().write(vals)

    def action_patient(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update({"search_default_group_ids": [self.id]})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_patient", "patient_action"
        )
        return dict(action, context=ctx)
