# Copyright (c) 2023 NSTDA
# Copyright 2019 Alexandre Díaz <dev@redneboa.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from colorsys import hls_to_rgb, rgb_to_hls

from odoo import fields, models

from ..utils import convert_to_image, image_to_rgb, n_rgb_to_hex


class Company(models.Model):
    _inherit = "res.company"

    brand_colors = fields.Serialized()
    primary_color = fields.Char(sparse="brand_colors", default="#8458c6")
    primary_dark_color = fields.Char(sparse="brand_colors", default="#6a3bb0")
    primary_light_color = fields.Char(sparse="brand_colors", default="#d8cbed")
    text_color = fields.Char("Text Color", sparse="brand_colors", default="#fff")

    def button_compute_color(self):
        self.ensure_one()
        values = self.default_get(
            ["color_navbar_bg", "color_navbar_bg_hover", "color_navbar_text"]
        )
        if self.logo:
            _r, _g, _b = image_to_rgb(convert_to_image(self.logo))
            # Make color 10% darker
            _h, _l, _s = rgb_to_hls(_r, _g, _b)
            _l = max(0, _l - 0.1)
            _rd, _gd, _bd = hls_to_rgb(_h, _l, _s)
            # Make color 35% lighter
            _l = min(1, _l + 0.35)
            _rl, _gl, _bl = hls_to_rgb(_h, _l, _s)
            # Calc. optimal text color (b/w)
            # Grayscale human vision perception (Rec. 709 values)
            _a = 1 - (0.2126 * _r + 0.7152 * _g + 0.0722 * _b)
            values.update(
                {
                    "primary_color": n_rgb_to_hex(_r, _g, _b),
                    "primary_dark_color": n_rgb_to_hex(_rd, _gd, _bd),
                    "primary_light_color": n_rgb_to_hex(_rl, _gl, _bl),
                    "text_color": "#000" if _a < 0.5 else "#fff",
                }
            )
        self.write(values)
