#  Copyright (c) 2023 NSTDA
import json
import logging
from datetime import datetime

import requests
from requests.exceptions import RequestException

from odoo import fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

TEST_BASE_URL = "https://test.nhso.go.th"
PROD_BASE_URL = "https://pucws.nhso.go.th"
PATH = "/authencodeapi/CheckAuthenStatus"


class Reception(models.Model):
    _inherit = "ni.reception"

    claim_code = fields.Char()
    name = fields.Char(required=False)

    def action_nhso_authen(self):
        service_code = "PG0150001"
        api_url = f"{TEST_BASE_URL}{PATH}"
        try:
            response = requests.get(
                f"{api_url}?personalId={self.identification_id}&serviceDate={self.period_start.date()}&serviceCode={service_code}"
            )
            response.raise_for_status()

            data = response.json() if not self._test_env() else self.dummy_json()

            if "statusAuthen" not in data or not data.get("statusAuthen"):
                raise RequestException(data["statusMessage"])

            cov_main = self.env["ni.coverage.type"].search(
                [("code", "=", data["mainInscl"])], limit=1
            )
            cov_sub = self.env["ni.coverage.type"].search(
                [("code", "=", data["subInscl"])], limit=1
            )
            prov = self.env["res.country.state"].search(
                [
                    ("country_id.code", "=", "TH"),
                    ("code", "=", f"TH-{data['provinceCode'][:2]}"),
                ],
                limit=1,
            )
            self.update(
                {
                    "identification_id": data["personalId"],
                    "name": data["fullName"],
                    "gender": "male" if data["sex"] == "ชาย" else "female",
                    "coverage_type_ids": [
                        fields.Command.set([cov_sub.id or cov_main.id])
                    ],
                    "state_id": prov.id,
                }
            )

            service_hist = data["serviceHistories"]
            for hist in service_hist:
                service_data = datetime.strptime(
                    hist["serviceDate"], "%Y-%m-%dT%H:%M:%S"
                )
                if service_data.date() != self.period_start.date():
                    continue
                if hist["serviceCode"] != service_code:
                    continue
                if hist["hcode"] != self.company_id.hcode:
                    continue

                self.write({"claim_code": hist["claimCode"]})
                break

            return data
        except RequestException as err:
            raise ValidationError(err) from err

    def _test_env(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_th_nhso_authen.test_env", default=False)
        )

    def dummy_json(self):
        data = """
{
    "statusAuthen": true,
    "statusMessage": "พบข้อมูลการ authen",
    "personalId": "14799XXXXXXX6",
    "firstName": "อัมพร",
    "lastName": "จาเพียญราชา",
    "fullName": "อัมพร จาเพียญราชา",
    "sex": "ชาย",
    "age": "23 ปี 7 เดือน 8 วัน",
    "nationCode": "099",
    "nationDescription": "ไทย",
    "provinceCode": "4700",
    "provinceName": "สกลนคร",
    "mainInscl": "UCS",
    "mainInsclName": "สิทธิหลักประกันสุขภาพแห่งชาติ",
    "subInscl": "89",
    "subInsclName": "ช่วงอายุ 12-59 ปี",
    "serviceHistories": [
        {
            "hcode": "13814",
            "hname": "รพ.ศิริราช",
            "serviceDate": "2023-10-06T15:16:38",
            "claimCode": "PP1015363237",
            "serviceCode": "PG0150001",
            "serviceName": "คัดกรองโควิดแบบ Antigen"
        },
        {
            "hcode": "13814",
            "hname": "รพ.ศิริราช",
            "serviceDate": "2021-12-20T16:50:57",
            "claimCode": "PP1015363259",
            "serviceCode": "PG0010066",
            "serviceName": "คัดกรองโควิดแบบ RTPCR"
        }
    ]
}
        """
        return json.loads(data)
