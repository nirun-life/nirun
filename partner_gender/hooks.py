#  Copyright (c) 2022-2023 NSTDA


def post_init_hook(env):
    gender_title = {
        "male": env.ref("base.res_partner_title_mister"),
        "female": env.ref("base.res_partner_title_miss")
        + env.ref("base.res_partner_title_madam"),
    }
    partners = env["res.partner"].with_context(active_test=False)
    for gender, titles in list(gender_title.items()):
        partners.search([("title", "in", titles.ids)]).write({"gender": gender})
