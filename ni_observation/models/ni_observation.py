#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.date_utils import get_timedelta


class Observation(models.Model):
    _name = "ni.observation"
    _description = "Observation"
    _inherit = ["ni.workflow.event.mixin"]
    _order = "occurrence DESC,patient_id,sequence"

    @api.model
    def default_get(self, fields):
        res = super(Observation, self).default_get(fields)
        if "patient_id" in fields and "patient_id" not in res:
            if self.env.context.get("active_model") == "ni.observation.sheet":
                res["sheet_id"] = self.env.context["active_id"]
            if self.env.context.get("active_model") == "ni.encounter":
                res["encounter_id"] = self.env.context["active_id"]
            if self.env.context.get("active_model") == "ni.patient":
                res["patient_id"] = self.env.context["active_id"]
        return res

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
    name = fields.Char(compute="_compute_name")

    sheet_id = fields.Many2one(
        "ni.observation.sheet",
        required=False,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    occurrence = fields.Datetime(default=lambda _: fields.datetime.now(), index=True)
    type_id = fields.Many2one("ni.observation.type", required=False, index=True)
    sequence = fields.Integer(default=0)
    category_id = fields.Many2one(
        related="type_id.category_id", readonly=True, store=True, index=True
    )
    value_type = fields.Selection(
        [("char", "Char"), ("float", "Float"), ("int", "Integer"), ("code_id", "Code")],
        default="float",
    )
    value = fields.Char(compute="_compute_value", inverse="_inverse_value", store=True)
    value_float = fields.Float("Value", group_operator="avg")
    value_char = fields.Char("Value")
    value_int = fields.Integer("Value", group_operator="avg")
    value_code_id = fields.Many2one(
        "ni.observation.value.code", "Value", domain="[('type_id', '=', type_id)]"
    )
    unit_id = fields.Many2one(related="type_id.unit_id")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
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

    @api.depends("type_id", "value")
    def _compute_name(self):
        for rec in self:
            rec.name = "{} {}".format(rec.value, rec.unit_id.name or "").strip()

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

    @api.constrains("sheet_id", "occurrence")
    def _check_occurrence(self):
        # effective date must always depend on observation sheet
        for rec in self.filtered(lambda r: r.sheet_id):
            if rec.occurrence != rec.sheet_id.occurrence:
                raise ValidationError(_("Effective date not follow the sheet"))

    @api.onchange("type_id")
    def _onchange_type(self):
        if self.type_id:
            self.update(
                {
                    "interpretation_id": None,
                    "value_type": self.type_id.value_type,
                }
            )
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
            return self.env.ref("ni_observation.interpretation_EX")

    @api.depends(
        "value_type", "value_char", "value_int", "value_float", "value_code_id"
    )
    def _compute_value(self):
        for rec in self:
            if not rec["value_%s" % rec.value_type]:
                continue
            match rec.value_type:
                case "char":
                    rec.value = rec.value_char
                case "int":
                    rec.value = str(rec.value_int)
                case "float":
                    rec.value = str(rec.value_float)
                case "code_id":
                    rec.value = rec.value_code_id.name

    def _inverse_value(self):
        for rec in self:
            if not rec.value:
                continue
            match rec.value_type:
                case "char":
                    rec.value_char = rec.value
                case "int":
                    rec.update(
                        {"value_int": int(rec.value), "value_float": float(rec.value)}
                    )
                    # also write to value_float for use on pivot view
                case "float":
                    rec.value_float = float(rec.value)
                case "code_id":
                    if rec.value.isnumeric():
                        code = self.env["ni.observation.value.code"].browse(
                            int(rec.value)
                        )
                    else:
                        code = self.env["ni.observation.value.code"].search(
                            [
                                ("type_id", "=", rec.type_id.id),
                                ("name", "ilike", rec.value),
                            ],
                            limit=1,
                        )
                    if code:
                        rec.update(
                            {
                                "value": code.name,
                                "value_code_id": code.id,
                            }
                        )
                    else:
                        raise ValidationError(
                            _('Not found match value for "%s"!' % rec.value)
                        )

    @api.constrains("value_float")
    def check_input_range(self):
        for rec in self:
            if not (rec.type_id.min <= rec.value_float <= rec.type_id.max):
                raise ValidationError(
                    _("%s %s is out of acceptable range [%d-%d]")
                    % (rec.type_id.name, rec.value, rec.type_id.min, rec.type_id.max)
                )

    def view_graph(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action_graph")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.patient_id.id,
                "search_default_type_id": self.type_id.id,
                "default_patient_id": self.patient_id.id,
                "search_default_occurrence_hour": True,
            }
        )
        action["context"] = ctx
        return action

    @property
    def _workflow_name(self):
        return self.category_id.name or self._name

    @property
    def _workflow_summary(self):
        return "{} {} {}".format(self.type_id.name, self.value, self.unit_id.name or "")

    @api.constrains("type_id", "value_type")
    def _check_value_type(self):
        for rec in self:
            if rec.type_id and rec.type_id.value_type != rec.value_type:
                raise ValidationError(
                    _("Value type is mismatch! please contact your administrator")
                )

    @api.model
    def garbage_collect(self):
        limit_date = fields.datetime.utcnow() - get_timedelta(1, "day")
        return self.search(
            [
                ("value", "=", False),
                ("write_date", "<", limit_date),
            ]
        ).unlink()

    @api.constrains("display_type", "name", "type_id")
    def _check_name_type(self):
        for rec in self:
            if not rec.display_type and not rec.type_id:
                raise UserError(_("Must specify code type"))
            if rec.display_type and not rec.name:
                raise UserError(_("Must specify section name"))
