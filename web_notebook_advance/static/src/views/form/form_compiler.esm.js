/** @odoo-module */

import {append, createElement, getTag} from "@web/core/utils/xml";
import {toStringExpression} from "@web/views/utils";
import {getModifier} from "@web/views/view_compiler";
import {FormCompiler} from "@web/views/form/form_compiler";
import {patch} from "web.utils";

/**
 * @param {Record<String, any>} obj
 * @returns {String}
 */
export function objectToString(obj) {
    return `{${Object.entries(obj)
        .map((t) => t.join(":"))
        .join(",")}}`;
}

patch(FormCompiler.prototype, "web_notebook_advance.compile_notebook", {
    compileNotebook(el, params) {
        const noteBookId = this.noteBookId++;
        const noteBook = createElement("Notebook");
        const pageAnchors = [...document.querySelectorAll("[href^=\\#]")]
            .map((a) => CSS.escape(a.getAttribute("href").substring(1)))
            .filter((a) => a.length);
        const noteBookAnchors = {};

        if (el.hasAttribute("class")) {
            noteBook.setAttribute("className", toStringExpression(el.getAttribute("class")));
            el.removeAttribute("class");
        }

        noteBook.setAttribute("defaultPage", `props.record.isNew ? undefined : props.activeNotebookPages[${noteBookId}]`);
        noteBook.setAttribute("onPageUpdate", `(page) => this.props.onNotebookPageChange(${noteBookId}, page)`);

        let index = 1;
        for (const child of el.children) {
            if (getTag(child, true) !== "page") {
                continue;
            }
            const invisible = getModifier(child, "invisible");
            if (this.isAlwaysInvisible(invisible, params)) {
                continue;
            }

            const pageSlot = createElement("t");
            append(noteBook, pageSlot);

            const pageId = `page_${this.id++}`;
            const pageTitle = toStringExpression(child.getAttribute("string") || child.getAttribute("name") || "");
            const pageNodeName = toStringExpression(child.getAttribute("name") || "");

            pageSlot.setAttribute("t-set-slot", pageId);
            pageSlot.setAttribute("title", pageTitle);
            pageSlot.setAttribute("name", pageNodeName);
            if (child.className) {
                pageSlot.setAttribute("className", `"${child.className}"`);
            }

            if (child.getAttribute("autofocus") === "autofocus") {
                noteBook.setAttribute(
                    "defaultPage",
                    `props.record.isNew ? "${pageId}" : (props.activeNotebookPages[${noteBookId}] || "${pageId}")`
                );
            }

            for (const anchor of child.querySelectorAll("[href^=\\#]")) {
                const anchorValue = CSS.escape(anchor.getAttribute("href").substring(1));
                if (!anchorValue.length) {
                    continue;
                }
                pageAnchors.push(anchorValue);
                noteBookAnchors[anchorValue] = {
                    origin: `'${pageId}'`,
                };
            }
            // eslint-disable-next-line
            let isVisible;
            if (typeof invisible === "boolean") {
                isVisible = `${!invisible}`;
            } else {
                isVisible = `!evalDomainFromRecord(props.record,${JSON.stringify(invisible)})`;
            }
            pageSlot.setAttribute("isVisible", isVisible);

            for (const contents of child.children) {
                append(pageSlot, this.compileNode(contents, {...params, currentSlot: pageSlot}));
            }

            // [web_notebook_advance] === start
            if (child.getAttribute("info")) {
                const info = toStringExpression(child.getAttribute("info"));
                pageSlot.setAttribute("info", `props.record.data[${info}]`);
            }
            if (child.getAttribute("badge")) {
                const badge = toStringExpression(child.getAttribute("badge"));
                pageSlot.setAttribute("badge", `props.record.data[${badge}]`);
            }

            const pageIcon = toStringExpression(child.getAttribute("icon") || "");
            pageSlot.setAttribute("icon", pageIcon);
            pageSlot.setAttribute("index", index);
            index += 1;
        }
        noteBook.setAttribute("orientation", toStringExpression(el.getAttribute("orientation") || "horizontal"));
        // [web_notebook_advance] === end

        if (pageAnchors.length) {
            // If anchors from the page are targetting an element
            // present in the notebook, it must be aware of the
            // page that contains the corresponding element
            for (const anchor of pageAnchors) {
                let pageId = 1;
                for (const child of el.children) {
                    if (child.querySelector(`#${anchor}`)) {
                        noteBookAnchors[anchor].target = `'page_${pageId}'`;
                        noteBookAnchors[anchor] = objectToString(noteBookAnchors[anchor]);
                        break;
                    }
                    pageId++;
                }
            }
            noteBook.setAttribute("anchors", objectToString(noteBookAnchors));
        }

        return noteBook;
    },
});
