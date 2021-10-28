#  Copyright (c) 2021 Piruin P.

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class ObservationService(Component):
    _inherit = "base.rest.service"
    _name = "ni.rest.services.observation.type"
    _usage = "observation-type"
    _collection = "ni.rest.services"
    _description = """
        Observation Types Services
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
        output_param=Datamodel("ni.rest.coding"),
    )
    def get(self, _id):
        """
        Get types of observation
        """
        res = self._get(_id)
        return (
            self.env.datamodels["ni.rest.coding"](
                id=res.id, name=res.name, code=res.code or None
            )
            if res
            else None
        )

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=Datamodel("ni.rest.coding.search"),
        output_param=Datamodel("ni.rest.coding", is_list=True),
    )
    def search(self, params):
        """
        Search types of Observation
        """
        domain = []
        if params.code:
            domain.append(("code", "=", params.code))
        if params.name:
            domain.append(("name", "ilike", params.name))
        if params.id:
            domain.append(("id", "=", params.id))
        res = self.env["ni.observation.type"].search(domain, limit=params.limit)
        schema = self.env.datamodels["ni.rest.coding"]
        return [schema(id=rec.id, name=rec.name, code=rec.code) for rec in res]

    def _get(self, _id: int):
        return self.env["ni.observation.type"].browse(_id)
