#  Copyright (c) 2021 Piruin P.

from odoo import models


class Country(models.Model):
    _inherit = "res.country"

    def datamodel(self):
        res = self.env.datamodels["ni.rest.coding"](partial=True)
        res._from(self)
        return res


class Company(models.Model):
    _inherit = "res.company"

    def datamodel(self):
        res = self.env.datamodels["ni.rest.reference"](partial=True)
        res._from(self)
        return res
