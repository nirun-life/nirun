/** @odoo-module **/

import SurveyFormWidget from "survey.form";

SurveyFormWidget.include({
    _nextScreen(nextScreenPromise) {
        this.$(".o_survey_saving").removeClass("d-none");
        nextScreenPromise.catch(() => {
            this.$(".o_survey_saving").addClass("d-none");
            this.$(".o_survey_form_content").fadeIn(0);
        });
        return this._super(...arguments);
    },

    _onNextScreenDone() {
        this.$(".o_survey_saving").addClass("d-none");
        return this._super(...arguments);
    },
});
