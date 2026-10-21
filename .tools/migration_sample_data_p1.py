#  Copyright (c) 2026 NSTDA
"""Sample data for the Phase 1 data migration pilot (nirun-life/nirun#141).

Fills a fresh 16.0 database that has ``ni_questionnaire`` installed with records
that cover the known data risks of the 16.0 -> 19.0 upgrade:

- patients with title, mobile and phone, and a ``private`` other-address partner
  (D2 at 17.0, D3 at 19.0);
- encounters in every state, with locations and participants, and an encounter
  class with auto-close;
- observations of every value type, computed BP and BMI, Nirun units of measure,
  reference ranges and interpretations, plus user-created units (D4 at 19.0);
- surveys for patients and encounters with a conditional question, grades with
  gender and age scopes, a question group, completed and partial responses, and
  the observations they produce;
- users in every Nirun group (D5 at 19.0);
- partners with religion, gender and age range.

Run once, through the Odoo shell, on a database without demo data (OpenUpgrade
removes demo records it no longer finds, which would show up as data loss):

    odoo-bin -c odoo16.conf -d nirun_p1 -i ni_questionnaire --without-demo=all \
        --stop-after-init
    odoo-bin shell -c odoo16.conf -d nirun_p1 --no-http \
        < .tools/migration_sample_data_p1.py

All names, numbers and dates are made up; the script holds no personal data.
"""

# pylint: disable=print-used
import sys
from datetime import date, datetime, timedelta

# 'env' is injected by the Odoo shell via exec() — pull it from globals so
# static analysis tools see it as a defined name.
env = globals().get("env")
if env is None:
    print(
        "ERROR: run via  python odoo-bin shell -c odoo.conf -d <db> --no-http"
        " < .tools/migration_sample_data_p1.py",
        file=sys.stderr,
    )
    sys.exit(1)

MARKER = "nirun.migration_sample_data_p1"
if env["ir.config_parameter"].sudo().get_param(MARKER):
    print("ERROR: sample data already loaded in this database", file=sys.stderr)
    sys.exit(1)

env = env(context=dict(env.context, tracking_disable=True, lang="en_US"), su=True)
ref = env.ref

# Fixed dates, so two runs give the same data. Past enough to be "finished",
# except the planned encounter, which must lie in the future.
BASE = datetime(2025, 6, 2, 9, 0)
FUTURE = datetime(2030, 1, 15, 9, 0)


def day(n, hour=9):
    return BASE.replace(hour=hour) + timedelta(days=n)


# ---------------------------------------------------------------- reference data

religions = env["res.religion"].search([], limit=2)
if len(religions) < 2:
    religions = env["res.religion"].create(
        [{"name": "Sample Religion A"}, {"name": "Sample Religion B"}]
    )
titles = {
    gender: env["res.partner.title"].search([("gender", "=", gender)], limit=1)
    for gender in ("male", "female")
}
company = env.company

location_type = env["ni.location.type"].search([], limit=1)
locations = env["ni.location"].create(
    [
        {"name": "Sample Ward A", "physical_type_id": location_type.id},
        {"name": "Sample Ward B", "physical_type_id": location_type.id},
    ]
)

# ------------------------------------------------------------------------ users

GROUPS = [
    "ni_patient.group_viewer",
    "ni_patient.group_user",
    "ni_patient.group_manager",
    "ni_patient.group_admin",
    "ni_observation.group_viewer",
    "ni_observation.group_user",
    "ni_observation.group_manager",
    "survey.group_survey_user",
]
users = env["res.users"]
for index, xmlid in enumerate(GROUPS, start=1):
    users |= (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": f"Sample Staff {index:02d}",
                "login": f"sample.staff{index:02d}",
                "groups_id": [(4, ref("base.group_user").id), (4, ref(xmlid).id)],
            }
        )
    )
employees = env["hr.employee"].create(
    [{"name": user.name, "user_id": user.id} for user in users[:3]]
)

# --------------------------------------------------------------------- patients

PATIENTS = [
    # gender, birthdate, title, mobile, phone, private address
    ("male", date(1950, 3, 1), True, "0800000001", "0200000001", True),
    ("female", date(1948, 7, 9), True, "0800000002", "0800000002", True),
    ("female", date(1960, 11, 20), True, "0800000003", False, False),
    ("male", date(1972, 1, 5), False, False, "0200000004", True),
    ("female", date(1985, 5, 15), True, "0800000005", "0200000005", False),
    ("male", date(2001, 9, 30), True, False, False, False),
    ("female", date(1939, 2, 14), False, "0800000007", "0200000007", True),
    ("male", date(1955, 12, 24), True, "0800000008", "0200000099", False),
]
patients = env["ni.patient"]
for index, (gender, birthdate, title, mobile, phone, private) in enumerate(
    PATIENTS, start=1
):
    identifier = f"SAMPLE-{index:03d}"
    partner = env["res.partner"].create(
        {
            "name": f"Sample Patient {index:02d}",
            "gender": gender,
            "title": title and titles[gender].id,
            "mobile": mobile,
            "phone": phone,
            "religion_id": religions[index % 2].id,
            "birthdate": birthdate,
            "company_id": company.id,
        }
    )
    patient = env["ni.patient"].create(
        {"partner_id": partner.id, "identifier": identifier}
    )
    if private:
        patient.other_address_id = env["res.partner"].create(
            {
                "name": f"Sample Home {index:02d}",
                "type": "private",
                "ref": identifier,
                "parent_id": partner.id,
                "street": f"{index} Sample Road",
                "city": "Sample City",
                "phone": f"02100000{index:02d}",
            }
        )
    patients |= patient

# A partner that is not a patient, with age range and religion only.
env["res.partner"].create(
    {
        "name": "Sample Relative",
        "gender": "female",
        "birthdate": date(1990, 4, 4),
        "religion_id": religions[0].id,
        "title": titles["female"].id,
        "mobile": "0800000100",
    }
)

# -------------------------------------------------------------------- encounters

class_auto = env["ni.encounter.class"].create(
    {
        "name": "Sample Day Care",
        "code": "SAMPLE-DC",
        "auto_close": True,
        "auto_close_offset_number": 1,
        "auto_close_offset_type": "days",
    }
)
class_stay = ref("ni_patient.class_IMP")


def encounter(patient, klass, start, location=None):
    vals = {
        "patient_id": patient.id,
        "class_id": klass.id,
        "period_start": start,
        "location_id": (location or locations[0]).id,
    }
    if patient.other_address_id:
        vals["other_address_id"] = patient.other_address_id.id
    enc = env["ni.encounter"].create(vals)
    enc.participant_ids = [
        (
            0,
            0,
            {
                "employee_id": employees[0].id,
                "period_start": start,
            },
        )
    ]
    return enc


encounters = {}
# finished (auto-close class and long stay)
for index, patient in enumerate(patients[:4]):
    enc = encounter(patient, class_auto if index % 2 else class_stay, day(index))
    enc.action_confirm()
    enc.action_close({"state": "finished", "period_end": day(index, hour=17)})
    encounters.setdefault("finished", env["ni.encounter"])
    encounters["finished"] |= enc
# in progress: one per patient that has no open encounter yet
for index, patient in enumerate(patients[:6]):
    enc = encounter(patient, class_stay, day(30 + index), locations[index % 2])
    enc.action_confirm()
    encounters.setdefault("in-progress", env["ni.encounter"])
    encounters["in-progress"] |= enc
encounters["planned"] = encounter(patients[6], class_stay, FUTURE)
encounters["planned"].action_confirm()
encounters["draft"] = encounter(patients[7], class_stay, day(40))
encounters["cancelled"] = encounter(patients[6], class_auto, day(41))
encounters["cancelled"].action_cancel()
encounters["error"] = encounter(patients[7], class_auto, day(5))
encounters["error"].action_entered_in_error()

# ------------------------------------------------------------------ observations


def obs_type(xmlid):
    return ref(f"ni_observation.{xmlid}")


# User-created units in a Nirun category (one smaller, one bigger than the
# reference unit) and a user-created category. They check the UoM conversion at
# 19.0, including OpenUpgrade's handling of "bigger" units.
density = ref("ni_observation.uom_categ_density")
env["uom.uom"].create(
    [
        {
            "name": "Sample g/m³",
            "category_id": density.id,
            "uom_type": "smaller",
            "factor": 1000.0,
        },
        {
            "name": "Sample 10 kg/m³",
            "category_id": density.id,
            "uom_type": "bigger",
            "factor_inv": 10.0,
        },
    ]
)
sample_category = env["uom.category"].create({"name": "Sample Score"})
env["uom.uom"].create(
    [
        {
            "name": "Sample point",
            "category_id": sample_category.id,
            "uom_type": "reference",
        },
        {
            "name": "Sample 5 points",
            "category_id": sample_category.id,
            "uom_type": "bigger",
            "factor_inv": 5.0,
        },
    ]
)

smoking = obs_type("type_smoking_status")
alcohol = obs_type("type_alcohol_use")
VITALS = [
    # sys, dia, weight, height, temperature, glucose
    (150, 95, 62.5, 160.0, 37.2, 126.0),
    (118, 76, 48.0, 152.0, 36.6, 92.0),
    (135, 85, 80.0, 175.0, 38.1, 185.0),
]
sheets = env["ni.observation.sheet"]
for index, enc in enumerate(encounters["in-progress"] | encounters["finished"]):
    sys_bp, dia_bp, weight, height, temperature, glucose = VITALS[index % 3]
    sheet = env["ni.observation.sheet"].create(
        {
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "occurrence": enc.period_start + timedelta(hours=1),
        }
    )
    values = [
        ("type_bp_s", sys_bp),
        ("type_bp_d", dia_bp),
        ("type_body_weight", weight),
        ("type_body_height", height),
        ("type_body_temp", temperature),
        ("type_glucose", glucose),
    ]
    env["ni.observation"].create(
        [
            {
                "sheet_id": sheet.id,
                "patient_id": enc.patient_id.id,
                "encounter_id": enc.id,
                "occurrence": sheet.occurrence,
                "type_id": obs_type(xmlid).id,
                f"value_{obs_type(xmlid).value_type}": value,
            }
            for xmlid, value in values
        ]
        + [
            {
                "sheet_id": sheet.id,
                "patient_id": enc.patient_id.id,
                "encounter_id": enc.id,
                "occurrence": sheet.occurrence,
                "type_id": smoking.id,
                "value_code_id": smoking.value_code_ids[
                    index % len(smoking.value_code_ids)
                ].id,
            },
            {
                "sheet_id": sheet.id,
                "patient_id": enc.patient_id.id,
                "encounter_id": enc.id,
                "occurrence": sheet.occurrence,
                "type_id": alcohol.id,
                "value_code_id": alcohol.value_code_ids[:1].id,
            },
        ]
    )
    sheets |= sheet

# A free-text and a multi-choice observation type, so that every value type has
# at least one record.
note_type = env["ni.observation.type"].create(
    {"name": "Sample Note", "code": "sample-note", "value_type": "char"}
)
multi_type = env["ni.observation.type"].create(
    {
        "name": "Sample Symptoms",
        "code": "sample-symptoms",
        "value_type": "code_ids",
        "value_code_ids": [
            (0, 0, {"name": "Sample Cough", "code": "sample-cough"}),
            (0, 0, {"name": "Sample Fever", "code": "sample-fever"}),
            (0, 0, {"name": "Sample Rash", "code": "sample-rash"}),
        ],
    }
)
first = encounters["in-progress"][0]
env["ni.observation"].create(
    [
        {
            "patient_id": first.patient_id.id,
            "encounter_id": first.id,
            "occurrence": day(30, hour=11),
            "type_id": note_type.id,
            "value_char": "Sample note text",
        },
        {
            "patient_id": first.patient_id.id,
            "encounter_id": first.id,
            "occurrence": day(30, hour=11),
            "type_id": multi_type.id,
            "value_code_ids": [(6, 0, multi_type.value_code_ids[:2].ids)],
        },
    ]
)

# ----------------------------------------------------------------------- surveys

score_type = env["ni.observation.type"].create(
    {
        "name": "Sample Risk Score",
        "code": "sample-risk-score",
        "value_type": "int",
        "min": 0,
        "max": 10,
    }
)
item_type = env["ni.observation.type"].create(
    {
        "name": "Sample Mobility Item",
        "code": "sample-mobility",
        "value_type": "int",
        "min": 0,
        "max": 10,
    }
)
group_type = env["ni.observation.type"].create(
    {
        "name": "Sample Group Sum",
        "code": "sample-group-sum",
        "value_type": "int",
        "min": 0,
        "max": 20,
    }
)


def choice(survey, title, sequence, score, **kwargs):
    vals = {
        "title": title,
        "sequence": sequence,
        "survey_id": survey.id,
        "question_type": "simple_choice",
        "suggested_answer_ids": [
            (0, 0, {"value": "No", "answer_score": 0}),
            (0, 0, {"value": "Yes", "answer_score": score}),
        ],
    }
    vals.update(kwargs)
    return env["survey.question"].create(vals)


def answer(question, value):
    return question.suggested_answer_ids.filtered(lambda a: a.value == value)


surveys = {}
for subject_type in ("ni.patient", "ni.encounter"):
    survey = env["survey.survey"].create(
        {
            "title": f"Sample Risk Survey ({subject_type})",
            "subject_type": subject_type,
            "scoring_type": "scoring_without_answers",
            "grading_basis": "score",
            "observation_type_id": score_type.id,
            "observation_score_type": "raw",
            "questions_layout": "one_page",
        }
    )
    q_fall = choice(
        survey,
        "Sample: fell in the last year?",
        10,
        4,
        observation_code_id=item_type.id,
        observation_answer_type="score",
    )
    q_injury = choice(
        survey,
        "Sample: injured by the fall?",
        20,
        3,
        is_conditional=True,
        triggering_question_id=q_fall.id,
        triggering_answer_id=answer(q_fall, "Yes").id,
    )
    q_aid = choice(survey, "Sample: uses a walking aid?", 30, 3)
    env["survey.question.group"].create(
        {
            "survey_id": survey.id,
            "question_ids": [(6, 0, (q_fall | q_aid).ids)],
            "observation_code_id": group_type.id,
            "operator": "sum",
        }
    )
    env["survey.grade"].create(
        [
            {"survey_id": survey.id, "name": "Sample Low", "low": 0, "high": 3},
            {
                "survey_id": survey.id,
                "name": "Sample High (female)",
                "low": 4,
                "high": 10,
                "gender": "female",
            },
            {
                "survey_id": survey.id,
                "name": "Sample High (male, 60+)",
                "low": 4,
                "high": 10,
                "gender": "male",
                "age_low": 60,
                "age_high": 200,
            },
            {
                "survey_id": survey.id,
                "name": "Sample High (male, under 60)",
                "low": 4,
                "high": 10,
                "gender": "male",
                "age_low": 0,
                "age_high": 59,
            },
        ]
    )
    surveys[subject_type] = (survey, q_fall, q_injury, q_aid)

class_stay.survey_id = surveys["ni.encounter"][0]


def respond(subject_type, enc, choices, done=True):
    survey, q_fall, q_injury, q_aid = surveys[subject_type]
    subject = enc if subject_type == "ni.encounter" else enc.patient_id
    response = survey._create_answer(
        user=users[0],
        subject_model=subject_type,
        subject_id=subject.id,
        patient_id=enc.patient_id.id,
        encounter_id=enc.id,
    )
    for question, value in zip((q_fall, q_injury, q_aid), choices):
        if value is None:
            continue
        env["survey.user_input.line"].create(
            {
                "user_input_id": response.id,
                "survey_id": survey.id,
                "question_id": question.id,
                "skipped": False,
                "answer_type": "suggestion",
                "suggested_answer_id": answer(question, value).id,
            }
        )
    if done:
        response._mark_done()
    else:
        response.state = "in_progress"
    return response


for index, enc in enumerate(encounters["in-progress"]):
    choices = [("Yes", "Yes", "Yes"), ("No", None, "No"), ("Yes", "No", "Yes")]
    respond("ni.encounter", enc, choices[index % 3])
    respond("ni.patient", enc, choices[(index + 1) % 3])
# partial responses
respond("ni.encounter", encounters["finished"][0], ("Yes", None, None), done=False)
respond("ni.patient", encounters["finished"][1], ("No", None, None), done=False)

env["ir.config_parameter"].set_param(MARKER, "1")
env.cr.commit()

print(
    "OK: sample data loaded: "
    f"{len(patients)} patients, "
    f"{env['ni.encounter'].with_context(active_test=False).search_count([])} encounters, "
    f"{env['ni.observation'].search_count([])} observations, "
    f"{env['survey.user_input'].search_count([])} responses, "
    f"{len(users)} users",
    file=sys.stderr,
)
