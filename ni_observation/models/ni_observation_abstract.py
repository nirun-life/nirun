#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ObservationAbstract(models.AbstractModel):
    _name = "ni.observation.abstract"
    _description = "Observation Abstract"

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
    name = fields.Char(compute="_compute_name")
    title = fields.Char()

    occurrence = fields.Datetime(default=lambda _: fields.datetime.now(), index=True)
    effective_date = fields.Datetime(
        related="occurrence", readonly=False, help="Alias for occurrence"
    )
    type_id = fields.Many2one("ni.observation.type", required=False, index=True)
    code_id = fields.Many2one(
        related="type_id", store=True, readonly=False, help="Alias for type_id"
    )
    code = fields.Char(compute="_compute_code", inverse="_inverse_code")

    @api.model_create_multi
    def create(self, vals_list):
        ob_types = self.env["ni.observation.type"].sudo()
        for vals in vals_list:
            if "type_id" not in vals and "code" in vals and vals["code"]:
                ob_type = ob_types.search([("code", "=", vals["code"])])
                if ob_type:
                    vals["type_id"] = ob_type.id
                    vals["value_type"] = ob_type.value_type

        return super().create(vals_list)

    @api.depends("type_id")
    def _compute_code(self):
        for rec in self:
            rec.code = rec.type_id.code if rec.type_id else None

    def _inverse_code(self):
        ob_types = self.env["ni.observation.type"].sudo()
        for rec in self.filtered("code"):
            ob_type = ob_types.search([("code", "=", rec.code)])
            if ob_type:
                rec.type_id = ob_type
                rec.value_type = ob_type.value_type

    sequence = fields.Integer(default=0)
    category_id = fields.Many2one(
        related="type_id.category_id", readonly=True, store=True, index=True
    )
    color = fields.Integer(related="type_id.category_id.color")
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
    value = fields.Char(compute="_compute_value", inverse="_inverse_value", store=True)
    value_float = fields.Float("Value", group_operator="avg")
    value_char = fields.Char("Value")
    value_int = fields.Integer("Value", group_operator="avg")
    value_code_id = fields.Many2one(
        "ni.observation.value.code", "Value", domain="[('type_ids', '=', type_id)]"
    )
    value_code_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_observation_value_code_rel",
        "observation_id",
        "value_id",
        domain="[('type_ids', '=', type_id)]",
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
    compare = fields.Selection(
        [
            ("lt", "Lesser"),
            ("eq", "Equal"),
            ("gt", "Greater"),
        ],
        store=True,
        default=None,
        help="Compare this observation value to previous observation",
    )
    compare_interpret = fields.Selection(
        [("neutral", "Neutral"), ("better", "Better"), ("worsen", "Worsen")],
        store=True,
        default=None,
    )
    is_problem = fields.Boolean(related="interpretation_id.is_problem", store=True)
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

    @api.depends("type_id", "value", "display_type", "title")
    def _compute_name(self):
        for rec in self:
            if not rec.display_type:
                rec.name = "{} {}".format(rec.value, rec.unit_id.name or "").strip()
            else:
                rec.name = rec.title

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

        ranges = self.env["ni.observation.reference.range"].range_for(
            self.type_id.id, self.patient_id.age, self.patient_id.gender
        )
        ref = None
        if self.value_type == "int":
            ref = ranges.interpret(self.value_int)
        elif self.value_type == "float":
            ref = ranges.interpret(self.value_float)
        if ref:
            return ref.interpretation_id
        else:
            return self.env.ref("ni_observation.interpretation_EX")

    @api.depends(
        "type_id",
        "value_type",
        "value_char",
        "value_int",
        "value_float",
        "value_code_id",
        "value_code_ids",
    )
    def _compute_value(self):
        for rec in self:
            if not rec.type_id or (
                not rec["value_%s" % rec.type_id.value_type]
                and not rec.type_id.keep_falsy
            ):
                rec.value = None
                continue
            match rec.type_id.value_type:
                case "char":
                    rec.value = rec.value_char
                case "int":
                    rec.value = str(rec.value_int)
                case "float":
                    rec.value = str(rec.value_float)
                case "code_id":
                    rec.value = rec.value_code_id.name
                case "code_ids":
                    rec.value = ", ".join(rec.value_code_ids.mapped("name"))

    def _inverse_value(self):
        for rec in self:
            if not rec.value:
                continue
            match rec.type_id.value_type:
                case "char":
                    rec.value_char = rec.value
                case "int":
                    rec.update(
                        {
                            "value_int": int(float(rec.value)),
                            "value_float": float(rec.value),
                        }
                    )
                    # also write to value_float for use on pivot view
                case "float":
                    rec.value_float = float(rec.value)
                case "code_id":
                    code = self._value_code_mapping(rec.type_id, rec.value.strip())
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
                case "code_ids":
                    values = rec.value.split(",")
                    codes = []
                    for val in values:
                        _code = self._value_code_mapping(rec.type_id, val.strip())
                        if _code:
                            codes.append(_code)
                    if codes:
                        rec.value = ", ".join([code.name for code in codes])
                        rec.value_code_ids = [
                            fields.Command.link(code.id) for code in codes
                        ]

    @api.model
    def _value_code_mapping(self, type_id, value):
        if value.isnumeric():
            code = self.env["ni.observation.value.code"].browse(int(value))
        else:
            code = self.env["ni.observation.value.code"].search(
                [
                    ("type_ids", "=", type_id.id),
                    "|",
                    ("name", "ilike", value),
                    ("code", "=", value),
                ],
                limit=1,
            )
        return code

    @api.constrains("value_float")
    def check_input_range(self):
        for rec in self:
            if not (rec.type_id.min <= rec.value_float <= rec.type_id.max):
                raise ValidationError(
                    _("%s %s is out of acceptable range [%d-%d]")
                    % (rec.type_id.name, rec.value, rec.type_id.min, rec.type_id.max)
                )

    @api.constrains("type_id", "value_type")
    def _check_value_type(self):
        for rec in self:
            if rec.type_id and rec.type_id.value_type != rec.value_type:
                rec.value_type = rec.type_id.value_type

    @api.constrains("display_type", "title", "type_id")
    def _check_name_type(self):
        for rec in self:
            if not rec.display_type and not rec.type_id:
                raise UserError(_("Must specify code type"))
            if rec.display_type and not rec.title:
                raise UserError(_("Must specify section name"))
