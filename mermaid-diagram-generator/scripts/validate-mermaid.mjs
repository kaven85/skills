#!/usr/bin/env node
// Syntax-validate every ```mermaid block in a .md file (or a whole .mmd file).
//
// The `mermaid` npm module is resolved in this order:
//   1. $MERMAID_MODULE — path to a mermaid package dir (resolved to its dist bundle) or a .mjs bundle
//   2. `mermaid` resolvable from the current working directory
//
// Install options:
//   npm i -D mermaid jsdom   (in the current project), or
//   npm i -g mermaid && npm i -D jsdom
//   export MERMAID_MODULE="$(npm root -g)/mermaid"
//
// Exit 0 when every block parses, 1 on any parse failure, 2 on usage/tooling errors.

import { readFileSync, statSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error('usage: validate-mermaid.mjs <file.md|file.mmd> [...]');
  process.exit(2);
}
// Resolve user-installed tooling from the project where this script is run.
const requireFromCwd = createRequire(join(process.cwd(), 'noop.cjs'));


// Some diagram parsers touch browser globals; shim them when jsdom is around.
// mermaid's dompurify instance picks up window/document at import time, so these
// globals MUST exist before the `import('mermaid')` below.
if (typeof globalThis.document === 'undefined') {
  try {
    const { JSDOM } = requireFromCwd('jsdom');
    const dom = new JSDOM('<!doctype html><html><body></body></html>', { url: 'http://localhost/' });
    globalThis.window = dom.window;
    globalThis.document = dom.window.document;
    try {
      globalThis.navigator = dom.window.navigator;
    } catch {
      // Node >= 21 defines navigator as a getter-only global — leave it as-is.
    }
  } catch {
    // jsdom not installed — most parsers still work; continue.
  }
}

// Node cannot import a directory; resolve a package dir to its ESM bundle.
function mermaidSpec() {
  const env = process.env.MERMAID_MODULE;
  if (!env) return pathToFileURL(requireFromCwd.resolve('mermaid')).href;
  try {
    if (statSync(env).isDirectory()) {
      for (const c of ['dist/mermaid.esm.min.mjs', 'dist/mermaid.esm.mjs', 'dist/mermaid.core.mjs']) {
        try {
          if (statSync(join(env, c)).isFile()) return pathToFileURL(join(env, c)).href;
        } catch {
          // try next candidate
        }
      }
    }
  } catch {
    // not a directory — fall through to the bare path below
  }
  return pathToFileURL(env).href;
}

let mermaid;
try {
  mermaid = (await import(mermaidSpec())).default;
} catch {
  console.error(
    'mermaid module not found.\n' +
    'Install it with `npm i mermaid` in this project, or set MERMAID_MODULE to a mermaid package path.'
  );
  process.exit(2);
}


function blocksOf(file) {
  const text = readFileSync(file, 'utf8');
  if (file.endsWith('.mmd')) return [text];
  const blocks = [];
  const re = /```mermaid\s*\n([\s\S]*?)```/g;
  let m;
  while ((m = re.exec(text)) !== null) blocks.push(m[1]);
  return blocks;
}

let failed = 0;
for (const file of files) {
  const blocks = blocksOf(file);
  if (blocks.length === 0) {
    console.log(`${file}: no mermaid blocks found`);
    continue;
  }
  for (const [i, code] of blocks.entries()) {
    try {
      await mermaid.parse(code);
      console.log(`${file} [block ${i + 1}]: OK`);
    } catch (err) {
      failed++;
      console.error(`${file} [block ${i + 1}]: PARSE ERROR`);
      console.error(String(err && err.message ? err.message : err).split('\n').slice(0, 6).join('\n'));
    }
  }
}
process.exit(failed === 0 ? 0 : 1);
