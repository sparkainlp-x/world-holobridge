// SPDX-License-Identifier: MIT OR Apache-2.0
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const HoloPlan = require('../../site/plan.js');
const { Node, fakeDocument } = require('./fake_dom.js');

const root = path.resolve(__dirname, '..', '..');
const template = JSON.parse(fs.readFileSync(path.join(root, 'plan_template.json'), 'utf8'));
const XSS = '<img src=x onerror=alert(1)><script>alert(2)</script>';

test('plan contains city and country and every section', () => {
  const plan = HoloPlan.generatePlan(template, { city: 'Moncton', country: 'Canada', region: 'NB' });
  assert.equal(plan.location.display, 'Moncton, NB, Canada');
  assert.match(plan.title, /Moncton, NB, Canada/);
  assert.deepEqual(plan.sections.map(s => s.id), [
    'indigenous_rights_holders', 'advisory_circle', 'protocols', 'consent', 'accessibility',
    'payment', 'incidents', 'ai_use', 'timeline', 'evaluation', 'legal']);
});

test('user input is rendered as text only (XSS-safe)', () => {
  const plan = HoloPlan.generatePlan(template, { city: XSS, country: '"><svg onload=alert(3)>', language: 'fr' });
  const container = new Node('div');
  HoloPlan.renderPlan(plan, container, fakeDocument);
  const html = container.toHTML();
  assert.ok(!html.includes('<img'), 'raw <img> must not appear');
  assert.ok(!html.includes('<script'), 'raw <script> must not appear');
  assert.ok(!html.includes('<svg'), 'raw <svg> must not appear');
  assert.ok(html.includes('&lt;img src=x onerror=alert(1)&gt;'));
  const tags = new Set(container.allTags());
  for (const tag of tags) assert.ok(['div', 'article', 'h2', 'h3', 'p', 'section', 'ul', 'li', 'strong', '#text'].includes(tag), tag);
  assert.ok(container.textContent.includes(XSS));
});

test('page scripts never use HTML-string sinks', () => {
  for (const file of ['site/plan.js', 'site/app.js']) {
    const src = fs.readFileSync(path.join(root, file), 'utf8').replace(/\/\/.*$/gm, '');
    for (const sink of ['innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval(', 'new Function']) {
      assert.ok(!src.includes(sink), `${file} uses ${sink}`);
    }
  }
});

test('page has a strict CSP and no external resources', () => {
  const html = fs.readFileSync(path.join(root, 'site/index.html'), 'utf8');
  assert.match(html, /Content-Security-Policy" content="default-src 'none'; script-src 'self'/);
  assert.ok(!/(src|href)="(https?:)?\/\/(?!github\.com\/sparkainlp-x)/.test(html), 'external resource');
});

test('markdown escapes user input', () => {
  const plan = HoloPlan.generatePlan(template, { city: '*bold* [x](y) <b>', country: 'C' });
  const md = HoloPlan.planToMarkdown(plan);
  assert.ok(md.includes('\\*bold\\* \\[x\\](y) \\<b\\>'));
  assert.ok(!md.includes('<b>'));
});

test('input validation', () => {
  const bad = [
    [{ city: '', country: 'C' }, 'required'], [{ city: '   ', country: 'C' }, 'required'],
    [{ country: 'C' }, 'required'], [{ city: 'A', country: '' }, 'required'],
    [{ city: 'a'.repeat(101), country: 'C' }, 'length'], [{ city: 'a\u0000b', country: 'C' }, 'control'],
    [{ city: 'a\tb', country: 'C' }, 'control'], [{ city: 5, country: 'C' }, 'type'],
    [{ city: 'A', country: 'C', language: 'de' }, 'language'],
  ];
  for (const [input, code] of bad) {
    assert.throws(() => HoloPlan.generatePlan(template, input), e => e.code === code, JSON.stringify(input));
  }
  const ok = HoloPlan.generatePlan(template, { city: '  Saint-Jean  ', country: 'Canada', region: '  ' });
  assert.equal(ok.location.city, 'Saint-Jean');
  assert.equal(ok.location.region, null);
  assert.equal(HoloPlan.generatePlan(template, { city: '🌊'.repeat(100), country: 'C' }).location.city.length, 200);
});

test('UI strings exist in every language with the same keys', () => {
  const keys = Object.keys(template.ui.en).sort();
  for (const lang of template.languages) assert.deepEqual(Object.keys(template.ui[lang]).sort(), keys);
});
