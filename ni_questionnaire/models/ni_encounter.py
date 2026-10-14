#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    survey_id = fields.Many2one(related="class_id.survey_id")
    response_id = fields.Many2one(
        "survey.user_input", store=True, groups="survey.group_survey_user"
    )

    response_ids = fields.One2many(
        "survey.user_input",
        "encounter_id",
        domain=[("state", "=", "done")],
        help="Completed survey's response",
    )

    response_count = fields.Integer(
        compute="_compute_response_count",
        compute_sudo=True,
    )

    @api.depends("response_ids")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)

    response_filter = fields.Selection(
        [
            ("encounter", "This Encounter"),
            ("patient", "All"),
        ],
        default="patient",
        required=True,
    )

    patient_response_latest_ids = fields.One2many(
        related="patient_ids.response_latest_ids"
    )

    response_latest_ids = fields.One2many(
        "ni.encounter.survey_latest", "encounter_id", "Latest Surveys"
    )

    response_latest_id = fields.Many2one(
        "ni.encounter.survey_latest",
        "Latest Survey",
        compute="_compute_response",
        store=True,
        compute_sudo=True,
    )
    response_latest_grade_id = fields.Many2one(
        "survey.grade",
        "Latest Survey Grade",
        compute="_compute_response",
        store=True,
        compute_sudo=True,
        index=True,
    )
    response_latest_date = fields.Datetime(
        "Latest Survey Date", compute="_compute_response", store=True, compute_sudo=True
    )

    @api.depends(
        "survey_id",
        "response_ids.state",
        "response_ids.survey_id",
        "response_ids.grade_id",
    )
    def _compute_response(self):
        # Read the responses through the ORM, not the ni.encounter.survey_latest SQL
        # view: stored computes run before pending writes reach the database, so the
        # view would not see a response that was just completed. The view's ids are
        # the responses' ids.
        latest_view = self.env["ni.encounter.survey_latest"]
        w_survey = self.filtered_domain([("survey_id", "!=", False)])
        for rec in w_survey:
            latest = rec.response_ids.filtered(
                lambda r, survey=rec.survey_id: r.state == "done"
                and r.survey_id == survey
            ).sorted(lambda r: (r.create_date, r.id), reverse=True)[:1]
            rec.response_latest_id = latest_view.browse(latest.id)
            rec.response_latest_grade_id = latest.grade_id
            rec.response_latest_date = latest.create_date
        for rec in self - w_survey:
            rec.response_latest_id = False
            rec.response_latest_grade_id = False
            rec.response_latest_date = False

    def action_survey_user_input_completed(self):
        action = self.patient_id.action_survey_user_input_completed()
        if self.state in ["draft", "planned", "in-progress"]:
            action["context"].update(
                {
                    "default_subject_ni_encounter": self.id,
                }
            )
        return action

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            # The clinician fills it in for the patient, like the survey_subject
            # wizard: with partner=<patient>, core rejects the clinician's session
            # as "answer_wrong_user". Created as superuser, as the wizard does:
            # core only lets a survey officer create answers on their own surveys.
            response = self.survey_id.sudo()._create_answer(
                user=self.env.user,
                subject_model="ni.encounter",
                subject_id=self.id,
                patient_id=self.patient_id.id,
                encounter_id=self.id,
            )
            self.response_id = response.id
        else:
            response = self.response_id
        # open the survey on this response (its access token goes in the URL)
        action = self.survey_id.action_start_survey(answer=response)
        action.update({"target": "new"})
        return action

    def action_print_survey(self):
        """If response is available then print this response otherwise print
        survey form (print template of the survey)"""
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_survey()
        else:
            action = self.survey_id.action_print_survey(answer=self.response_id)
            action.update({"target": "new"})
            return action

    def action_survey_subject(self):
        action_rec = self.env.ref("survey_subject.survey_subject_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_subject_ni_encounter": self.id,
                "default_subject_ni_patient": self.patient_id.id,
            }
        )
        action["context"] = ctx
        return action
