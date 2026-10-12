#  Copyright (c) 2026 NSTDA
"""Restore patient addresses that were 'private' partners up to 16.0.

Odoo 17 dropped the 'private' partner type. OpenUpgrade 17 turns those partners
into contacts and masks their address with '*****', keeping the original rows in
``ou_res_partner_private``. Patient and encounter "other addresses" were private
partners, so restore them from that copy and make them 'other' addresses.
"""


def migrate(cr, version):
    cr.execute("SELECT to_regclass('ou_res_partner_private')")
    if not cr.fetchone()[0]:
        return
    cr.execute(
        """
        UPDATE res_partner partner
        SET type = 'other',
            name = private.name,
            street = private.street,
            street2 = private.street2,
            city = private.city,
            zip = private.zip,
            state_id = private.state_id,
            country_id = private.country_id,
            phone = private.phone,
            mobile = private.mobile,
            email = private.email
        FROM ou_res_partner_private private
        WHERE partner.id = private.id
        AND partner.id IN (
            SELECT other_address_id FROM ni_patient
            WHERE other_address_id IS NOT NULL
            UNION
            SELECT other_address_id FROM ni_encounter
            WHERE other_address_id IS NOT NULL
        )
        """
    )
