// SPDX-License-Identifier: MIT OR Apache-2.0
// Minimal DOM stand-in: text goes through textContent/createTextNode only;
// any attempt to set innerHTML/outerHTML throws.
'use strict';

class Node {
  constructor(tag, text) {
    this.tagName = tag;
    this.children = [];
    this.attrs = {};
    this._text = text === undefined ? '' : String(text);
    this.className = '';
  }
  get firstChild() { return this.children[0] || null; }
  appendChild(c) { this.children.push(c); return c; }
  removeChild(c) { this.children.splice(this.children.indexOf(c), 1); return c; }
  setAttribute(k, v) {
    if (/^on/i.test(k)) throw new Error('event-handler attribute set: ' + k);
    this.attrs[k] = String(v);
  }
  set textContent(v) { this.children = []; this._text = String(v); }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(''); }
  set innerHTML(v) { throw new Error('innerHTML used'); }
  set outerHTML(v) { throw new Error('outerHTML used'); }
  insertAdjacentHTML() { throw new Error('insertAdjacentHTML used'); }
  // Serialize as escaped HTML, the way a browser would for text nodes.
  toHTML() {
    const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    if (this.tagName === '#text') return esc(this._text);
    const attrs = Object.entries(this.attrs).map(([k, v]) => ` ${k}="${esc(v).replace(/"/g, '&quot;')}"`).join('');
    const cls = this.className ? ` class="${this.className}"` : '';
    return `<${this.tagName}${cls}${attrs}>${esc(this._text)}${this.children.map(c => c.toHTML()).join('')}</${this.tagName}>`;
  }
  allTags() { return [this.tagName, ...this.children.flatMap(c => c.allTags())]; }
}

const fakeDocument = {
  createElement: tag => new Node(tag),
  createTextNode: text => new Node('#text', text),
};

module.exports = { Node, fakeDocument };
