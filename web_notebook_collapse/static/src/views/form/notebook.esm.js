/** @odoo-module */

import {Notebook} from "@web/core/notebook/notebook";
import {patch} from "web.utils";
import {scrollTo} from "@web/core/utils/scrolling";
import {onMounted, onWillDestroy, onWillUpdateProps, useEffect, useRef, useState} from "@odoo/owl";

function masonryLayout() {
    var $grid = document.querySelector(".o_notebook_collapse.row");
    if ($grid !== null) {
        /* eslint no-undef: 0 */
        var masonry = new Masonry($grid, {
            percentPosition: true,
        });
        masonry.layout();
    }
}

function AddListener() {
    var elems = document.querySelectorAll(".o_notebook_collapse.row .collapse");
    [].forEach.call(elems, function (el) {
        el.addEventListener("shown.bs.collapse", masonryLayout, false);
        el.addEventListener("hidden.bs.collapse", masonryLayout, false);
    });
    return elems;
}

patch(Notebook.prototype, "web_notebook_collapse.collapXpand", {
    setup() {
        this.activePane = useRef("activePane");
        this.anchorTarget = null;
        this.pages = this.computePages(this.props);
        this.state = useState({currentPage: null});
        this.state.currentPage = this.computeActivePage(this.props.defaultPage, true);
        const onAnchorClicked = this.onAnchorClicked.bind(this);
        this.env.bus.addEventListener("SCROLLER:ANCHOR_LINK_CLICKED", onAnchorClicked);
        useEffect(
            () => {
                this.props.onPageUpdate(this.state.currentPage);
                if (this.anchorTarget) {
                    const matchingEl = this.activePane.el.querySelector(`#${this.anchorTarget}`);
                    scrollTo(matchingEl, {isAnchor: true});
                    this.anchorTarget = null;
                }
            },
            () => [this.state.currentPage]
        );
        onWillUpdateProps((nextProps) => {
            const activateDefault = this.props.defaultPage !== nextProps.defaultPage || !this.defaultVisible;
            this.pages = this.computePages(nextProps);
            this.state.currentPage = this.computeActivePage(nextProps.defaultPage, activateDefault);
        });
        onWillDestroy(() => {
            this.env.bus.removeEventListener("SCROLLER:ANCHOR_LINK_CLICKED", onAnchorClicked);
        });
        onMounted(async () => {
            AddListener();
        });
    },
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
        masonryLayout();
    },
});
