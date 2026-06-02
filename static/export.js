'use strict';

// ---- YAML シリアライザ（簡易版）----

function toYaml(value, indent) {
  indent = indent || 0;
  const pad = '  '.repeat(indent);
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') return String(value);
  if (typeof value === 'string') {
    if (/[\n:#{}\[\],&*?|<>=!%@`]/.test(value) || value.trim() !== value || value === '') {
      return JSON.stringify(value);
    }
    return value;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';
    return value.map(v => pad + '- ' + toYaml(v, indent + 1)).join('\n');
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value).filter(k => !k.startsWith('_'));
    if (keys.length === 0) return '{}';
    return keys.map(k => {
      const v = value[k];
      if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
        return pad + k + ':\n' + toYaml(v, indent + 1);
      }
      if (Array.isArray(v)) {
        return pad + k + ':\n' + toYaml(v, indent + 1);
      }
      return pad + k + ': ' + toYaml(v, indent);
    }).join('\n');
  }
  return String(value);
}

// ---- BibTeX 変換 ----

const TYPE_MAP = {
  conference: 'inproceedings',
  journal:    'article',
  talk:       'misc',
  patent:     'misc',
  award:      'misc',
  book:       'book',
  misc:       'misc',
  other:      'misc',
};

function entryToBibtex(entry) {
  const bibtype = TYPE_MAP[entry.type] || 'misc';
  const key = entry.id;
  const fields = [];

  const title = entry.title || entry.title_en || '';
  if (title) fields.push(['title', '{' + title + '}']);

  if (entry.authors && entry.authors.length) {
    fields.push(['author', '{' + entry.authors.join(' and ') + '}']);
  }

  if (entry.date) {
    fields.push(['year', entry.date.slice(0, 4)]);
  }

  const src = entry.source || {};
  if (src.journal_name) fields.push(['journal', '{' + src.journal_name + '}']);
  if (src.volume !== undefined) fields.push(['volume', String(src.volume)]);
  if (src.number !== undefined) fields.push(['number', String(src.number)]);
  if (src.pages) fields.push(['pages', '{' + src.pages + '}']);
  if (src.doi) fields.push(['doi', '{' + src.doi + '}']);
  if (src.proceedings) fields.push(['booktitle', '{' + src.proceedings + '}']);
  if (src.publisher) fields.push(['publisher', '{' + src.publisher + '}']);
  if (src.isbn) fields.push(['isbn', '{' + src.isbn + '}']);

  if (entry.organization) fields.push(['organization', '{' + entry.organization + '}']);
  if (entry.url) fields.push(['url', '{' + entry.url + '}']);
  if (entry.note) fields.push(['note', '{' + entry.note + '}']);

  const body = fields.map(([k, v]) => '  ' + k + ' = ' + v).join(',\n');
  return '@' + bibtype + '{' + key + ',\n' + body + '\n}';
}

// ---- ダウンロード共通 ----

function download(filename, content, mimetype) {
  const blob = new Blob([content], { type: mimetype });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---- 公開 API ----

function exportEntries(entries, format) {
  // _authors_hl などの内部フィールドを除いてエクスポート
  const clean = entries.map(e => {
    const out = {};
    for (const k of Object.keys(e)) {
      if (!k.startsWith('_')) out[k] = e[k];
    }
    return out;
  });

  if (format === 'yaml') {
    const text = 'entries:\n' + clean.map(e => '  - ' + toYaml(e, 2).replace(/^  /gm, '')).join('\n\n');
    download('publications.yaml', text, 'text/yaml');
  } else if (format === 'json') {
    download('publications.json', JSON.stringify({ entries: clean }, null, 2), 'application/json');
  } else if (format === 'bibtex') {
    const text = entries.map(entryToBibtex).join('\n\n');
    download('publications.bib', text, 'text/plain');
  }
}

// 一覧ページから呼ばれる（ALL_ENTRIES は index.html.j2 側で定義）
function exportAll(format) {
  exportEntries(typeof ALL_ENTRIES !== 'undefined' ? ALL_ENTRIES : [], format);
}
