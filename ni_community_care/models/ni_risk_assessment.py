import pprint

from odoo import api, fields, models
from odoo.fields import Command


class RiskAssessment(models.Model):
    _name = "ni.risk.assessment"
    _description = "Risk Assessment"
    _rec_name = "occurrence_date"
    _order = "occurrence_date desc"

    @api.model
    def default_get(self, fields):
        res = super(RiskAssessment, self).default_get(fields)
        if "prediction_ids" in fields and "prediction_ids" not in res:
            categ = self.env["ni.service.category"].search([])
            predicts = []
            for cat in categ:
                service = self.env["ni.service"].search(
                    [("category_ids", "in", cat.id)]
                )
                if not service:
                    continue
                predicts += [
                    Command.create({"name": cat.name, "display_type": "line_section"})
                ]
                predicts += [Command.create({"service_id": s.id}) for s in service]
            pprint.pprint(predicts)
            res["prediction_ids"] = predicts
        return res

    patient_id = fields.Many2one(
        "ni.patient",
        "ผู้ถูกประเมิน",
        required=True,
        help="Who does assessment apply to?",
        group_operator="count_distinct",
    )
    patient_type_id = fields.Many2one(
        "ni.patient.type", "ประเภทผู้ถูกประเมิน", required=True
    )
    patient_type_decoration = fields.Selection(related="patient_type_id.decoration")
    performer_uid = fields.Many2one(
        "res.users",
        "ผู้ประเมิน",
        required=True,
        default=lambda self: self.env.user,
        help="Who did assessment?",
    )
    occurrence_date = fields.Datetime(
        "วันที่ประเมิน",
        default=lambda _: fields.Datetime.now(),
        help="When was assessment made?",
    )
    prediction_ids = fields.One2many(
        "ni.risk.assessment.prediction", "assessment_id", "แผนกิจกรรม 5 มิติ"
    )
    planned_all = fields.Boolean(
        "ประเมินครบ 5 มิติ",
        compute="_compute_planned_actual",
        store=True,
        group_operator="bool_or",
    )
    actual_all = fields.Boolean("ปฎิบัติจริงครบ", compute="_compute_planned_actual")
    actual_ratio = fields.Float(
        "ความก้าวหน้าการปฎิบัติ", compute="_compute_planned_actual"
    )
    patient_count = fields.Integer(
        "จำนวนผู้สูงอายุ", compute="_compute_planned_actual", store=True
    )
    actual_count = fields.Integer(
        "จำนวนกิจกรรม", compute="_compute_planned_actual", store=True
    )

    @api.depends("prediction_ids.planned", "prediction_ids.actual")
    def _compute_planned_actual(self):
        for rec in self:
            backlog = rec.prediction_ids.filtered_domain([("planned", "=", True)])
            rec.planned_all = len(backlog.mapped("service_id.category_ids")) == 5
            rec.patient_count = 1 if rec.planned_all else 0
            todo = backlog.filtered_domain([("actual", "=", False)])
            rec.actual_all = not todo and rec.planned_all
            done = backlog.filtered_domain([("actual", "=", True)])
            rec.actual_count = len(done)
            rec.actual_ratio = (
                len(done) / len(backlog) * 100 if backlog and done else 0.0
            )

    @api.onchange("patient_id")
    def _onchange_patient_id(self):
        for rec in self:
            if rec.patient_id:
                rec.patient_type_id = rec.patient_id.type_id

    def action_edit(self):
        self.ensure_one()
        view = {
            "name": self[self._rec_name],
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": self.id,
            "view_type": "form",
            "views": [[False, "form"]],
            "context": self.env.context,
        }
        return view


class RiskAssessmentPrediction(models.Model):
    _name = "ni.risk.assessment.prediction"
    _description = "Prediction"

    sequence = fields.Integer(default=10)
    assessment_id = fields.Many2one(
        "ni.risk.assessment", required=True, ondelete="cascade"
    )
    performer_id = fields.Many2one(related="assessment_id.performer_uid", store=True)
    patient_id = fields.Many2one(
        related="assessment_id.patient_id", store=True, group_operator="count_distinct"
    )
    occurrence_date = fields.Datetime(
        related="assessment_id.occurrence_date", store=True
    )
    outcome_id = fields.Many2one("ni.risk.assessment.outcome", "ผลลัพธ์")
    service_id = fields.Many2one("ni.service", "กิจกรรม 5 มิติ")
    category_id = fields.Many2one(related="service_id.category_id")
    category_decoration = fields.Selection(related="service_id.category_decoration")
    service_name = fields.Char("ชื่อกิจกรรม 5 มิติ", related="service_id.name")
    event_ids = fields.One2many("ni.service.event", "prediction_id")
    event_date = fields.Datetime("วันที่ปฎิบัติจริง", compute="_compute_actual")
    planned = fields.Boolean("การปฎิบัติตามแผน")
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    name = fields.Text(
        string="กิจกรรม",
        compute="_compute_name",
        store=True,
        readonly=False,
        required=True,
        precompute=True,
    )
    actual = fields.Boolean(
        "การปฎิบัติจริง",
        compute="_compute_actual",
        inverse="_inverse_actual",
        group_operator="bool_and",
        store=True,
    )
    rationale = fields.Text(help="Explanation of prediction")

    _sql_constraints = [
        (
            "assessment_service_uniq",
            "unique (assessment_id, service_id)",
            "This assessment_service already exists!",
        ),
    ]

    def _inverse_actual(self):
        for rec in self:
            from dateutil import relativedelta

            if rec.actual:
                start = fields.Datetime.now()
                stop = start + relativedelta.relativedelta(hours=1)
                event = self.env["ni.service.event"].create(
                    {
                        "name": rec.service_id.name,
                        "mode": "single",
                        "service_id": rec.service_id.id,
                        "user_id": self.env.user.id,
                        "start": start,
                        "stop": stop,
                        "prediction_id": rec.id,
                        "patient_id": rec.assessment_id.patient_id.id,
                    }
                )
                rec.event_ids = [fields.Command.link(event.id)]

    @api.depends("service_id")
    def _compute_name(self):
        for rec in self:
            if not rec.service_id:
                continue
            rec.name = rec.service_id.name

    @api.onchange("service_id")
    def _onchange_service_id(self):
        for rec in self:
            if rec.service_id:
                rec.name = rec.service_id.name

    @api.depends("event_ids")
    def _compute_actual(self):
        for rec in self:
            rec.actual = bool(rec.event_ids)
            if rec.actual:
                rec.event_date = rec.event_ids[0].start
            else:
                rec.event_date = None

    def action_event(self):
        self.ensure_one()
        view = self.service_id.create_event()
        ctx = dict(view.get("context"))
        ctx.update(
            {
                "default_prediction_id": self.id,
            }
        )
        view.update(
            {
                "name": "ข้อมูลการปฎิบัติจริง",
                "view_mode": "form",
                "target": "new",
                "context": ctx,
            }
        )
        if self.event_ids:
            view.update({"res_id": self.event_ids[0].id})

        return view


class RiskOutcome(models.Model):
    _name = "ni.risk.assessment.outcome"
    _description = "Risk Assessment Outcome"
    _inherit = "ni.coding"
