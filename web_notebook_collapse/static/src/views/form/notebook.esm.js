/** @odoo-module */

import {Notebook} from "@web/core/notebook/notebook";
import {patch} from "web.utils";

patch(Notebook.prototype, "web_notebook_collapse.collapXpand", {
    collapXpand(collapseState) {
        var elems = document.querySelectorAll(".o_notebook_collapse .collapse");
        var btns = document.querySelectorAll(".accordion-button.o_notebook_header_button");
        if (collapseState) {
            [].forEach.call(elems, function (el) {
                el.classList.remove("show");
            });
            [].forEach.call(btns, function (btn) {
                btn.classList.add("collapsed");
            });
        } else {
            [].forEach.call(elems, function (el) {
                el.classList.add("show");
            });
            [].forEach.call(btns, function (btn) {
                btn.classList.remove("collapsed");
            });
        }
    },
});
