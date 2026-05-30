// Copyright (c) 2026 NSTDA
import path from "node:path";
import {test} from "node:test";
import assert from "node:assert/strict";

import {buildLoginUrl, extractActionId, resolveConfig} from "./odoo_screenshot.mjs";

test("resolveConfig uses portable defaults and normalizes the base URL", () => {
  const config = resolveConfig(
    {
      ODOO_ADMIN_PWD: "x",
    },
    "C:\\Temp"
  );

  assert.equal(config.baseUrl, "http://localhost:16669");
  assert.equal(config.login, "admin");
  assert.equal(config.password, "x");
  assert.equal(config.outDir, path.resolve("C:\\Temp", "odoo_shots"));
});

test("resolveConfig keeps an optional database name and builds a db-aware login URL", () => {
  const config = resolveConfig(
    {
      ODOO_ADMIN_PWD: "x",
      ODOO_DB: "nirun-dc-master",
    },
    "/tmp"
  );

  assert.equal(config.database, "nirun-dc-master");
  assert.equal(buildLoginUrl(config), "http://localhost:16669/web/login?db=nirun-dc-master");
});

test("resolveConfig throws when the admin password is missing", () => {
  assert.throws(() => resolveConfig({}, "/tmp"), /ODOO_ADMIN_PWD/);
});

test("extractActionId returns the numeric id from a successful payload", () => {
  assert.equal(extractActionId({result: {id: 42}}, "ni_flag.ni_flag_action"), 42);
});

test("extractActionId throws when the RPC payload reports an error", () => {
  assert.throws(
    () =>
      extractActionId(
        {
          error: {
            message: "Odoo Server Error",
            data: {
              name: "builtins.KeyError",
              message: "Missing action",
            },
          },
        },
        "x_demo.missing_action"
      ),
    /Failed to resolve action x_demo\.missing_action\. Odoo Server Error\(builtins.KeyError\): Missing action/
  );
});

test("extractActionId throws when the XML action does not resolve", () => {
  assert.throws(() => extractActionId({result: null}, "ni_flag.missing_action"), /ni_flag\.missing_action/);
});
