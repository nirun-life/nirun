#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    spouse_id = fields.Many2one(
        "res.partner",
        domain=[("is_company", "=", False)],
        tracking=True,
        ondelete="set null",
    )
    spouse_name = fields.Char(compute="_compute_spouse_name")
    child_ids = fields.Many2many(
        "res.partner",
        "ni_patient_child_rel",
        string="Children",
        domain=[("is_company", "=", False)],
        tracking=True,
    )
    father_id = fields.Many2one(
        "res.partner",
        domain=[("is_company", "=", False)],
        tracking=True,
        ondelete="set null",
    )
    father_name = fields.Char(compute="_compute_father_name")
    mother_id = fields.Many2one(
        "res.partner",
        domain=[("is_company", "=", False)],
        tracking=True,
        ondelete="set null",
    )
    mother_name = fields.Char(compute="_compute_mother_name")

    @api.onchange("child_ids")
    def onchange_child_ids(self):
        if self.children_count < len(self.child_ids):
            self.children_count = len(self.child_ids)

    @api.depends("spouse_name")
    def _compute_spouse_name(self):
        for rec in self:
            if rec.spouse_id:
                rec.spouse_name = rec.spouse_id.name
            else:
                rec.spouse_name = None

    @api.depends("mother_id")
    def _compute_mother_name(self):
        for rec in self:
            if rec.mother_id:
                rec.mother_name = rec.mother_id.name
            else:
                rec.mother_name = None

    @api.depends("father_id")
    def _compute_father_name(self):
        for rec in self:
            if rec.father_id:
                rec.father_name = rec.father_id.name
            else:
                rec.father_name = None
