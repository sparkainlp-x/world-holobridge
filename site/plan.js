// SPDX-License-Identifier: MIT OR Apache-2.0
// Community plan logic shared by the web page and the Node tests.
// Mirrors generate_community_plan / plan_to_markdown / plan_to_json in
// world_holobridge.py; tests/test_plan_parity.py checks they agree.
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.HoloPlan = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var PLACEHOLDER = /\{(city|country|location)\}/g;
  var TRIM = /^[ \t\n\r\u00a0\u3000\ufeff]+|[ \t\n\r\u00a0\u3000\ufeff]+$/g;
  var CONTROL = /[\u0000-\u001f\u007f]/;
  var MD_SPECIAL = /([\\`*_\[\]<>|])/g;

  function PlanInputError(code, field, max) {
    var err = new Error(code + ':' + field);
    err.name = 'PlanInputError';
    err.code = code;
    err.field = field;
    err.max = max;
    return err;
  }

  // Same rules as clean_plan_field in Python. Length counts code points.
  function cleanField(value, field, required, maxLength) {
    if (value === null || value === undefined) {
      if (required) throw PlanInputError('required', field);
      return null;
    }
    if (typeof value !== 'string') throw PlanInputError('type', field);
    value = value.replace(TRIM, '');
    if (!value) {
      if (required) throw PlanInputError('required', field);
      return null;
    }
    if (Array.from(value).length > maxLength) throw PlanInputError('length', field, maxLength);
    if (CONTROL.test(value)) throw PlanInputError('control', field);
    return value;
  }

  function fill(node, values) {
    if (typeof node === 'string') {
      return node.replace(PLACEHOLDER, function (_, key) { return values[key]; });
    }
    if (Array.isArray(node)) return node.map(function (n) { return fill(n, values); });
    if (node && typeof node === 'object') {
      var out = {};
      Object.keys(node).forEach(function (k) { out[k] = fill(node[k], values); });
      return out;
    }
    return node;
  }

  function generatePlan(template, input) {
    var language = input.language === undefined ? 'en' : input.language;
    if (template.languages.indexOf(language) === -1) throw PlanInputError('language', 'language');
    var max = template.max_field_length;
    var city = cleanField(input.city, 'city', true, max);
    var country = cleanField(input.country, 'country', true, max);
    var region = cleanField(input.region, 'region', false, max);
    var display = [city, region, country].filter(Boolean).join(', ');
    var content = fill(template.content[language], { city: city, country: country, location: display });
    var plan = {
      schema: template.schema,
      language: language,
      location: { city: city, region: region, country: country, display: display }
    };
    Object.keys(content).forEach(function (k) { plan[k] = content[k]; });
    return plan;
  }

  function md(text) { return text.replace(MD_SPECIAL, '\\$1'); }

  function planToMarkdown(plan) {
    var lines = ['# ' + md(plan.title), '', '**' + plan.md.location + ':** ' + md(plan.location.display), ''];
    plan.notices.forEach(function (n) { lines.push('> ' + md(n)); lines.push('>'); });
    if (plan.notices.length) { lines.pop(); lines.push(''); }
    plan.sections.forEach(function (s) {
      lines.push('## ' + md(s.title), '');
      if (s.intro) lines.push(md(s.intro), '');
      s.items.forEach(function (it) {
        lines.push(it.label ? '- **' + md(it.label) + ':** ' + md(it.text) : '- ' + md(it.text));
      });
      if (s.items.length) lines.push('');
      if (s.note) lines.push(md(s.note), '');
      if (s.gate) lines.push('*' + plan.md.gate + ': ' + md(s.gate) + '*', '');
    });
    return lines.join('\n').replace(/\n+$/, '') + '\n';
  }

  function planToJson(plan) { return JSON.stringify(plan, null, 2) + '\n'; }

  // Renders the plan using DOM text nodes only (never innerHTML), so user
  // input cannot inject markup. `doc` is injectable for tests.
  function renderPlan(plan, container, doc) {
    doc = doc || container.ownerDocument;
    function el(tag, text, cls) {
      var e = doc.createElement(tag);
      if (cls) e.className = cls;
      if (text !== undefined && text !== null) e.textContent = text;
      return e;
    }
    while (container.firstChild) container.removeChild(container.firstChild);
    var article = el('article', null, 'plan');
    article.appendChild(el('h2', plan.title));
    var notices = el('div', null, 'notices');
    plan.notices.forEach(function (n) { notices.appendChild(el('p', n)); });
    article.appendChild(notices);
    plan.sections.forEach(function (s) {
      var sec = el('section', null, 'plan-section');
      sec.setAttribute('data-section', s.id);
      sec.appendChild(el('h3', s.title));
      if (s.intro) sec.appendChild(el('p', s.intro));
      if (s.items.length) {
        var ul = el('ul');
        s.items.forEach(function (it) {
          var li = el('li');
          if (it.label) { li.appendChild(el('strong', it.label + ': ')); li.appendChild(doc.createTextNode(it.text)); }
          else li.textContent = it.text;
          ul.appendChild(li);
        });
        sec.appendChild(ul);
      }
      if (s.note) sec.appendChild(el('p', s.note, 'note'));
      if (s.gate) sec.appendChild(el('p', plan.md.gate + ': ' + s.gate, 'gate'));
      article.appendChild(sec);
    });
    container.appendChild(article);
    return article;
  }

  return {
    cleanField: cleanField,
    generatePlan: generatePlan,
    planToMarkdown: planToMarkdown,
    planToJson: planToJson,
    renderPlan: renderPlan
  };
}));
