// SPDX-License-Identifier: MIT OR Apache-2.0
// Reads [{input}, ...] JSON on stdin and prints [{ok, json, markdown} | {ok:false, code}].
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const HoloPlan = require('../../site/plan.js');
const template = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'plan_template.json'), 'utf8'));
const inputs = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = inputs.map(input => {
  try {
    const plan = HoloPlan.generatePlan(template, input);
    return { ok: true, json: HoloPlan.planToJson(plan), markdown: HoloPlan.planToMarkdown(plan) };
  } catch (e) {
    if (e.name !== 'PlanInputError') throw e;
    return { ok: false, code: e.code };
  }
});
process.stdout.write(JSON.stringify(out));
