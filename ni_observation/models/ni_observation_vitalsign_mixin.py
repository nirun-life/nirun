#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError

VITALSIGN_FIELDS = [
    "bp_s",
    "bp_d",
    "heart_rate",
    "respiratory_rate",
    "body_temp",
    "body_weight",
    "body_height",
    "bmi",
    "fbs",
    "dtx",
    "oxygen_sat",
]

REPLACE_FIELDS = {
    "bp_s": "bp",
    "bp_d": "bp",
}


class ObservationVitalsignMixin(models.AbstractModel):
    _name = "ni.observation.vitalsign.mixin"
    _description = "Vital Sign Mixin"

    vital_sign = fields.Text("Vital Sign", compute="_compute_vital_sign", store=True)
    bp = fields.Char(
        "Blood Pressure", help="Blood Pressure", compute="_compute_bp", store=True
    )
    bp_s = fields.Float(
        "Systolic Blood Pressure", digits=(4, 1), help="Systolic Blood Pressure (mmHg)"
    )
    bp_d = fields.Float(
        "Diastolic Blood Pressure",
        digits=(4, 1),
        help="Diastolic Blood Pressure (mmHg)",
    )
    heart_rate = fields.Integer("Heart Rate (Pulse)", help="Heart Rate | Pulse (/min)")
    respiratory_rate = fields.Integer(
        "Respiratory Rate", help="Respiratory Rate (/min)"
    )
    body_temp = fields.Float(
        "Body Temperature", digits=(3, 1), help="Body Temperature (°C)"
    )
    body_weight = fields.Float("Body Weight", digits=(4, 1), help="Body Weight (kg)")
    body_height = fields.Float("Body Height", digits=(4, 1), help="Body Height (cm)")
    bmi = fields.Float(
        "Body Mass Index",
        digits=(3, 1),
        help="Body Mass Index (kg/m²) - weight(kg) / height(m)²",
        compute="_compute_bmi",
        store=True,
    )
    glucose_type = fields.Selection(
        [("fbs", "FBS"), ("dtx", "DTX")],
        default="dtx",
        required=True,
    )
    fbs = fields.Float(
        "Fasting Blood Sugar", digits=(3, 1), help="Fasting Blood Sugar (mg/dl)"
    )
    dtx = fields.Float("Dextrostix", digits=(3, 1), help="Dextrostix (mg/dl)")
    oxygen_sat = fields.Float("Oxygen Saturation", digits=(4, 1), help="Oxygen sat (%)")
    pain_score = fields.Integer(
        "ความเจ็บปวด (0-10)",
        default="0",
        compute="_compute_pain_score",
        inverse="_inverse_pain_score",
        copy=False,
    )
    pain_score_enum = fields.Selection(
        [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("6", "6"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
        "ความเจ็บปวด",
        default="0",
        copy=False,
    )
    pain_area = fields.Char("บริเวณที่เจ็บปวด")

    @api.depends("pain_score_enum")
    def _compute_pain_score(self):
        for rec in self:
            rec.pain_score = int(rec.pain_score_enum)

    def _inverse_pain_score(self):
        for rec in self:
            if 0 <= rec.pain_score <= 10:
                rec.pain_score_enum = str(rec.pain_score)

    @api.depends(*VITALSIGN_FIELDS)
    def _compute_vital_sign(self):
        for rec in self:
            # First we get only field that have value
            vs_f = [f for f in VITALSIGN_FIELDS if rec[f]]
            # Replace it if present in REPLACE_FIELD
            vs_rp = [f if f not in REPLACE_FIELDS else REPLACE_FIELDS[f] for f in vs_f]
            # Then remove None or Duplicate field that may occurred after replace field
            res = []
            [res.append(v) for v in vs_rp if v and v not in res]
            vs = rec._short_info(res)
            rec.vital_sign = "  /  ".join(vs) if vs else None

    def _short_info(self, vs_fields):
        if not vs_fields:
            return []
        self.ensure_one()
        f = [f.replace("_", "-") for f in vs_fields]
        code = self.env["ni.observation.type"].search([("code", "in", f)])
        return [
            "{} = {}{}".format(
                c.abbr or c.code or c.name,
                self[c.code.replace("-", "_")],
                c.unit_id.name,
            )
            for c in code
        ]

    @api.depends("bp_d")
    def _compute_bp(self):
        for rec in self:
            if rec.bp_s and rec.bp_d:
                rec.bp = "{} / {}".format(rec.bp_s, rec.bp_d)

    @api.depends("body_height", "body_weight")
    def _compute_bmi(self):
        for rec in self:
            if rec.body_height and rec.body_weight:
                body_height_m = rec.body_height * 0.01
                rec.bmi = round(rec.body_weight / pow(body_height_m, 2), 1)
            else:
                rec.bmi = 0.0

    @api.constrains("pain_score", "pain_area")
    def _check_pain_score(self):
        for rec in self:
            if rec.pain_area and not any([rec.pain_score, rec.pain_score_enum != "0"]):
                raise UserError(_("กรุณาระบุระดับความเจ็บปวด"))
