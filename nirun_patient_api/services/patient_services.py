#  Copyright (c) 2021 NSTDA

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PartnerNewApiService(Component):
    _inherit = "base.rest.service"
    _name = "ni.rest.services.patient"
    _usage = "patient"
    _collection = "ni.rest.services"
    _description = """
        Partner API Services
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
        output_param=Datamodel("ni.rest.patient"),
    )
    def get(self, _id):
        """
        Get partner's information
        """
        partner = self._get(_id)
        return partner.datamodel()

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=Datamodel("ni.rest.patient.search"),
        output_param=Datamodel("ni.rest.patient", is_list=True),
    )
    def search(self, params):
        """
        Search for partners
        """
        domain = []
        if params.name:
            domain.append(("name", "ilike", params.name))
        if params.id:
            domain.append(("id", "=", params.id))
        if params.identification_id:
            domain.append(("identification_id", "=", params.identification_id))

        res = self.env["ni.patient"].search(domain, limit=params.limit)
        return res.datamodels()

    def _get(self, _id: int):
        return self.env["ni.patient"].browse(_id)
