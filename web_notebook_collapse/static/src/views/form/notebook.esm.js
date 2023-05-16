/** @odoo-module */

import {Notebook} from "@web/core/notebook/notebook";
import {patch} from "web.utils";

patch(Notebook.prototype, "web_notebook_collapse.collapXpand", {
    collapXpand(collapseState) {
        var elems = document.querySelectorAll(".collapse");
        if (collapseState) {
            document.getElementById("btnCollapse").classList.add("d-none");
            document.getElementById("btnExpand").classList.remove("d-none");
            [].forEach.call(elems, function (el) {
                el.classList.remove("show");
            });
        } else {
            document.getElementById("btnExpand").classList.add("d-none");
            document.getElementById("btnCollapse").classList.remove("d-none");
            [].forEach.call(elems, function (el) {
                el.classList.add("show");
            });
        }
    },
});
