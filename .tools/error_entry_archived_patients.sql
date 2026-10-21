-- Copyright (c) 2026 NSTDA
--
-- Patients that "Error Entry" may have archived by mistake (nirun-life/nirun#135, F4).
--
-- From b25bb607 (2023-12-20) until the 16.0 fix, marking an encounter as
-- entered-in-error also archived its patient, and through _inherits that hid all
-- of the patient's encounters. The archive wizard always sets state_reason_id, so
-- an archived patient without one that has an entered-in-error encounter is a
-- likely victim.
--
-- Read-only. Nothing is reactivated automatically: support checks each patient
-- and reactivates the confirmed ones from the UI, so the change is tracked in the
-- chatter. Run it before the OpenUpgrade 16 -> 17 step:
--
--     psql -d <database> -f .tools/error_entry_archived_patients.sql
--
-- The output holds patient identifiers. Share it only through support's own
-- channel, never in an issue, a pull request or a log attached to one.

SELECT p.id, p.identifier
FROM ni_patient p
WHERE p.active IS NOT TRUE
  AND p.state_reason_id IS NULL
  AND EXISTS (
      SELECT 1 FROM ni_encounter e
      WHERE e.patient_id = p.id AND e.state = 'entered-in-error'
  )
ORDER BY p.id;
