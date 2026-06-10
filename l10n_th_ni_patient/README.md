# Patients Thai Localization (`l10n_th_ni_patient`)

## Purpose

Thai localization for core patient registration. The module validates Thai national identification numbers, formats them for
display, adds smart-card reading logs, and provides patient-side tooling for linking smart-card data back into Nirun patient
records.

## Main Components

- `ni.patient` extension Adds smart-card relations, a formatted `display_identification_id`, Thai-default nationality behavior,
  uniqueness checks, and Thai PIN validation through `python-stdnum`.
- `ni.patient.smartcard` New log model storing raw smart-card payloads, parsed demographic fields, card metadata, reader/device
  information, optional geolocation, and an image attachment through `image.mixin`.

## Views and Security

- Patient tree: shows `display_identification_id` to managers.
- Smart-card logs: adds a dedicated action, tree/form views, and a configuration menu entry.
- Security: creates `Smart Card Reader` group, model access, and a multi-company record rule for `ni.patient.smartcard`.

## Dependencies

- `ni_patient`
- Python package `stdnum`

## Notes

- Entering a Thai identification number triggers validation and uniqueness warnings on change.
- New patients with a matching identification number will automatically link to the latest smart-card log when possible.
- `ni.patient.smartcard.create()` parses the raw `card_data` string immediately and links an existing patient when the
  identifier is already known.
