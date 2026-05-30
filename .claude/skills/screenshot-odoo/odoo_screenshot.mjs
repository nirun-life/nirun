// Copyright (c) 2026 NSTDA
import fs from "node:fs/promises";
import {existsSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import {createRequire} from "node:module";
import {pathToFileURL} from "node:url";

const require = createRequire(import.meta.url);

export function resolveConfig(env = process.env, tempDir = os.tmpdir()) {
  const password = env.ODOO_ADMIN_PWD?.trim();
  if (!password) {
    throw new Error("Missing ODOO_ADMIN_PWD. Set the admin web password before running the screenshot helper.");
  }

  const baseUrl = (env.ODOO_BASE_URL || "http://localhost:16669").replace(/\/+$/, "");
  const database = env.ODOO_DB?.trim() || null;
  const login = env.ODOO_LOGIN || "admin";
  const outDir = path.resolve(env.ODOO_SHOTS_DIR || path.join(tempDir, "odoo_shots"));

  return {
    baseUrl,
    database,
    login,
    outDir,
    password,
    playwrightModule: env.PLAYWRIGHT_MODULE || "playwright",
  };
}

export function buildLoginUrl(config) {
  if (!config.database) {
    return `${config.baseUrl}/web/login`;
  }

  return `${config.baseUrl}/web/login?db=${encodeURIComponent(config.database)}`;
}

export function extractActionId(payload, xmlid) {
  if (payload?.error) {
    const rpcMessage = payload.error.message || "RPC error";
    const serverName = payload.error.data?.name;
    const serverMessage = payload.error.data?.message;
    const details = [rpcMessage];
    if (serverName) {
      details.push(`(${serverName})`);
    }
    if (serverMessage) {
      details.push(`: ${serverMessage}`);
    }
    throw new Error(`Failed to resolve action ${xmlid}. ${details.join("")}`);
  }

  const actionId = payload?.result?.id;
  if (!Number.isInteger(actionId)) {
    throw new Error(`Action XML ID did not resolve to a numeric action: ${xmlid}`);
  }

  return actionId;
}

export function loadPlaywright(playwrightModule = "playwright") {
  try {
    if (existsSync(playwrightModule)) {
      const resolutionRoot =
        path.basename(playwrightModule) === "playwright" ? path.dirname(playwrightModule) : playwrightModule;
      const resolvedModule = require.resolve("playwright", {
        paths: [resolutionRoot],
      });
      return require(resolvedModule);
    }

    return require(playwrightModule);
  } catch (error) {
    throw new Error(
      `Unable to load Playwright from "${playwrightModule}". Install the Node Playwright package or set PLAYWRIGHT_MODULE to a resolvable package path.\n` +
        `Original error: ${error.message}`
    );
  }
}

async function dismiss(page) {
  for (const selector of [".o_dialog .btn-primary", ".o_dialog button.btn"]) {
    try {
      const button = page.locator(selector).first();
      await button.waitFor({state: "visible", timeout: 400});
      await button.click();
      await page.waitForTimeout(200);
    } catch (error) {
      console.warn(`WARN dismiss failed for selector ${selector}: ${error.message}`);
    }
  }
}

async function screenshot(page, outDir, name, wait = 2000) {
  await page.waitForTimeout(wait);
  await dismiss(page);
  await page.waitForTimeout(300);

  const shotPath = path.resolve(outDir, `${name}.png`);
  await page.screenshot({path: shotPath, fullPage: false});
  console.log(`OK ${name}`);
  return shotPath;
}

async function login(page, config) {
  await page.goto(buildLoginUrl(config));
  await page.waitForLoadState("domcontentloaded");
  if (config.database) {
    const databaseField = page.locator("input[name=db]");
    if ((await databaseField.count()) > 0) {
      await databaseField.fill(config.database);
    }
  }
  await page.fill("input[name=login]", config.login);
  await page.fill("input[name=password]", config.password);
  await page.locator("button[type=submit]").click();
  await page.waitForTimeout(4000);

  if (page.url().includes("/web/login")) {
    throw new Error("Login failed. Check ODOO_LOGIN, ODOO_ADMIN_PWD, and ODOO_DB.");
  }
}

async function actionId(page, xmlid) {
  const payload = await page.evaluate(async (currentXmlId) => {
    const response = await fetch("/web/action/load", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        id: 1,
        params: {
          action_id: currentXmlId,
        },
      }),
    });
    return response.json();
  }, xmlid);

  return extractActionId(payload, xmlid);
}

export async function run(customEnv = process.env) {
  const config = resolveConfig(customEnv);
  const {chromium} = loadPlaywright(config.playwrightModule);

  await fs.mkdir(config.outDir, {recursive: true});

  const shots = [];
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 900}});
    await login(page, config);

    // ------- VIEWS -------
    // Replace or extend this section per task.
    // Pattern:
    //   const aid = await actionId(page, "module.action_xmlid");
    //   await page.goto(`${config.baseUrl}/web#action=${aid}`);
    //   await page.waitForLoadState("domcontentloaded");
    //   shots.push(await screenshot(page, config.outDir, "descriptive_name"));

    console.log("WARN no views configured in the helper copy");
  } finally {
    await browser.close();
  }

  console.log("---");
  for (const shotPath of shots) {
    console.log(shotPath);
  }
}

export {actionId, dismiss, login, screenshot};

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  run().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
