/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import {HtmlField} from "@web_editor/js/backend/html_field";
import {onWillUnmount, useState} from "@odoo/owl";
import {DictationController} from "../dictation/dictation_controller";
import {DictationModal} from "../dictation/dictation_modal";

patch(HtmlField.prototype, "web_speech_dictation.HtmlField", {
    setup() {
        this._super(...arguments);
        const orm = useService("orm");
        const user = useService("user");
        this.dialog = useService("dialog");
        this.dictationState = useState({
            error: false,
            interimTranscript: "",
            languageError: false,
            languages: [],
            listening: false,
            selectedLanguage: "",
            transcript: "",
            wysiwygReady: false,
        });
        this.dictation = new DictationController({
            state: this.dictationState,
            getTarget: () => this.codeViewRef.el || (this.wysiwyg && this.wysiwyg.$editable && this.wysiwyg.$editable[0]),
            applyTranscript: (transcript, mode, snapshot) => this.applyDictationTranscript(transcript, mode, snapshot),
        });
        this.dictation.loadLanguages(orm, user.lang);
        onWillUnmount(() => this.dictation.destroy());
    },

    async startWysiwyg(wysiwyg) {
        await this._super(wysiwyg);
        // This.wysiwyg is a plain instance property, not reactive state, so
        // without this OWL never re-renders once the editor becomes ready
        // and the mic button (bound to dictationReady) stays stuck disabled
        // from whatever it evaluated to on the last reactive render.
        this.dictationState.wysiwygReady = true;
    },

    applyDictationTranscript(transcript, mode, snapshot) {
        if (this.state.showCodeView) {
            if (this.codeViewRef.el) {
                this.dictation.writeTextarea(this.codeViewRef.el, transcript, mode, snapshot);
            }
            return;
        }
        if (!this.wysiwyg || !this.wysiwyg.odooEditor) {
            return;
        }
        const editable = this.wysiwyg.$editable[0];
        this.wysiwyg.focus();
        if (mode !== "cursor") {
            const range = document.createRange();
            range.selectNodeContents(editable);
            if (mode === "tail") {
                range.collapse(false);
            }
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
        this.wysiwyg.odooEditor.execCommand("insert", document.createTextNode(transcript));
    },

    onDictationClick() {
        this.dictation.snapshotSelection();
        this.dictation.syncSelectedLanguage();
        this.dialog.add(DictationModal, {dictation: this.dictation});
    },

    get dictationSupported() {
        return this.dictation.isSupported;
    },

    get dictationReady() {
        return this.state.showCodeView ? Boolean(this.codeViewRef.el) : this.dictationState.wysiwygReady;
    },

    get dictationTooltip() {
        if (!this.dictationSupported) {
            return _t("Speech dictation is not supported in this browser.");
        }
        if (!this.dictationReady) {
            return _t("The editor is still loading.");
        }
        if (this.dictationState.languageError) {
            return _t("Dictation languages could not be loaded.");
        }
        if (!this.dictationState.languages.length) {
            return _t("No active dictation languages are available.");
        }
        return _t("Dictate");
    },
});
