// SPDX-License-Identifier: MIT OR Apache-2.0
// Page wiring. No network requests except loading the local template, no
// storage, no analytics. All user text is rendered as text nodes.
(function () {
  'use strict';
  var template = null;
  var plan = null;
  var lang = (navigator.language || 'en').toLowerCase().indexOf('fr') === 0 ? 'fr' : 'en';
  var $ = function (id) { return document.getElementById(id); };

  function t(key) { return template.ui[lang][key]; }

  function applyUi() {
    document.documentElement.lang = lang;
    document.title = t('page_title');
    document.querySelectorAll('[data-i18n]').forEach(function (node) {
      node.textContent = t(node.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
    });
  }

  function errorText(err) {
    var field = t(err.field) || err.field;
    var key = { required: 'err_required', length: 'err_length', control: 'err_control', type: 'err_required' }[err.code];
    if (!key) return String(err.message);
    return t(key).replace('{field}', field).replace('{max}', String(err.max));
  }

  function generate() {
    var status = $('status');
    status.textContent = '';
    try {
      plan = HoloPlan.generatePlan(template, {
        city: $('city').value, country: $('country').value, region: $('region').value, language: lang
      });
    } catch (err) {
      if (err.name !== 'PlanInputError') throw err;
      plan = null;
      status.textContent = errorText(err);
      $('actions').hidden = true;
      return;
    }
    HoloPlan.renderPlan(plan, $('output'), document);
    $('actions').hidden = false;
  }

  function download(text, type, ext) {
    var blob = new Blob([text], { type: type + ';charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    var slug = plan.location.display.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-+|-+$/g, '') || 'plan';
    a.href = url;
    a.download = 'community_plan_' + slug + '_' + plan.language + '.' + ext;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function init(tpl) {
    template = tpl;
    applyUi();
    $('plan-form').addEventListener('submit', function (e) { e.preventDefault(); generate(); });
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.addEventListener('click', function () {
        lang = b.getAttribute('data-lang');
        applyUi();
        if (plan) generate();
      });
    });
    $('dl-md').addEventListener('click', function () { download(HoloPlan.planToMarkdown(plan), 'text/markdown', 'md'); });
    $('dl-json').addEventListener('click', function () { download(HoloPlan.planToJson(plan), 'application/json', 'json'); });
    $('print').addEventListener('click', function () { window.print(); });
    document.body.setAttribute('data-ready', 'true');
  }

  fetch('plan_template.json', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error('template ' + r.status); return r.json(); })
    .then(init)
    .catch(function (err) { $('status').textContent = 'Could not load plan_template.json: ' + err.message; });
}());
