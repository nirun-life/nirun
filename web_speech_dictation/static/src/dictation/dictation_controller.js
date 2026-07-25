/** @odoo-module **/

import {browser} from "@web/core/browser/browser";

const LANGUAGE_STORAGE_KEY = "web_speech_dictation.language";

/**
 * Small, UI-framework-independent wrapper around the browser recognition API.
 * Recognized speech accumulates in `state.transcript` across as many
 * pause/resume cycles as the caller runs; nothing reaches the target field
 * until `applyToField` is called. Field widgets provide a target element (or
 * a custom `applyTranscript` writer, for rich-text editors) and a reactive
 * state object; all recognition, buffering, language persistence, and
 * cursor/selection handling remains here.
 */
export class DictationController {
    constructor({state, getTarget, applyTranscript}) {
        this.state = state;
        this.getTarget = getTarget;
        this.applyTranscript = applyTranscript;
        this.recognition = null;
        this.selectionSnapshot = null;
    }

    get Recognition() {
        return window.SpeechRecognition || window.webkitSpeechRecognition;
    }

    get isSupported() {
        return Boolean(this.Recognition);
    }

    async loadLanguages(orm, defaultLanguage) {
        try {
            const languages = await orm.searchRead("res.lang", [["active", "=", true]], ["name", "code"]);
            this.state.languages = languages
                .map((language) => ({
                    code: language.code,
                    recognitionCode: language.code.replace("_", "-"),
                    name: language.name,
                }))
                .sort((left, right) => left.name.localeCompare(right.name));

            const rememberedLanguage = browser.localStorage.getItem(LANGUAGE_STORAGE_KEY);
            const selectedLanguage = this.state.languages.find((language) => language.code === rememberedLanguage);
            const userLanguage = this.state.languages.find((language) => language.code === defaultLanguage);
            this.state.selectedLanguage = (selectedLanguage || userLanguage || this.state.languages[0] || {}).code || "";
        } catch (_error) {
            this.state.languageError = true;
        }
    }

    selectLanguage(languageCode) {
        this.state.selectedLanguage = languageCode;
        browser.localStorage.setItem(LANGUAGE_STORAGE_KEY, languageCode);
    }

    /**
     * Re-reads the remembered language before opening the modal, so a change
     * made from another field's dictation session is picked up here too.
     */
    syncSelectedLanguage() {
        const rememberedLanguage = browser.localStorage.getItem(LANGUAGE_STORAGE_KEY);
        const selectedLanguage = this.state.languages.find((language) => language.code === rememberedLanguage);
        if (selectedLanguage) {
            this.state.selectedLanguage = selectedLanguage.code;
        }
    }

    /**
     * Captures the caller's current caret/selection so it can still be used
     * as the "insert at cursor" target after focus has moved to the modal.
     */
    snapshotSelection() {
        const target = this.getTarget();
        if (!target) {
            this.selectionSnapshot = null;
        } else if (target.isContentEditable) {
            const selection = window.getSelection();
            const range = document.createRange();
            if (selection.rangeCount && target.contains(selection.getRangeAt(0).commonAncestorContainer)) {
                range.setStart(selection.getRangeAt(0).startContainer, selection.getRangeAt(0).startOffset);
                range.setEnd(selection.getRangeAt(0).endContainer, selection.getRangeAt(0).endOffset);
            } else {
                range.selectNodeContents(target);
                range.collapse(false);
            }
            this.selectionSnapshot = {type: "range", range};
        } else {
            this.selectionSnapshot = {type: "textarea", start: target.selectionStart, end: target.selectionEnd};
        }
    }

    toggle() {
        if (this.state.listening) {
            this.stop();
        } else {
            this.start();
        }
    }

    start() {
        if (!this.isSupported || !this.state.selectedLanguage) {
            return;
        }
        const recognition = new this.Recognition();
        const language = this.state.languages.find((candidate) => candidate.code === this.state.selectedLanguage);
        recognition.lang = language.recognitionCode;
        // Keep the session alive through short pauses; the user can still end
        // dictation at any time with the pause button.
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = (event) => this.onResult(event);
        recognition.onerror = () => {
            this.state.error = true;
        };
        recognition.onend = () => this.clearRecognition(recognition);

        this.recognition = recognition;
        this.state.error = false;
        this.state.listening = true;
        try {
            recognition.start();
        } catch (_error) {
            this.clearRecognition(recognition);
            this.state.error = true;
        }
    }

    stop() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    destroy() {
        if (this.recognition) {
            this.recognition.onend = null;
            this.recognition.abort();
        }
        this.recognition = null;
    }

    onResult(event) {
        let interimTranscript = "";
        for (let index = event.resultIndex; index < event.results.length; index++) {
            const result = event.results[index];
            if (result.isFinal) {
                this.state.transcript += result[0].transcript;
            } else {
                interimTranscript += result[0].transcript;
            }
        }
        this.state.interimTranscript = interimTranscript;
    }

    clearRecognition(recognition) {
        if (this.recognition !== recognition) {
            return;
        }
        this.recognition = null;
        this.state.listening = false;
        // Interim (non-final) speech was never committed to the buffer by the
        // browser, so it's not recoverable on pause; only accumulated finals
        // (state.transcript) survive across pause/resume cycles.
        this.state.interimTranscript = "";
    }

    /** Ends the session and throws away everything dictated so far. */
    discard() {
        this.endSession();
    }

    // Writes the buffered transcript to the target using the chosen insert mode, then ends the session.
    applyToField(mode) {
        const transcript = this.state.transcript.trim();
        const snapshot = this.selectionSnapshot;
        this.endSession();
        if (!transcript) {
            return;
        }
        if (this.applyTranscript) {
            this.applyTranscript(transcript, mode, snapshot);
            return;
        }
        const target = this.getTarget();
        if (!target) {
            return;
        }
        if (target.isContentEditable) {
            this.writeContentEditable(target, transcript, mode, snapshot);
        } else {
            this.writeTextarea(target, transcript, mode, snapshot);
        }
    }

    endSession() {
        this.stop();
        this.state.transcript = "";
        this.state.interimTranscript = "";
        this.selectionSnapshot = null;
    }

    writeTextarea(target, transcript, mode, snapshot) {
        const value = target.value;
        let start = value.length;
        let end = value.length;
        if (mode === "replace") {
            start = 0;
        } else if (mode === "cursor" && snapshot && snapshot.type === "textarea") {
            start = snapshot.start;
            end = snapshot.end;
        }
        target.value = `${value.slice(0, start)}${transcript}${value.slice(end)}`;
        const caret = start + transcript.length;
        target.setSelectionRange(caret, caret);
        target.dispatchEvent(new Event("input", {bubbles: true}));
        target.focus();
    }

    writeContentEditable(target, transcript, mode, snapshot) {
        const range = document.createRange();
        if (mode === "replace") {
            range.selectNodeContents(target);
        } else if (mode === "cursor" && snapshot && snapshot.type === "range") {
            range.setStart(snapshot.range.startContainer, snapshot.range.startOffset);
            range.setEnd(snapshot.range.endContainer, snapshot.range.endOffset);
        } else {
            range.selectNodeContents(target);
            range.collapse(false);
        }
        range.deleteContents();
        const textNode = document.createTextNode(transcript);
        range.insertNode(textNode);
        range.setStartAfter(textNode);
        range.collapse(true);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        target.dispatchEvent(new Event("input", {bubbles: true}));
        target.focus();
    }
}
