#  Copyright (c) 2021 Piruin P.

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PartnerNewApiService(Component):
    _inherit = "base.rest.service"
    _name = "ni.rest.services.patient"
    _usage = "patient"
    _collection = "ni.rest.services"
    _description = """
        Partner New API Services
        Services developed with the new api provided by base_rest
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
        output_param=Datamodel("ni.rest.patient.short", is_list=True),
    )
    def search(self, partner_search_param):
        """
        Search for partners
        :param partner_search_param: An instance of partner.search.param
        :return: List of partner.short.info
        """
        domain = []
        if partner_search_param.name:
            domain.append(("name", "like", partner_search_param.name))
        if partner_search_param.id:
            domain.append(("id", "=", partner_search_param.id))
        if partner_search_param.identification_id:
            domain.append(
                ("identification_id", "=", partner_search_param.identification_id)
            )

        res = self.env["ni.patient"].search(domain)
        return res.datamodel(mode="short")

    # The following method are 'private' and should be never never NEVER call
    # from the controller.

    def _get(self, _id: int):
        return self.env["ni.patient"].browse(_id)
