import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.date_utils import end_of, relativedelta, start_of
from odoo.tools.safe_eval import safe_eval, test_python_expr

_logger = logging.getLogger(__name__)


class Demographic(models.Model):
    _name = "ni.report.demographic"
    _description = "Demographic"
    _inherit = ["period.mixin", "ir.sequence.mixin"]
    _order = "period_end DESC"

    def _get_default_period_start(self):
        today = fields.Date.context_today(self)
        return start_of(today, "month")

    def _get_default_period_end(self):
        today = fields.Date.context_today(self)
        return end_of(today, "month")

    name = fields.Char("Report No.", default="new")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    line_ids = fields.One2many("ni.report.demographic.line", "report_id", "detail")

    period_start = fields.Date(default=lambda self: self._get_default_period_start())
    period_end = fields.Date(default=lambda self: self._get_default_period_end())

    state = fields.Selection(
        [("draft", "Draft"), ("active", "Published")], default="draft", required=True
    )
    note = fields.Text()

    def action_confirm(self):
        self.check_company_period()
        self.write({"state": "active"})

    @api.constrains("company_id", "period_start", "period_end")
    def check_company_period(self):
        for rec in self:
            duplicate = rec.search_intercept(
                [("company_id", "=", rec.company_id.id), ("state", "=", "active")]
            )
            if duplicate:
                r = duplicate[0]
                raise ValidationError(
                    _(
                        "{} already have report for given time!"
                        "\n\n\t{} ({}->{})".format(
                            rec.company_id.name, r.name, r.period_start, r.period_end
                        )
                    )
                )

    @api.model_create_single
    def create(self, vals):
        if "line_ids" not in vals:
            codes = self.env["ni.report.demographic.code"].search([])
            vals["line_ids"] = [(0, 0, {"code_id": c.id}) for c in codes]

        report = super(Demographic, self).create(vals)
        if report.line_ids:
            report.line_ids.action_exec_code()
        return report

    @api.model
    def cron_report_last_month(self):
        last_month = fields.date.today() - relativedelta(months=1)
        self.monthly_report(start_of(last_month, "month"), end_of(last_month, "month"))

    @api.model
    def cron_report_this_month(self):
        today = fields.date.today()
        self.monthly_report(start_of(today, "month"), end_of(today, "month"))

    @api.model
    def monthly_report(self, start=None, end=None):
        if not start:
            start = start_of(fields.date.today(), "month")
        if not end:
            end = end_of(start, "month")
        _logger.info("Generating %s (%s -> %s)...", self._description, start, end)
        vals = {
            "name": f"DR-{start.year}{start.month}",
            "period_start": start,
            "period_end": end,
            "note": "Auto-generate report",
            "state": "active",
        }

        for company in self.env["res.company"].sudo().search([]):
            vals["company_id"] = company.id
            report = self.create(vals)
            _logger.info(
                "Generated report %s(id=%d) for %s(id=%d)",
                report.name,
                report.id,
                company.name,
                company.id,
            )
        return True


class DemographicLine(models.Model):
    _name = "ni.report.demographic.line"
    _description = "Demographic Detail"

    company_id = fields.Many2one(related="report_id.company_id", store=True)
    report_id = fields.Many2one(
        "ni.report.demographic", required=True, index=True, ondelete="cascade"
    )
    code_id = fields.Many2one(
        "ni.report.demographic.code",
        "Topic",
        required=True,
        index=True,
        ondelete="restrict",
    )
    code_parent_id = fields.Many2one(
        related="code_id.parent_id", string="Subject", store=True, index=True
    )
    date = fields.Date(related="report_id.period_end", store=True)

    total = fields.Integer()
    male = fields.Integer()
    female = fields.Integer()
    other = fields.Integer(compute="_compute_other", store=True)

    state = fields.Selection(related="report_id.state")

    _sql_constraints = [
        (
            "report_code__uniq",
            "unique (report_id, code_id)",
            "Duplication summary subject type!",
        ),
    ]

    @api.depends("total", "male", "female")
    def _compute_other(self):
        for rec in self:
            rec.other = rec.total - (rec.male + rec.female)

    def action_exec_code(self):
        for line in self:
            line.code_id.action_exec(line)


class DemographicCode(models.Model):
    _name = "ni.report.demographic.code"
    _description = "Demographic Topic"
    _inherit = ["coding.base"]
    _order = "sequence"
    _parent_store = True

    name = fields.Char("Topic")
    display_name = fields.Char(
        compute="_compute_display_name", string="Topic", store=True, index=True
    )
    parent_id = fields.Many2one(
        "ni.report.demographic.code", "Subject", domain="[('parent_id', '=', False)]"
    )
    company_ids = fields.Many2many(
        "res.company",
        help="Companies can use this topic, when left empty the topic is public",
    )
    parent_path = fields.Char(index=True)
    type = fields.Selection(
        [("read_group", "Group"), ("search", "Search")],
        default="read_group",
        help="""'Group' use GROUP BY gender,
        Search slower than Group by but provide mode flexibility""",
    )
    res_model = fields.Char(
        "Model",
        compute="_compute_res_model",
        required=True,
        inverse="_inverse_res_model",
    )
    res_model_id = fields.Many2one("ir.model", "Model", required=True)
    domain = fields.Text(default="[]", help="Use to query on database")
    filter = fields.Text(
        default="[]",
        help="domain pattern for filter retrieved records with python "
        "(after 'domain' was used)",
    )

    @api.onchange("res_model_id")
    @api.depends("res_model_id")
    def _compute_res_model(self):
        for rec in self:
            rec.res_model = rec.res_model_id.model if rec.res_model_id else False

    def _inverse_res_model(self):
        for rec in self:
            if rec.res_model and not rec.res_model_id:
                model = self.env["ir.model"].search(
                    [("model", "=", rec.res_model)], limit=1
                )
                rec.res_model_id = model if model else False

    @api.constrains("domain")
    def check_domain(self):
        for code in self.sudo().filtered("domain"):
            msg = test_python_expr(expr=code.domain.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.constrains("filter")
    def check_filter(self):
        for code in self.sudo().filtered("domain"):
            msg = test_python_expr(expr=code.filter.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _compute_display_name(self):
        for rec in self:
            names = []
            current = rec
            while current:
                names.append(current.name)
                current = current.parent_id
            rec.display_name = ", ".join(reversed(names))

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    def eval_domain(self, eval_context=None):
        self.ensure_one()
        if not self.domain or self.domain == "[]":
            return []
        return safe_eval(self.domain.strip(), eval_context, nocopy=True)

    def eval_filter(self, eval_context=None):
        self.ensure_one()
        if not self.filter or self.filter == "[]":
            return []
        return safe_eval(self.filter.strip(), eval_context, nocopy=True)

    def action_exec(self, line: DemographicLine = None):
        self.ensure_one()
        subject = self
        if not line:
            raise ValidationError(_("Must have demographic line"))

        eval_context = {"report": line.report_id, "line": line}
        domain = subject.eval_domain(eval_context)
        domain.append(("company_id", "=", line.company_id.id))
        model = self.env[subject.res_model].sudo()

        if subject.type == "read_group":
            group_by = model.read_group(domain, ["gender"], ["gender"])
            result = {group["gender"]: group["gender_count"] for group in group_by}
            other = result.get("other", 0) + result.get(False, 0)
            male = result.get("male", 0)
            female = result.get("female", 0)
            line.update(
                {
                    "total": male + female + other,
                    "male": male,
                    "female": female,
                    "other": other,
                }
            )
        elif subject.type == "search":
            res = model.search(domain)
            if self.filter and self.filter != "[]":
                res = res.filtered_domain(subject.eval_filter(eval_context))
            line.update(
                {
                    "total": len(res),
                    "male": sum(map(lambda r: r.gender == "male", res)),
                    "female": sum(map(lambda r: r.gender == "female", res)),
                    "other": sum(map(lambda r: r.gender in ["other", False], res)),
                }
            )
