/** @odoo-module **/
/* global QUnit */

import {DictationController} from "@web_speech_dictation/dictation/dictation_controller";

class MockSpeechRecognition {
    constructor() {
        this.lang = "";
        this.continuous = false;
        this.interimResults = false;
        this.started = false;
        this.aborted = false;
        this.onresult = null;
        this.onerror = null;
        this.onend = null;
        MockSpeechRecognition.instances.push(this);
    }
    start() {
        this.started = true;
    }
    stop() {
        if (this.onend) {
            this.onend();
        }
    }
    abort() {
        this.aborted = true;
    }
}
MockSpeechRecognition.instances = [];

function finalResult(transcript) {
    const result = [{transcript}];
    result.isFinal = true;
    return {resultIndex: 0, results: [result]};
}

function interimResult(transcript) {
    const result = [{transcript}];
    result.isFinal = false;
    return {resultIndex: 0, results: [result]};
}

function makeState() {
    return {
        error: false,
        interimTranscript: "",
        languageError: false,
        languages: [{code: "en_US", recognitionCode: "en-US", name: "English"}],
        listening: false,
        selectedLanguage: "en_US",
        transcript: "",
    };
}

QUnit.module("web_speech_dictation", () => {
    QUnit.module("DictationController", (hooks) => {
        let originalRecognition = window.SpeechRecognition;

        hooks.beforeEach(() => {
            MockSpeechRecognition.instances = [];
            originalRecognition = window.SpeechRecognition;
            window.SpeechRecognition = MockSpeechRecognition;
        });
        hooks.afterEach(() => {
            window.SpeechRecognition = originalRecognition;
        });

        QUnit.test("buffer accumulates finalized speech across pause/resume cycles", (assert) => {
            const state = makeState();
            const controller = new DictationController({state, getTarget: () => null});

            controller.start();
            const firstSession = MockSpeechRecognition.instances.at(-1);
            firstSession.onresult(interimResult("hel"));
            assert.strictEqual(state.interimTranscript, "hel", "interim speech is shown while listening");
            firstSession.onresult(finalResult("hello "));
            assert.strictEqual(state.transcript, "hello ", "final speech lands in the buffer");

            // Pause: ends this recognition session.
            controller.stop();
            assert.strictEqual(state.listening, false);
            assert.strictEqual(state.interimTranscript, "", "unfinalized speech is dropped on pause");
            assert.strictEqual(state.transcript, "hello ", "buffered speech survives the pause");

            // Resume: a new underlying recognition instance.
            controller.start();
            const secondSession = MockSpeechRecognition.instances.at(-1);
            assert.notStrictEqual(secondSession, firstSession);
            secondSession.onresult(finalResult("world"));
            assert.strictEqual(state.transcript, "hello world", "buffer keeps accumulating after resume");
        });

        QUnit.test("applyToField('cursor') inserts at the snapshotted caret", (assert) => {
            const textarea = document.createElement("textarea");
            textarea.value = "before after";
            const state = makeState();
            state.transcript = "middle ";
            const controller = new DictationController({state, getTarget: () => textarea});
            controller.selectionSnapshot = {type: "textarea", start: 7, end: 7};

            controller.applyToField("cursor");

            assert.strictEqual(textarea.value, "before middle after");
            assert.strictEqual(state.transcript, "", "buffer is cleared after applying");
        });

        QUnit.test("applyToField('tail') appends at the end regardless of the snapshot", (assert) => {
            const textarea = document.createElement("textarea");
            textarea.value = "before after";
            const state = makeState();
            state.transcript = " more";
            const controller = new DictationController({state, getTarget: () => textarea});
            controller.selectionSnapshot = {type: "textarea", start: 0, end: 0};

            controller.applyToField("tail");

            assert.strictEqual(textarea.value, "before after more");
        });

        QUnit.test("applyToField('replace') overwrites the whole field", (assert) => {
            const textarea = document.createElement("textarea");
            textarea.value = "old content";
            const state = makeState();
            state.transcript = "new content";
            const controller = new DictationController({state, getTarget: () => textarea});

            controller.applyToField("replace");

            assert.strictEqual(textarea.value, "new content");
        });

        QUnit.test("discard clears the buffer without touching the field", (assert) => {
            const textarea = document.createElement("textarea");
            textarea.value = "untouched";
            const state = makeState();
            state.transcript = "would have been inserted";
            const controller = new DictationController({state, getTarget: () => textarea});

            controller.discard();

            assert.strictEqual(textarea.value, "untouched");
            assert.strictEqual(state.transcript, "");
            assert.strictEqual(state.interimTranscript, "");
        });

        QUnit.test("applyToField writes nothing when the buffer is empty", (assert) => {
            const textarea = document.createElement("textarea");
            textarea.value = "unchanged";
            const state = makeState();
            const controller = new DictationController({state, getTarget: () => textarea});

            controller.applyToField("tail");

            assert.strictEqual(textarea.value, "unchanged");
        });
    });
});
