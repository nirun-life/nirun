#  Copyright (c) 2021 Piruin P.

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class ObservationService(Component):
    _inherit = "base.rest.service"
    _name = "ni.rest.services.observation"
    _usage = "observation"
    _collection = "ni.rest.services"
    _description = """
        Observation Services
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
        output_param=Datamodel("ni.rest.observation"),
    )
    def get(self, _id):
        """
        Get observation's information
        """
        res = self._get(_id)
        return res.datamodel()

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=Datamodel("ni.rest.observation.search"),
        output_param=Datamodel("ni.rest.observation", is_list=True),
    )
    def search(self, ob_search_param):
        """
        Search for Observation
        """
        domain = []
        if ob_search_param.patient_id:
            domain.append(("patient_id", "=", ob_search_param.patient_id))
        if ob_search_param.id:
            domain.append(("id", "=", ob_search_param.id))
        res = self.env["ni.observation"].search(domain, limit=ob_search_param.limit)
        return res.datamodels()

    @restapi.method(
        [(["/"], "POST")],
        input_param=Datamodel("ni.rest.observation"),
        output_param=Datamodel("ni.rest.observation"),
    )
    # pylint:disable=method-required-super
    def create(self, params):
        """
        Create a new observation
        """
        ob = self.env["ni.observation"].create(self._prepare_params(params.dump()))
        return ob.datamodel()

    def _get(self, _id: int):
        return self.env["ni.observation"].browse(_id)

    def _prepare_params(self, params):
        for key in ["patient", "encounter"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        if "identifier" in params:
            params["name"] = params.pop("identifier")
        params["effective_date"] = params.get("effective_date").replace("T", " ", 1)
        params["lines"] = [
            (0, 0, self._prepare_line_params(l)) for l in params.get("lines")
        ]
        return params

    def _prepare_line_params(self, params):
        for ref in ["type"]:
            if ref in params:
                val = params.pop(ref)
                if val.get("id"):
                    params["%s_id" % ref] = val["id"]
        for rm in ["unit", "interpretation"]:
            if rm in params:
                params.pop(rm)
        return params
