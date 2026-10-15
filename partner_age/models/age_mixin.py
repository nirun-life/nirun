#  Copyright (c) 2024 NSTDA
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AgeMixin(models.AbstractModel):
    _name = "age.mixin"
    _description = "Age mixin"

    birthdate = fields.Date("Date of Birth", tracking=True)
    deceased_date = fields.Date(tracking=True)
    deceased = fields.Boolean(compute="_compute_is_deceased", store=True, tracking=True)
    display_age = fields.Char("Age", compute="_compute_display_age", compute_sudo=True)
    age = fields.Integer(
        "Age (years)",
        compute="_compute_age",
        inverse="_inverse_age",
        compute_sudo=True,
        store=True,
        readonly=False,
        aggregator="avg",
    )
    age_month = fields.Integer(
        "Age (month)",
        compute="_compute_age",
        compute_sudo=True,
        store=True,
        readonly=False,
        aggregator="avg",
    )
    age_day = fields.Integer(
        "Age (day)",
        compute="_compute_age",
        compute_sudo=True,
        store=True,
        readonly=False,
        aggregator="avg",
    )
    age_init = fields.Integer(
        "Age (Years) Input", help="Internal: Age (years) input value", readonly=True
    )
    age_init_date = fields.Date(
        "Age (Years) Input Date",
        help="Internal: Date when Age (years) input value was provided",
        readonly=True,
    )
    age_range_id = fields.Many2one(
        "res.partner.age.range",
        compute="_compute_age_range_id",
        index=True,
        store=True,
        ondelete="set null",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("age") and not vals.get("birthdate"):
                vals.update(
                    {
                        "birthdate": None,
                        "age_init": vals.get("age"),
                        "age_init_date": fields.Date.context_today(self),
                    }
                )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("birthdate"):
            vals.update({"age_init": None, "age_init_date": None})
        elif vals.get("age"):
            vals.update(
                {
                    "birthdate": None,
                    "age_init": vals.get("age"),
                    "age_init_date": fields.Date.context_today(self),
                }
            )
        return super().write(vals)

    def _inverse_age(self):
        for rec in self:
            if not rec.birthdate:
                rec.age_init = rec.age
                rec.age_init_date = fields.Date.context_today(self)
            if rec.birthdate:
                rec.age_init = 0
                rec.age_init_date = None

    @api.depends("birthdate", "deceased_date", "age_init")
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                rec._compute_age_from_birthdate()
            elif rec.age_init:
                rec._compute_age_from_init()
            else:
                rec.age = 0

    @api.depends("birthdate", "deceased_date", "age_init", "age_init_date")
    def _compute_display_age(self):
        today = fields.Date.context_today(self)
        for rec in self:
            dt = rec.deceased_date or today
            if rec.birthdate:
                rec.display_age = self._format_age(relativedelta(dt, rec.birthdate))
            elif rec.age_init and rec.age_init_date:
                age_year = rec.age_init + dt.year - rec.age_init_date.year
                rec.display_age = self.env._("%s Years", age_year)
            else:
                rec.display_age = None

    def _compute_age_from_init(self, date=None):
        if not date:
            date = fields.Date.context_today(self)
        for rec in self:
            if rec.age_init and rec.age_init_date:
                dt = rec.deceased_date if rec.deceased_date else date
                year_diff = dt.year - rec.age_init_date.year
                age_year = rec.age_init + year_diff
                if rec.age != age_year:
                    # check this for reduce chance to call `_inverse_age()`
                    rec.age = age_year
                rec.age_month = 0
                rec.age_day = 0

    def _compute_age_from_birthdate(self, date=None):
        if not date:
            date = fields.Date.context_today(self)
        for rec in self:
            if rec.birthdate:
                dt = rec.deceased_date if rec.deceased_date else date
                rd = relativedelta(dt, rec.birthdate)
                if rec.age != rd.years:
                    # check this for reduce chance to call `_inverse_age()`
                    rec.age = rd.years
                rec.age_month = rd.months
                rec.age_day = rd.days
                _logger.debug(f"age = {rec.age}Y {rec.age_month}M {rec.age_day}D")

    @api.model
    def _format_age(self, delta):
        result = []
        if delta.years > 0:
            result.append(self.env._("%s Years", delta.years))
        if delta.months > 0:
            result.append(self.env._("%s Months", delta.months))
        if delta.days > 0:
            result.append(self.env._("%s Days", delta.days))
        return " ".join(result) or None

    @api.depends("age")
    def _compute_age_range_id(self):
        # Age ranges are a short configuration list, read them all once.
        range_ids = self.env["res.partner.age.range"].search([])  # pylint: disable=no-search-all
        for record in self:
            if not record.age:
                range_id = False
            else:
                age = record.age
                range_id = (
                    range_ids.filtered(lambda r, age=age: r.age_from <= age <= r.age_to)
                    or False
                )
            if record.age_range_id != range_id:
                record.age_range_id = range_id

    @api.constrains("birthdate")
    def _check_birthdate(self):
        """Not allow birthdates in the future."""
        for record in self:
            if not record.birthdate:
                continue
            if record.birthdate > fields.Date.today():
                raise ValidationError(
                    self.env._(
                        "Birthdate must not be in the future",
                    )
                )

    @api.constrains("deceased_date")
    def _check_deceased_date(self):
        for record in self:
            if not record.deceased_date:
                continue
            if record.deceased_date > fields.Date.today():
                raise ValidationError(
                    self.env._(
                        "Deceased date must not be in the future",
                    )
                )
            if record.birthdate and record.deceased_date < record.birthdate:
                raise ValidationError(
                    self.env._(
                        "Deceased date must not before birthdate",
                    )
                )

    @api.constrains("age")
    def _check_age(self):
        for rec in self:
            if rec.age < 0:
                raise ValidationError(self.env._("Age (years) must not be less than 0"))

    @api.depends("deceased_date")
    def _compute_is_deceased(self):
        for record in self:
            record.deceased = bool(record.deceased_date)

    @api.model
    def cron_compute_age(self):
        partner = self.search(
            [
                ("deceased", "!=", True),
                "|",
                ("birthdate", "!=", False),
                ("age_init", "!=", False),
            ]
        )
        partner._compute_age()

    @api.model
    def cron_compute_age_range(self):
        partner = self.search([("age", "!=", False)])
        partner._compute_age_range_id()
