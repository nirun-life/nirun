#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Medication(models.Model):
    _name = "ni.medication"
    _description = "Medication"
    _inherit = ["mail.thread"]
    _inherits = {"product.template": "product_tmpl_id"}

    product_tmpl_id = fields.Many2one(
        "product.template",
        "Product Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
        required=True,
        tracking=True,
    )
    manufacturer_name = fields.Char(index=True, tracking=True)
    manufacturer_id = fields.Many2one(
        "res.partner", domain=[("is_company", "=", True)], tracking=True
    )
    form = fields.Many2one("ni.medication.form", index=True, tracking=True)
    ingredient = fields.Char(
        "Ingredient",
        compute="_compute_ingredient",
        store=True,
        index=True,
        tracking=True,
    )
    ingredient_ids = fields.One2many(
        "ni.medication.ingredient", "medication_id", "Ingredient List", tracking=True
    )
    amount = fields.Char(
        compute="_compute_amount",
        store=True,
        index=True,
        help="Amount of drug in package",
        tracking=True,
    )
    amount_numerator = fields.Float(tracking=True)
    amount_numerator_unit = fields.Many2one("ni.quantity.unit", tracking=True)
    amount_denominator = fields.Float(default=1.0, tracking=True)
    amount_denominator_unit = fields.Many2one("ni.quantity.unit", tracking=True)

    statement_ids = fields.One2many("ni.medication.statement", "medication_id")
    patient_ids = fields.Many2many(
        "ni.patient",
        "ni_medication_patient_rel",
        compute="_compute_patient",
        store=True,
        sudo_compute=True,
    )
    patient_count = fields.Integer(
        compute="_compute_patient", store=True, sudo_compute=True
    )
    dosage_ids = fields.Many2many(
        "ni.medication.dosage",
        "ni_medication_dosage_rel",
        "medication_id",
        "dosage_id",
        help="dosages available for this medication",
    )

    @api.depends("statement_ids", "statement_ids.state")
    def _compute_patient(self):
        statement = self.env["ni.medication.statement"].search(
            [
                ("medication_id", "in", self.ids),
                ("state", "=", "active"),
                ("company_id", "in", self.env.company.ids),
            ]
        )
        for rec in self:
            statement_active_ids = statement.filtered(lambda s: s.medication_id == rec)
            rec.patient_ids = statement_active_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("manufacturer_name", operator, name),
                ("ingredient", operator, name),
            ]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    @api.depends("ingredient_ids")
    def _compute_ingredient(self):
        for rec in self:
            if rec.ingredient_ids:
                ingredient = [ing.display_name for ing in rec.ingredient_ids]
                rec.ingredient = " + ".join(ingredient)

    @api.depends(
        "amount_numerator",
        "amount_numerator_unit",
        "amount_denominator",
        "amount_denominator_unit",
    )
    def _compute_amount(self):
        for rec in self:
            res = []
            if rec.amount_numerator and rec.amount_numerator_unit:
                res.append(
                    "{} {}".format(rec.amount_numerator, rec.amount_numerator_unit.name)
                )

            if rec.amount_denominator_unit:
                denominator = []
                if rec.amount_denominator > 1 or not rec.amount_numerator:
                    denominator.append(str(rec.amount_denominator))
                denominator.append(rec.amount_denominator_unit.name)
                res.append(" ".join(denominator))

            rec.amount = " / ".join(res) if res else None

    @api.onchange("manufacturer_id")
    def _onchange_manufacturer_id(self):
        for rec in self:
            if rec.manufacturer_id:
                rec.manufacturer_name = rec.manufacturer_id.name

    def open_statement(self):
        ctx = dict(self._context)
        ctx.update(
            {
                "search_default_medication_id": self.id,
                "search_default_state_active": True,
                "search_default_group_by_location": True,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_medication", "medication_statement_action"
        )
        return dict(action, context=ctx)
