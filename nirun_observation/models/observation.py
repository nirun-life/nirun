#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class Observation(models.Model):
    _name = "ni.observation"
    _description = "Observation"
    _inherit = ["ni.workflow.event.mixin"]
    _workflow_occurrence = "effective_date"
    _order = "effective_date DESC,patient_id,sequence"

    sheet_id = fields.Many2one(
        "ni.observation.sheet",
        required=False,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    effective_date = fields.Datetime(default=lambda _: fields.datetime.now())
    type_id = fields.Many2one("ni.observation.type", required=True)
    sequence = fields.Integer(default=0)
    category_id = fields.Many2one(related="type_id.category_id", readonly=True)
    value = fields.Float(group_operator="avg")
    unit = fields.Many2one(related="type_id.unit")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        require=False,
        store=True,
        default=None,
    )
    display_class = fields.Selection(
        [
            ("text", "Text"),
            ("muted", "Muted"),
            ("info", "Info"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        related="interpretation_id.display_class",
        default="text",
    )

    _sql_constraints = [
        (
            "type__uniq",
            "unique (sheet_id, type_id)",
            "Duplication observation type!",
        ),
    ]

    def init(self):
        tools.create_index(
            self._cr,
            "ni_observation__patient__ob_type__idx",
            self._table,
            ["patient_id", "type_id"],
        )
        tools.create_index(
            self._cr,
            "ni_observation__encounter__ob_type__idx",
            self._table,
            ["encounter_id", "type_id"],
        )

    @api.constrains("sheet_id", "effective_date")
    def _check_effective_date(self):
        # effective date must always depend on observation sheet
        for rec in self.filtered(lambda r: r.sheet_id):
            if rec.effective_date != rec.sheet_id.effective_date:
                raise ValidationError(_("Effective date not follow the sheet"))

    @api.onchange("type_id")
    def _onchange_type(self):
        self.update({"interpretation_id": None})
        self._compute_interpretation()

    @api.depends("value")
    def _compute_interpretation(self):
        for rec in self:
            rec.interpretation_id = rec._interpretation_for()

    def _interpretation_for(self):
        if self.type_id.ref_range_count == 0:
            return None

        ranges = self.env["ni.observation.reference.range"].search(
            [
                ("type_id", "=", self.type_id.id),
                ("low", "<=", self.value),
                ("high", ">", self.value),
            ],
            limit=1,
        )
        if ranges:
            return ranges[0].interpretation_id
        else:
            return self.env.ref("nirun_observation.interpretation_EX")

    @api.constrains("value")
    def check_input_range(self):
        for rec in self:
            if not (rec.type_id.min <= rec.value <= rec.type_id.max):
                raise ValidationError(
                    _("%s %s is out of acceptable range [%d-%d]")
                    % (rec.type_id.name, rec.value, rec.type_id.min, rec.type_id.max)
                )

    def view_graph(self):
        action_rec = self.env.ref("nirun_observation.ob_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.patient_id.id,
                "search_default_type_id": self.type_id.id,
                "default_patient_id": self.patient_id.id,
            }
        )
        action["context"] = ctx
        return action

    @property
    def _workflow_name(self):
        return self.category_id.name or self._name

    @property
    def _workflow_summary(self):
        return "{} {} {}".format(self.type_id.name, self.value, self.unit.name)
