import {SurveyForm} from "@survey/interactions/survey_form";
import {fadeIn} from "@survey/utils";
import {patch} from "@web/core/utils/patch";

patch(SurveyForm.prototype, {
    async nextScreen(nextScreenPromise) {
        this.el.querySelector(".o_survey_saving")?.classList.remove("d-none");
        nextScreenPromise.catch(() => {
            this.el.querySelector(".o_survey_saving")?.classList.add("d-none");
            const contentEl = this.el.querySelector(".o_survey_form_content");
            if (contentEl) {
                fadeIn(contentEl, 0);
            }
        });
        return super.nextScreen(...arguments);
    },

    onNextScreenDone() {
        this.el.querySelector(".o_survey_saving")?.classList.add("d-none");
        return super.onNextScreenDone(...arguments);
    },
});
