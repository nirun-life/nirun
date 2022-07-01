#  Copyright (c) 2021 NSTDA

from odoo.addons.base_rest.controllers import main


class PatientApiController(main.RestController):
    _root_path = "/ni/"
    _collection_name = "ni.rest.services"
    _default_auth = "user"
