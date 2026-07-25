/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import {TextField} from "@web/views/fields/text/text_field";
import {onWillUnmount, useState} from "@odoo/owl";
import {DictationController} from "../dictation/dictation_controller";
import {DictationModal} from "../dictation/dictation_modal";

patch(TextField.prototype, "web_speech_dictation.TextField", {
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
        });
        this.dictation = new DictationController({
            state: this.dictationState,
            getTarget: () => this.textareaRef.el,
        });
        this.dictation.loadLanguages(orm, user.lang);
        onWillUnmount(() => this.dictation.destroy());
    },

    onDictationClick() {
        this.dictation.snapshotSelection();
        this.dictation.syncSelectedLanguage();
        this.dialog.add(DictationModal, {dictation: this.dictation});
    },

    get dictationSupported() {
        return this.dictation.isSupported;
    },

    get dictationTooltip() {
        if (!this.dictationSupported) {
            return _t("Speech dictation is not supported in this browser.");
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
