/** @odoo-module **/

import {Component, onMounted, onWillUnmount, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {Dialog} from "@web/core/dialog/dialog";

/**
 * Dictation review modal: owns no logic of its own, only wires user
 * interaction to the shared DictationController passed in as a prop.
 * Confirming applies the buffered transcript and closes; any other way of
 * leaving the dialog (close button, backdrop/Escape) discards it instead.
 */
export class DictationModal extends Component {
    setup() {
        this.dictation = this.props.dictation;
        // Re-wrap the controller's reactive state so *this* component
        // subscribes to it too; reading through `this.dictation.state`
        // directly would not trigger a re-render here.
        this.state = useState(this.dictation.state);
        this.env.dialogData.close = () => this.discard();
        onMounted(() => this.dictation.start());
        onWillUnmount(() => this.dictation.stop());
    }

    get toggleDisabled() {
        return !this.state.selectedLanguage || Boolean(this.state.languageError);
    }

    get toggleIcon() {
        if (!this.dictation.isSupported) {
            return "fa-microphone-slash";
        }
        return this.state.listening ? "fa-pause" : "fa-microphone";
    }

    get statusLabel() {
        if (!this.dictation.isSupported) {
            return _t("Dictation is not supported in this browser.");
        }
        if (this.state.languageError) {
            return _t("Dictation languages could not be loaded.");
        }
        if (!this.state.languages.length) {
            return _t("No active dictation languages are available.");
        }
        return this.state.listening ? _t("Listening…") : _t("Paused");
    }

    get transcriptPreview() {
        const {transcript, interimTranscript} = this.state;
        if (!interimTranscript) {
            return transcript;
        }
        return transcript ? `${transcript} ${interimTranscript}` : interimTranscript;
    }

    get hasTranscript() {
        return Boolean(this.state.transcript.trim());
    }

    onToggle() {
        this.dictation.toggle();
    }

    onLanguageChange(event) {
        this.dictation.selectLanguage(event.target.value);
    }

    confirm(mode) {
        this.dictation.applyToField(mode);
        this.props.close();
    }

    discard() {
        this.dictation.discard();
        this.props.close();
    }
}
DictationModal.template = "web_speech_dictation.DictationModal";
DictationModal.components = {Dialog};
DictationModal.props = {
    close: Function,
    dictation: Object,
};
