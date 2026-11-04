#  Copyright (c) 2026 NSTDA
"""Sample data for the Phase 2 data migration check (nirun-life/nirun#193).

Adds, on top of ``migration_sample_data_p1.py``, records that cover the known data
risks of the Phase 2 modules on the 16.0 -> 19.0 upgrade:

- practitioners: licences (``hr.resume.line`` with an identifier), encounter
  performer, licence and department; user roles with an invitation token in two
  companies (company-dependent field, jsonb at 18.0);
- employees with a home address and no work contact, used as communication
  sender (D11: ``address_home_id`` is gone at 17.0);
- conditions in the problem list and as encounter diagnoses with roles, several
  per patient and code, so ``ni.condition.latest`` has to choose;
- procedures, allergies with reactions, communications in every state, and
  document references with attachments (filestore);
- coverages with insurance plans, benefits and copay; related persons with a
  title and a mobile (D3 through ``_inherits`` at 19.0);
- immunizations and dose evaluations giving each protection status;
- services with categories, two of them without the ``category_ids`` rows the
  old backfill cron fills, service events on the calendar (all-day and timed),
  encounter attendances and service requests;
- users in each new Nirun group (procedure, communication, immunization).

Run once, through the Odoo shell, on the Phase 1 sample database with the Phase 2
modules installed, after ``migration_sample_data_p1.py``:

    odoo-bin -c odoo16.conf -d nirun_p2 --without-demo=all --stop-after-init \
        -i ni_questionnaire,ni_timing,ni_body_site,ni_organization,ni_specialty,\
ni_coding_specialty,ni_practitioner,ni_practitioner_role,ni_condition,\
ni_procedure,ni_allergy,ni_coverage,ni_document_ref,ni_communication,\
ni_related_person,ni_immunization,ni_benefit,ni_service
    odoo-bin shell -c odoo16.conf -d nirun_p2 --no-http \
        < .tools/migration_sample_data_p1.py
    odoo-bin shell -c odoo16.conf -d nirun_p2 --no-http \
        < .tools/migration_sample_data_p2.py

All names, numbers and dates are made up; the script holds no personal data.
"""

# pylint: disable=print-used
import base64
import sys
from datetime import date, datetime, timedelta

# 'env' is injected by the Odoo shell via exec() — pull it from globals so
# static analysis tools see it as a defined name.
env = globals().get("env")
if env is None:
    print(
        "ERROR: run via  python odoo-bin shell -c odoo.conf -d <db> --no-http"
        " < .tools/migration_sample_data_p2.py",
        file=sys.stderr,
    )
    sys.exit(1)

MARKER = "nirun.migration_sample_data_p2"
params = env["ir.config_parameter"].sudo()
if params.get_param(MARKER):
    print("ERROR: sample data already loaded in this database", file=sys.stderr)
    sys.exit(1)
if not params.get_param("nirun.migration_sample_data_p1"):
    print("ERROR: run migration_sample_data_p1.py first", file=sys.stderr)
    sys.exit(1)

env = env(context=dict(env.context, tracking_disable=True, lang="en_US"), su=True)
ref = env.ref

# Same fixed dates as the Phase 1 script.
BASE = datetime(2025, 6, 2, 9, 0)


def day(n, hour=9, minute=0):
    return BASE.replace(hour=hour, minute=minute) + timedelta(days=n)


company = env.company
patients = env["ni.patient"].search([("identifier", "like", "SAMPLE-")], order="id")
encounters = (
    env["ni.encounter"]
    .with_context(active_test=False)
    .search([("patient_id", "in", patients.ids)], order="id")
)
open_encounters = encounters.filtered(lambda e: e.state == "in-progress")
finished = encounters.filtered(lambda e: e.state == "finished")
staff = env["hr.employee"].search([("name", "like", "Sample Staff")], order="id")
assert len(patients) == 8 and open_encounters and staff, "Phase 1 data not found"

# ------------------------------------------------------------- organization (P2-1)

company.write({"capacity": 30, "capacity_unit": "bed", "identifier": "SAMPLE-ORG-1"})
company_type = env["res.company.type"].create({"name": "Sample Care Home"})
company_2 = env["res.company"].create(
    {
        "name": "Sample Branch",
        "type_id": company_type.id,
        "capacity": 40,
        "capacity_unit": "pat",
    }
)
env.user.company_ids = [(4, company_2.id)]
benefits = env["ni.benefit"].search([], limit=3, order="id")
patients[0].benefit_ids = [(6, 0, benefits[:2].ids)]
patients[1].benefit_ids = [(6, 0, benefits[2:3].ids)]

# ------------------------------------------------------------ practitioners (P2-2)

department = env["hr.department"].search([], limit=1, order="id")
jobs = env["hr.job"].create(
    [{"name": "Sample Nurse"}, {"name": "Sample Physiotherapist"}]
)
license_type = ref("ni_practitioner.resume_type_license")
certificate_type = ref("ni_practitioner.resume_type_certificate")
license_code = env["hr.resume.line.code"].search(
    [("type_id", "=", license_type.id)], limit=1, order="id"
)
for index, employee in enumerate(staff, start=1):
    employee.write({"department_id": department.id, "job_id": jobs[index % 2].id})
    env["hr.resume.line"].create(
        [
            {
                "employee_id": employee.id,
                "name": f"Sample Licence {index:02d}",
                "line_type_id": license_type.id,
                "code_id": license_code.id,
                "identifier": f"SAMPLE-LIC-{index:04d}",
                "date_start": date(2015 + index, 1, 1),
            },
            {
                "employee_id": employee.id,
                "name": f"Sample Certificate {index:02d}",
                "line_type_id": certificate_type.id,
                "date_start": date(2020, index, 1),
            },
        ]
    )
staff[0].license_id = staff[0].resume_line_ids.filtered("identifier")[:1]

# Setting a performer adds a participation from now on; Sample Staff 01 already
# takes part in every encounter (Phase 1), so use the other two.
for index, enc in enumerate(encounters):
    performer = staff[1 + index % 2]
    enc.write(
        {
            "performer_id": performer.id,
            "performer_license_id": performer.license_default_id.id,
            "department_id": department.id,
        }
    )

categories = env["hr.employee.category"].search([], limit=2, order="id")
roles = env["res.users.role"].create(
    [
        {
            "name": "Sample Caregiver Role",
            "employee_category_ids": [(6, 0, categories[:1].ids)],
        },
        {
            "name": "Sample Volunteer Role",
            "employee_category_ids": [(6, 0, categories[1:2].ids)],
        },
    ]
)
for index, role in enumerate(roles, start=1):
    role.with_company(company).access_token = f"sample-token-{index}-c1"
    role.with_company(company_2).access_token = f"sample-token-{index}-c2"
role_user = (
    env["res.users"]
    .with_context(no_reset_password=True)
    .create(
        {
            "name": "Sample Registered Caregiver",
            "login": "sample.caregiver",
            "company_id": company.id,
            "company_ids": [(6, 0, [company.id, company_2.id])],
            "verified": False,
        }
    )
)
env["res.users.role.line"].create({"role_id": roles[0].id, "user_id": role_user.id})

# --------------------------------------------------------------- new Nirun groups

GROUPS = [
    "ni_procedure.group_viewer",
    "ni_procedure.group_user",
    "ni_procedure.group_manager",
    "ni_communication.group_viewer",
    "ni_communication.group_user",
    "ni_communication.group_manager",
    "ni_immunization.group_viewer",
    "ni_immunization.group_user",
    "ni_immunization.group_manager",
    "ni_immunization.group_admin",
]
for index, xmlid in enumerate(GROUPS, start=1):
    env["res.users"].with_context(no_reset_password=True).create(
        {
            "name": f"Sample P2 Staff {index:02d}",
            "login": f"sample.p2staff{index:02d}",
            "groups_id": [(4, ref("base.group_user").id), (4, ref(xmlid).id)],
        }
    )

# ------------------------------------------------- employees with a home address

home_senders = env["hr.employee"]
for index in (1, 2):
    home = env["res.partner"].create(
        {
            "name": f"Sample Home Address {index:02d}",
            "type": "private",
            "street": f"{index} Sample Lane",
            "city": "Sample City",
        }
    )
    employee = env["hr.employee"].create(
        {
            "name": f"Sample Visiting Staff {index:02d}",
            "address_home_id": home.id,
            "department_id": department.id,
        }
    )
    # Employees from before 16.0 have no work contact: the sender falls back to
    # the home address.
    work_contact = employee.work_contact_id
    employee.work_contact_id = False
    work_contact.unlink()
    home_senders |= employee

# ------------------------------------------------------------- conditions (P2-5)

condition_codes = env["ni.condition.code"].create(
    [
        {"name": "Sample Hypertension", "code": "SAMPLE-HT"},
        {"name": "Sample Diabetes", "code": "SAMPLE-DM"},
        {"name": "Sample Fall Risk", "code": "SAMPLE-FALL"},
    ]
)
condition_codes[0].observation_code_ids = [(6, 0, [ref("ni_observation.type_bp_s").id])]
problem_category = env["ni.condition.category"].search([], limit=1, order="id")
verifications = env["ni.condition.verification"].search([], order="id")
roles_dx = env["ni.encounter.diagnosis.role"].search([], order="id")
# (patient_id, code_id) is unique on 16.0, so only conditions without a code can
# repeat for a patient; ni.condition.latest groups those together and keeps the
# newest one in an active, recurrence or remission state.
CONDITIONS = [
    # patient index, code index (None: free text), clinical state, severity,
    # verification
    (0, 0, "active", "moderate", 3),
    (0, 1, "recurrence", "severe", 3),
    (0, 2, "resolved", "mild", 1),
    (0, None, "active", "mild", 1),
    (0, None, "remission", "mild", 1),  # newest free-text one: latest keeps it
    (0, None, "inactive", "mild", 0),  # newer but excluded by its state
    (1, 0, "active", "mild", 3),
    (1, 2, "inactive", "mild", 0),
    (2, 1, "active", "severe", 3),
    (3, 2, "relapse", "moderate", 2),
    (4, 0, "remission", None, 3),
]
conditions = env["ni.condition"]
for index, (pat, code, state, severity, verif) in enumerate(CONDITIONS):
    patient = patients[pat]
    enc = encounters.filtered(lambda e, p=patient: e.patient_id == p)[:1]
    code = condition_codes[code] if code is not None else condition_codes.browse()
    conditions |= env["ni.condition"].create(
        {
            "patient_id": patient.id,
            "encounter_id": enc.id,
            "code_id": code.id,
            "name": code.name or f"Sample free-text condition {index:02d}",
            "clinical_state": state,
            "severity": severity,
            "verification_id": verifications[verif].id,
            "is_problem": index % 3 != 2,
            "is_diagnosis": index % 2 == 0,
            "category_ids": [(6, 0, problem_category.ids)],
            "period_start": day(-300 + index * 20),
            "note": "Sample condition note",
        }
    )
for index, condition in enumerate(conditions.filtered("is_diagnosis")):
    enc = condition.encounter_id
    if enc:
        env["ni.encounter.diagnosis"].create(
            {
                "condition_id": condition.id,
                "encounter_id": enc.id,
                "role_id": roles_dx[index % len(roles_dx)].id,
            }
        )

# ------------------------------------------------- procedures, allergies (P2-3)

procedure_category = env["ni.procedure.category"].search([], limit=1, order="id")
procedure_codes = env["ni.procedure.code"].create(
    [
        {
            "name": "Sample Wound Dressing",
            "code": "SAMPLE-WD",
            "category_id": procedure_category.id,
            "duration_hours": 0.5,
        },
        {
            "name": "Sample Physiotherapy",
            "code": "SAMPLE-PT",
            "category_id": procedure_category.id,
            "duration_hours": 1.0,
        },
    ]
)
outcomes = env["ni.procedure.outcome"].search([], order="id")
PROC_STATES = [
    "preparation",
    "in-progress",
    "completed",
    "completed",
    "not-done",
    "suspended",
    "abort",
]
for index, state in enumerate(PROC_STATES):
    enc = open_encounters[index % len(open_encounters)]
    env["ni.procedure"].create(
        {
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "code_id": procedure_codes[index % 2].id,
            "category_id": procedure_category.id,
            "performer_id": staff[index % len(staff)].id,
            "location_id": enc.location_id.id,
            "period_start": day(30 + index, hour=10),
            "period_end": day(30 + index, hour=11),
            "state": state,
            "outcome_id": outcomes[index % len(outcomes)].id
            if state == "completed"
            else False,
            "note": "Sample procedure note",
        }
    )

allergy_codes = env["ni.allergy.code"].create(
    [
        {"name": "Sample Peanut", "code": "SAMPLE-PEANUT", "category": "food"},
        {"name": "Sample Penicillin", "code": "SAMPLE-PEN", "category": "medication"},
        {"name": "Sample Dust", "code": "SAMPLE-DUST", "category": "environment"},
    ]
)
ALLERGIES = [
    # patient, code, criticality, state, type
    (0, 0, "high", "active", "allergy"),
    (0, 1, "low", "active", "intolerance"),
    (1, 2, "unable-to-assess", "inactive", "allergy"),
    (3, 1, "high", "resolved", "allergy"),
]
# ni.allergy.create has no @api.model_create_multi on 16.0: pass a list.
for index, (pat, code, criticality, state, kind) in enumerate(ALLERGIES):
    env["ni.allergy"].create(
        [
            {
                "patient_id": patients[pat].id,
                "code_id": allergy_codes[code].id,
                "name": allergy_codes[code].name,
                "category": allergy_codes[code].category,
                "criticality": criticality,
                "state": state,
                "type": kind,
                "last_occurrence": day(-60 + index),
                "reaction_ids": [
                    (
                        0,
                        0,
                        {
                            "onset": day(-60 + index),
                            "severity": "moderate",
                            "description": "Sample reaction",
                        },
                    ),
                    (0, 0, {"onset": day(-200 + index), "severity": "mild"}),
                ],
            }
        ]
    )
patients[0].allergy = "identified"
patients[2].allergy = "unknown"
patients[5].allergy = "not-ask"

# ---------------------------------------------------------- communications (P2-3)

comm_categories = env["ni.communication.category"].search([], order="id")
contents = env["ni.communication.content"].create(
    [
        {"name": "Sample Diet Advice", "category_id": comm_categories[0].id},
        {"name": "Sample Exercise Advice", "category_id": comm_categories[0].id},
    ]
)
COMM_STATES = [
    "preparation",
    "in-progress",
    "completed",
    "not-done",
    "suspended",
    "abort",
]
for index, state in enumerate(COMM_STATES):
    enc = open_encounters[index % len(open_encounters)]
    sender = (staff + home_senders)[index % (len(staff) + len(home_senders))]
    env["ni.communication"].create(
        {
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "category_id": comm_categories[index % len(comm_categories)].id,
            "content_ids": [(6, 0, contents.ids)]
            if index % len(comm_categories) == 0
            else [],
            "sender_employee_id": sender.id,
            "recipient_ids": [(6, 0, enc.patient_id.partner_id.ids)],
            "period_start": day(30 + index, hour=14),
            "state": state,
            "note": "Sample communication note",
        }
    )
# Both home-address senders must be used.
for employee in home_senders:
    enc = finished[0]
    env["ni.communication"].create(
        {
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "category_id": comm_categories[0].id,
            "sender_employee_id": employee.id,
            "recipient_ids": [(6, 0, enc.patient_id.partner_id.ids)],
            "period_start": day(1, hour=15),
        }
    )

# ------------------------------------------------------ document references (P2-3)

doc_types = env["ni.document.ref.type"].search([], order="id")
PDF = (
    b"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
)
for index, enc in enumerate(open_encounters[:4] | finished[:1]):
    attachments = env["ir.attachment"].create(
        [
            {
                "name": f"sample-document-{index:02d}.pdf",
                "datas": base64.b64encode(PDF + f"% sample {index}\n".encode()),
                "mimetype": "application/pdf",
            },
            {
                "name": f"sample-note-{index:02d}.txt",
                "datas": base64.b64encode(f"Sample note {index}\n".encode()),
                "mimetype": "text/plain",
            },
        ]
    )
    doc = env["ni.document.ref"].create(
        {
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "type_id": doc_types[index % len(doc_types)].id,
            "attachment_ids": [(6, 0, attachments[: 1 + index % 2].ids)],
            "author_id": staff[index % len(staff)].id,
            "author_ids": [(6, 0, staff[:2].ids)],
            "occurrence": day(30 + index, hour=16),
            "state": "completed" if index % 3 else "in-progress",
        }
    )
    attachments.write({"res_model": "ni.document.ref", "res_id": doc.id})

# ---------------------------------------------------------- coverage, related (P2-4)

copays = env["ni.coverage.copay"].search([], order="id")
coverage_types = env["ni.coverage.type"].search([], order="id")
insurance_type = coverage_types.filtered(lambda t: t.kind == "insurance")[:1]
self_pay_type = coverage_types.filtered(lambda t: t.kind == "self-pay")[:1]
other_type = coverage_types.filtered(lambda t: t.kind == "other")[:1]
insurer = env["res.partner"].create({"name": "Sample Insurer", "is_company": True})
thb = ref("base.THB")
thb.active = True
plans = env["ni.insurance.plan"].create(
    [
        {
            "name": "Sample Basic Plan",
            "alias": "SBP",
            "type_id": insurance_type.id,
            "issuer_id": insurer.id,
            "benefit_ids": [
                (
                    0,
                    0,
                    {
                        "type_id": copays[0].id,
                        "value": 500.0,
                        "value_currency_id": thb.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "type_id": copays[1].id,
                        "value_percentage": 20.0,
                        "value_currency_id": thb.id,
                    },
                ),
            ],
        },
        {
            "name": "Sample Premium Plan",
            "type_id": insurance_type.id,
            "issuer_id": insurer.id,
        },
    ]
)
COVERAGES = [
    # patient, plan, type, state
    (0, 0, insurance_type, "active"),
    (0, None, self_pay_type, "active"),
    (1, 1, insurance_type, "active"),
    (2, None, other_type, "draft"),
    (3, 0, insurance_type, "cancelled"),
    (4, None, self_pay_type, "entered-in-error"),
]
for index, (pat, plan, ctype, state) in enumerate(COVERAGES):
    patient = patients[pat]
    coverage = env["ni.coverage"].create(
        {
            "name": plans[plan].name
            if plan is not None
            else f"Sample Coverage {index}",
            "patient_id": patient.id,
            "insurance_plan_id": plans[plan].id if plan is not None else False,
            "type_id": ctype.id,
            "insurer": insurer.id if plan is not None else False,
            "subscriber_id": patient.partner_id.id,
            "subscriber_no": f"SAMPLE-SUB-{index:03d}",
            "dependent_no": "01",
            "identifier": f"SAMPLE-COV-{index:03d}",
            # period_start is a Date on ni.coverage but ni.period.mixin calls
            # .date() on it: on 16.0 a coverage with a start date cannot be saved.
            "period_end": datetime(2026, 12, 31, 23, 59),
            "state": state,
            "benefit_ids": [
                (
                    0,
                    0,
                    {
                        "type_id": copays[index % len(copays)].id,
                        "value": 100.0 * (index + 1),
                        "value_percentage": 10.0,
                        "value_currency_id": thb.id,
                    },
                )
            ],
        }
    )
    if state == "active":
        patient.coverage_id = coverage

relationships = env["ni.patient.relationship"].search([], order="id")
titles = env["res.partner.title"].search([], order="id")
RELATED = [
    # patient, title, mobile, phone, relationships
    (0, 0, "0810000001", "0210000001", [0]),
    (0, 1, False, "0210000002", [1, 2]),
    (1, 1, "0810000003", False, [3]),
    (2, None, "0810000004", "0810000004", [0]),
    (4, 0, False, False, [4]),
]
for index, (pat, title, mobile, phone, rels) in enumerate(RELATED, start=1):
    env["ni.patient.related.person"].create(
        {
            "patient_id": patients[pat].id,
            "name": f"Sample Related Person {index:02d}",
            "title": titles[title].id if title is not None else False,
            "mobile": mobile,
            "phone": phone,
            "relationship_ids": [(6, 0, [relationships[i].id for i in rels])],
            "period_start": day(-1000),
        }
    )

# ---------------------------------------------------------- immunizations (P2-6)

diseases = env["ni.immunization.target.disease"].search(
    [("series_doses", ">", 1)], order="id", limit=2
)
single = env["ni.immunization.target.disease"].search(
    [("series_doses", "<=", 1)], order="id", limit=1
)
vaccines = env["ni.immunization.vaccine"].search([], order="id")
routes = env["ni.immunization.route"].search([], order="id")
sites = env["ni.body.site"].search([], order="id", limit=2)


def vaccine_for(disease):
    return (
        vaccines.filtered(lambda v: disease in v.target_disease_ids)[:1] or vaccines[0]
    )


EVALUATIONS = [
    # patient, disease, doses given, last dose valid -> protected / partial / not
    (0, diseases[0], diseases[0].series_doses, True),  # protected
    (0, diseases[1], 1, True),  # partial
    (1, diseases[0], 2, False),  # not protected
    (1, single, 1, True),  # protected (single dose)
    (2, diseases[1], diseases[1].series_doses, True),  # protected
]
for pat, disease, doses, valid in EVALUATIONS:
    patient = patients[pat]
    enc = open_encounters.filtered(lambda e, p=patient: e.patient_id == p)[:1]
    vaccine = vaccine_for(disease)
    for dose in range(1, doses + 1):
        when = day(-400 + dose * 30, hour=10)
        immunization = env["ni.immunization"].create(
            {
                "patient_id": patient.id,
                "encounter_id": enc.id,
                "vaccine_id": vaccine.id,
                "performer_id": staff[dose % len(staff)].id,
                "occurrence": when,
                "route_id": routes[dose % len(routes)].id,
                "site_id": sites[dose % len(sites)].id,
                "dose_quantity": 0.5,
                "lot_number": f"SAMPLE-LOT-{dose}",
                "expiration_date": date(2027, 1, 1),
                "state": "completed",
            }
        )
        env["ni.immunization.evaluation"].create(
            {
                "patient_id": patient.id,
                "encounter_id": enc.id,
                "immunization_id": immunization.id,
                "target_disease_id": disease.id,
                "dose_number": dose,
                "series_doses": disease.series_doses or 1,
                "dose_status": "valid" if valid or dose < doses else "not-valid",
                "dose_status_reason": False if valid or dose < doses else "Sample",
                "occurrence": when,
                "immunization_date": when.date(),
                "state": "completed",
            }
        )
ref("ni_patient.class_IMP").immunization = True

# --------------------------------------------------------------- services (P2-7)

calendar = company.resource_calendar_id
attendances = calendar.attendance_ids.sorted(lambda a: (a.dayofweek, a.hour_from))
company.write(
    {
        "service_calendar_id": calendar.id,
        "service_multi_category": True,
        "service_attendance_ids": [(6, 0, attendances.ids)],
    }
)
service_type = env["ni.service.type"].search([], limit=1, order="id")
shipped_categories = env["ni.service.category"].search([], order="id")
routine = ref("ni_service.categ_routine")
own_categories = env["ni.service.category"].create(
    [
        {"name": "Sample Activity", "code": "SAMPLE-ACT", "decoration": "info"},
        {"name": "Sample Therapy", "code": "SAMPLE-THER", "decoration": "success"},
    ]
)
SERVICES = [
    # name, category, extra categories, day of week, calendar, attendance index
    ("Sample Morning Exercise", own_categories[0], [], "0", True, [0]),
    ("Sample Art Class", own_categories[0], [own_categories[1]], "1", True, [2]),
    ("Sample Physio Session", own_categories[1], [], "2", True, [4]),
    ("Sample Lunch", routine, [], "0", False, [1]),
    ("Sample Music", shipped_categories[-1], [own_categories[0]], "3", True, []),
    ("Sample Legacy Walk", own_categories[1], [], "4", True, []),
]
services = env["ni.service"]
for index, (name, categ, extra, dow, cal, atts) in enumerate(SERVICES):
    services |= env["ni.service"].create(
        {
            "name": name,
            "code": f"SAMPLE-SVC-{index}",
            "company_id": company.id,
            "type_id": service_type.id,
            "category_id": categ.id,
            "category_ids": [(6, 0, [categ.id] + [c.id for c in extra])],
            "dayofweek": dow,
            "calendar": cal,
            "calendar_id": calendar.id,
            "attendance_ids": [(6, 0, [attendances[i].id for i in atts])],
            "duration": 1.0,
            "employee_id": staff[index % len(staff)].id,
            "employee_ids": [(6, 0, staff[:2].ids)],
            "specialty_ids": [(6, 0, jobs[:1].ids)],
        }
    )
# Services created before category_ids existed have only category_id: the old
# one-time cron (ir_cron_backfill_category_ids) fills ni_service_category_rel.
legacy = services[-2:]
env.flush_all()
env.cr.execute(
    "DELETE FROM ni_service_category_rel WHERE service_id IN %s", (tuple(legacy.ids),)
)
env.invalidate_all()

klass = ref("ni_patient.class_IMP")
klass.write(
    {
        "service_calendar_id": calendar.id,
        "service_ids": [(6, 0, services[:3].ids)],
        "communication": True,
    }
)

event_partners = patients[:3].mapped("partner_id") | staff[:1].mapped("work_contact_id")
EVENTS = [
    # service, start, stop, all day, planned patients
    (0, day(30, 9), day(30, 10), False, patients[:3]),
    (1, day(31, 13), day(31, 14, 30), False, patients[1:4]),
    (2, day(32, 0), day(32, 23, 59), True, patients[:1]),
    (4, day(33, 15), day(33, 16), False, env["ni.patient"]),
]
service_events = env["ni.service.event"]
for sidx, start, stop, allday, planned in EVENTS:
    service = services[sidx]
    vals = {
        "service_id": service.id,
        "service_ids": [(6, 0, service.ids)],
        "mode": "single",
        "start": start,
        "stop": stop,
        "allday": allday,
        "partner_ids": [(6, 0, event_partners.ids)],
        "plan_patient_ids": [(6, 0, planned.ids)],
        "service_category_id": service.category_id.id,
        "company_id": company.id,
    }
    if service.attendance_ids:
        vals.update(
            {
                "calendar_id": calendar.id,
                "attendance_ids": [(6, 0, service.attendance_ids[:1].ids)],
            }
        )
    service_events |= env["ni.service.event"].create(vals)

template = env["ni.timing.template"].search([], limit=1, order="id")
timing = env["ni.timing.timing"].create(
    {
        "template_id": template.id,
        "repeat_type": "dow",
        "day_of_week": [(6, 0, env["ni.timing.dow"].search([], limit=3).ids)],
        "time_type": "tod",
        "time_of_day": [(0, 0, {"start_time": 9.0, "end_time": 10.0})],
    }
)
REQUESTS = [
    ("draft", "proposal"),
    ("active", "order"),
    ("on-hold", "plan"),
    ("completed", "order"),
    ("revoked", "plan"),
]
requests = env["ni.service.request"]
for index, (state, intent) in enumerate(REQUESTS):
    enc = open_encounters[index % len(open_encounters)]
    requests |= env["ni.service.request"].create(
        {
            "name": f"Sample Request {index:02d}",
            "patient_id": enc.patient_id.id,
            "encounter_id": enc.id,
            "service_ids": [(6, 0, services[index % 3].ids)],
            "category_id": services[index % 3].category_id.id,
            "body_site_ids": [(6, 0, sites[:1].ids)],
            "intent": intent,
            "state": state,
            "timing_id": timing.id if index == 1 else False,
            "period_start": day(30 + index),
            "company_id": company.id,
        }
    )

for index, enc in enumerate(open_encounters[:3]):
    enc.resource_calendar_id = calendar
    for sidx in range(3):
        service = services[sidx]
        env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": enc.id,
                "attendance_id": service.attendance_ids[:1].id,
                "service_id": service.id,
                "service_event_id": service_events[sidx].id if sidx < 3 else False,
                "request_id": requests[1].id if sidx == 0 and index == 0 else False,
                "note": "Sample attendance",
            }
        )

params.set_param(MARKER, "1")
env.cr.commit()


def count(model):
    return env[model].with_context(active_test=False).search_count([])


print(
    "OK: P2 sample data loaded: "
    + ", ".join(
        f"{count(m)} {m}"
        for m in (
            "ni.condition",
            "ni.encounter.diagnosis",
            "ni.procedure",
            "ni.allergy",
            "ni.communication",
            "ni.document.ref",
            "ni.coverage",
            "ni.patient.related.person",
            "ni.immunization.evaluation",
            "ni.service",
            "ni.service.event",
            "ni.encounter.service.attendance",
            "ni.service.request",
            "res.users.role",
        )
    ),
    file=sys.stderr,
)
