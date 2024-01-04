#  Copyright (c) 2024 NSTDA
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ExportDataLogger(models.AbstractModel):
    _name = "ni.export.data.logger"
    _description = "Export Data Logger Mixin"

    @api.model
    def export_data(self, fields_to_export):
        # Call super() to get the original export_data functionality
        _logger.info(
            "{}[{}] exporting {} {} records".format(
                self.env.user.name,
                self.env.user.id,
                self._name,
                len(self),
            )
        )

        return super().export_data(fields_to_export)
