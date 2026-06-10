# Partner - Location (`partner_location`)

## Purpose

Adds latitude/longitude-driven Google Maps direction links to partner and company forms.

## Main Components

- `res.partner` extension Computes `google_maps_url` from `partner_latitude` and `partner_longitude`, and exposes
  `action_google_maps_dir()`.
- `res.company` extension Reuses the partner location fields through related fields and proxies the same Google Maps action.

## Views

- Partner form: adds latitude/longitude inputs and a direction button before `vat`.
- Company form: adds the same controls before `vat`, backed by the company partner record.

## Dependencies

- `base`

## Notes

- The button is only visible when both coordinates are present and the computed Google Maps URL is available.
