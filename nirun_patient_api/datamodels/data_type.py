#  Copyright (c) 2021 NSTDA

from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class ResourceSchema(Datamodel):
    _name = "ni.rest.resource"

    id = fields.Integer(
        required=True,
        allow_none=False,
    )
    meta = NestedModel("ni.rest.meta")

    def _from(self, rec):
        self.id = rec.id
        self.meta = self.env.datamodels["ni.rest.meta"]()._from(rec)
        return self


class ReferenceSchema(Datamodel):
    _name = "ni.rest.reference"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=False, allow_none=True)

    def _from(self, rec):
        self.id = rec.id
        self.name = rec.name
        return self


class CodingSchema(Datamodel):
    _name = "ni.rest.coding"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    code = fields.String(required=False, allow_none=True)

    def _from(self, coding):
        self.id = coding.id
        self.name = coding.name
        if coding.code:
            self.code = coding.code
        return self


class CodingSearchSchema(Datamodel):
    _name = "ni.rest.coding.search"

    id = fields.Integer()
    name = fields.String()
    code = fields.String()
    limit = fields.Integer(missing=64)


class MetaSchema(Datamodel):
    _name = "ni.rest.meta"

    create_date = fields.DateTime()
    create_user = NestedModel("ni.rest.reference")
    write_date = fields.DateTime()
    write_user = NestedModel("ni.rest.reference")

    def _from(self, rec):
        self.create_date = rec.create_date
        if rec.create_uid:
            self.create_user = self.env.datamodels["ni.rest.reference"](
                id=rec.create_uid.id, name=rec.create_uid.name
            )
        self.write_date = rec.write_date
        if rec.write_uid:
            self.write_user = self.env.datamodels["ni.rest.reference"](
                id=rec.write_uid.id, name=rec.write_uid.name
            )
        return self
