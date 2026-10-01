#  Copyright (c) 2025-2026 NSTDA
from copy import deepcopy

from lxml import etree

from odoo import api, models

# Each shared fragment lives as plain, normal (translatable) content inside
# one donor model's own ir.ui.view - no separate template file, no custom
# translation code. Consumers below carry a matching empty
# <group name="..."/> placeholder that gets replaced with a deep copy of the
# donor's (already-translated) node.
_DOSAGE_FIELDS_DONORS = {
    "dosage_fields": "ni_medication.ni_medication_dosage_view_form",
    "dosage_administration_fields": "ni_medication.ni_medication_dosage_view_form",
    "dosage_page_content": "ni_medication.ni_medication_request_view_form",
}


class DosageFieldsMixin(models.AbstractModel):
    """Splices dosage fields donated by another model's real form view into
    any matching empty <group name="..."/> placeholder.

    Not standard Odoo view inheritance: inherit_id/xpath only works within
    one model, but these fields are shared across 5 different models, so we
    fetch a donor view's already-translated .arch via ORM instead.
    """

    _name = "ni.medication.dosage.fields.mixin"
    _description = "Shared Dosage Form Fields"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            # a donor's own raw arch can itself carry another placeholder
            # (e.g. request's dosage_page_content donates dosage_fields
            # onward from dosage) - loop until nothing more resolves
            resolved = True
            while resolved:
                resolved = False
                for name, donor_xmlid in _DOSAGE_FIELDS_DONORS.items():
                    placeholders = arch.xpath(f"//*[@name='{name}' and not(node())]")
                    if not placeholders:
                        continue
                    donor_arch = etree.fromstring(self.env.ref(donor_xmlid).arch)
                    fragments = donor_arch.xpath(f"//*[@name='{name}' and node()]")
                    if not fragments:
                        continue
                    for placeholder in placeholders:
                        placeholder.getparent().replace(
                            placeholder, deepcopy(fragments[0])
                        )
                        resolved = True
        return arch, view
