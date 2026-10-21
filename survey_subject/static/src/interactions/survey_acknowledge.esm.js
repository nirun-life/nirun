import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

/**
 * "Acknowledge Results" on the end screen of a non-partner subject: close the
 * tab opened from the backend, or offer a link back when the browser keeps it.
 *
 * The end screen is inserted by the survey form after submit, so inline
 * scripts in the template do not run: this has to be an interaction.
 */
export class SurveyAcknowledge extends Interaction {
    static selector = ".o_survey_subject_acknowledge";

    dynamicContent = {
        ".o_survey_subject_acknowledge_button": {
            "t-on-click.prevent": this.onAcknowledge,
            "t-att-class": () => ({"d-none": this.acknowledged}),
        },
        ".o_survey_subject_return_link": {
            "t-att-class": () => ({"d-none": !this.acknowledged || !this.previousURL}),
        },
        ".o_survey_subject_return_link a": {
            "t-att-href": () => this.previousURL || "#",
        },
    };

    setup() {
        this.acknowledged = false;
        this.previousURL = document.referrer;
    }

    onAcknowledge() {
        this.acknowledged = true;
        window.close();
    }
}

registry
    .category("public.interactions")
    .add("survey_subject.survey_acknowledge", SurveyAcknowledge);
