'use strict';

// js-yaml (CDN) が読み込まれていることを前提とする

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
  report:     'techreport',
};

function entryToBibtex(entry) {
  let bibtype;
  if (entry.type === 'thesis') {
    const degree = (entry.source || {}).degree;
    bibtype = degree === 'doctoral' ? 'phdthesis' : degree === 'master' ? 'mastersthesis' : 'misc';
  } else {
    bibtype = TYPE_MAP[entry.type] || 'misc';
  }
  const key = entry.id;
  const fields = [];

  const title = entry.title || entry.title_en || '';
  if (title) fields.push(['title', '{' + title + '}']);

  if (entry.authors && entry.authors.length) {
    fields.push(['author', '{' + entry.authors.join(' and ') + '}']);
  }

  if (entry.date) {
    fields.push(['year', String(entry.date).slice(0, 4)]);
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

  if (entry.abstract) fields.push(['abstract', '{' + entry.abstract + '}']);
  // thesis: school フィールドに機関名
  if (entry.type === 'thesis' && src.institution) fields.push(['school', '{' + src.institution + '}']);
  // report: institution・number フィールド
  if (entry.type === 'report' && src.institution) fields.push(['institution', '{' + src.institution + '}']);
  if (entry.type === 'report' && src.number) fields.push(['number', '{' + src.number + '}']);
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
    const text = jsyaml.dump({ entries: clean }, { indent: 2, lineWidth: -1, noRefs: true });
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
