#  Copyright (c) 2023 NSTDA

from lxml import etree

from odoo import api, fields, models

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
    "abo",
    "rh",
]

REPLACE_FIELDS = {
    "bp_s": "bp",
    "bp_d": "bp",
    "abo": None,
    "rh": None,
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
        default="fbs",
        required=True,
    )
    fbs = fields.Float(
        "Fasting Blood Sugar", digits=(3, 1), help="Fasting Blood Sugar (mg/dl)"
    )
    dtx = fields.Float("Dextrostix", digits=(3, 1), help="Dextrostix (mg/dl)")
    oxygen_sat = fields.Float("Oxygen Saturation", digits=(4, 1), help="Oxygen sat (%)")
    abo = fields.Many2one("ni.observation.value.code")
    rh = fields.Many2one("ni.observation.value.code")

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        Alternative way to enforce domain filter with external id reference
        """
        res = super(ObservationVitalsignMixin, self).get_view(
            view_id, view_type, **options
        )

        if view_type == "form":
            doc = etree.XML(res["arch"])
            abo_field = doc.xpath("//field[@name='abo']")
            if abo_field:
                type_abo = self.env.ref("ni_observation.type_blood_abo")
                if type_abo.exists():
                    abo_field[0].attrib["domain"] = (
                        "[('type_id', '=', %s)]" % type_abo.id
                    )

            rh_field = doc.xpath("//field[@name='rh']")
            if rh_field:
                pos = self.env.ref("ni_observation.code_positive")
                neg = self.env.ref("ni_observation.code_negative")
                if pos.exists() and neg.exists():
                    rh_field[0].attrib["domain"] = "[('id', 'in', ['%d', '%d'])]" % (
                        pos.id,
                        neg.id,
                    )

            res["arch"] = etree.tostring(doc)
        return res

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
