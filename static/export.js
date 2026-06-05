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
  if (entry.type === 'thesis' && src.institution) fields.push(['school', '{' + src.institution + '}']);
  if (entry.type === 'report' && src.institution) fields.push(['institution', '{' + src.institution + '}']);
  if (entry.type === 'report' && src.number) fields.push(['number', '{' + src.number + '}']);
  if (entry.organization) fields.push(['organization', '{' + entry.organization + '}']);
  if (entry.url) fields.push(['url', '{' + entry.url + '}']);
  if (entry.note) fields.push(['note', '{' + entry.note + '}']);

  const body = fields.map(([k, v]) => '  ' + k + ' = ' + v).join(',\n');
  return '@' + bibtype + '{' + key + ',\n' + body + '\n}';
}

// ---- Hayagriva 変換 ----

function _hayaTitle(entry) {
  if (entry.title && !entry.title_en) return entry.title;
  if (!entry.title && entry.title_en) return entry.title_en;
  if (entry.title && entry.title_en) {
    return entry.language === 'en' ? entry.title_en : entry.title;
  }
  return '';
}

function _extractDoi(url) {
  if (!url) return null;
  const m = url.match(/^https?:\/\/doi\.org\/(.+)$/);
  return m ? m[1] : null;
}

function _addSerialNumber(obj, key, value) {
  if (!value) return;
  if (!obj['serial-number']) {
    obj['serial-number'] = {};
  }
  obj['serial-number'][key] = value;
}

function entryToHayagriva(entry) {
  const src = entry.source || {};
  const obj = {};

  // ---- 種別ごとの変換 ----
  switch (entry.type) {
    case 'conference':
      obj.type = 'article';
      if (src.pages) obj['page-range'] = src.pages;
      if (src.proceedings || entry.organization || entry.location) {
        const parent = { type: 'proceedings' };
        if (src.proceedings) parent.title = src.proceedings;
        if (entry.organization) parent.organization = entry.organization;
        if (entry.location) parent.location = entry.location;
        obj.parent = parent;
      } else if (entry.venue) {
        obj.note = entry.venue;
      }
      break;

    case 'journal':
      obj.type = 'article';
      if (src.pages) obj['page-range'] = src.pages;
      if (src.doi) _addSerialNumber(obj, 'doi', src.doi);
      if (src.journal_name) {
        const parent = { type: 'periodical', title: src.journal_name };
        if (src.volume !== undefined) parent.volume = src.volume;
        if (src.number !== undefined) parent.issue = src.number;
        obj.parent = parent;
      }
      break;

    case 'book': {
      const isChapter = src.chapter || src.pages;
      const sn = {};
      if (src.isbn) sn.isbn = src.isbn;
      if (isChapter) {
        obj.type = 'chapter';
        if (src.pages) obj['page-range'] = src.pages;
        const parent = { type: 'book' };
        if (src.publisher) parent.publisher = src.publisher;
        if (src.editors && src.editors.length) parent.editor = src.editors;
        if (Object.keys(sn).length) parent['serial-number'] = sn;
        obj.parent = parent;
      } else {
        obj.type = 'book';
        if (src.publisher) obj.publisher = src.publisher;
        if (src.editors && src.editors.length) obj.editor = src.editors;
        if (Object.keys(sn).length) obj['serial-number'] = sn;
      }
      break;
    }

    case 'thesis': {
      obj.type = 'thesis';
      if (src.institution) obj.organization = src.institution;
      const degreeMap = {
        doctoral: 'Doctoral dissertation',
        master:   "Master's thesis",
        bachelor: "Bachelor's thesis",
      };
      if (src.degree && degreeMap[src.degree]) obj.genre = degreeMap[src.degree];
      break;
    }

    case 'report':
      obj.type = 'report';
      if (src.institution) obj.organization = src.institution;
      if (src.number) _addSerialNumber(obj, 'serial', src.number);
      break;

    case 'patent':
      obj.type = 'patent';
      if (src.patent_number) obj['serial-number'] = src.patent_number;
      break;

    case 'award':
      obj.type = 'misc';
      if (src.org_giving_award) obj.organization = src.org_giving_award;
      break;

    case 'talk':
      obj.type = 'misc';
      {
        const parts = [];
        if (entry.venue) parts.push(entry.venue);
        if (entry.location) parts.push(entry.location);
        if (parts.length) obj.note = parts.join(', ');
      }
      break;

    default: // misc, other
      obj.type = 'misc';
      if (src.description) obj.note = src.description;
      break;
  }

  // ---- 共通フィールド ----
  const title = _hayaTitle(entry);
  if (title && !obj.title) obj.title = title;

  if (entry.authors && entry.authors.length) {
    obj.author = entry.authors.length === 1 ? entry.authors[0] : entry.authors;
  }

  if (entry.date) obj.date = String(entry.date);
  if (entry.language) obj.language = entry.language;
  if (entry.abstract) obj.abstract = entry.abstract;

  if (entry.organization && !obj.organization) {
    obj.organization = entry.organization;
  }

  // URL: DOI URL なら serial-number.doi に変換、それ以外は url フィールドへ
  if (entry.url) {
    const doi = _extractDoi(entry.url);
    if (doi) {
      // report の serial-number はオブジェクト形式に変換してから doi を追加
      if (typeof obj['serial-number'] === 'string') {
        obj['serial-number'] = { serial: obj['serial-number'], doi };
      } else {
        _addSerialNumber(obj, 'doi', doi);
      }
    } else {
      obj.url = entry.url;
    }
  }

  if (entry.note) {
    obj.note = obj.note ? obj.note + '; ' + entry.note : entry.note;
  }

  return { [entry.id]: obj };
}

// ---- RIS 変換 ----

const RIS_TYPE_MAP = {
  journal:    'JOUR',
  conference: 'CONF',
  book:       'BOOK',
  thesis:     'THES',
  report:     'RPRT',
  patent:     'PAT',
  talk:       'GEN',
  award:      'GEN',
  misc:       'MISC',
  other:      'MISC',
};

function _dateToRISPY(date) {
  if (!date) return null;
  const parts = String(date).split('-');
  const y = parts[0];
  const m = parts[1] ? parts[1].padStart(2, '0') : null;
  const d = parts[2] ? parts[2].padStart(2, '0') : null;
  if (m && d) return `${y}/${m}/${d}/`;
  if (m)      return `${y}/${m}/`;
  return `${y}/`;
}

function _risPages(pages) {
  if (!pages) return [null, null];
  // scholist 形式 "1-1 -- 1-2" 等の二重ダッシュ
  let m = pages.match(/^(.+?)\s*--\s*(.+)$/);
  if (m) return [m[1].trim(), m[2].trim()];
  // 単純な "100-110"
  m = pages.match(/^([^-]+)-([^-]+)$/);
  if (m) return [m[1].trim(), m[2].trim()];
  return [pages, null];
}

function entryToRIS(entry) {
  const src = entry.source || {};
  const lines = [];
  const f = (tag, val) => {
    if (val != null && String(val).trim()) lines.push(`${tag}  - ${val}`);
  };

  let ty = RIS_TYPE_MAP[entry.type] || 'GEN';
  if (entry.type === 'book' && (src.chapter || src.pages)) ty = 'CHAP';
  f('TY', ty);
  f('ID', entry.id);
  f('TI', entry.title || entry.title_en || '');
  (entry.authors || []).forEach(a => f('AU', a));
  f('PY', _dateToRISPY(entry.date));
  f('AB', entry.abstract);
  f('N1', entry.note);

  const doiMatch = entry.url && entry.url.match(/^https?:\/\/doi\.org\/(.+)$/);
  if (doiMatch) {
    f('DO', doiMatch[1]);
    f('UR', entry.url);
  } else if (entry.url) {
    f('UR', entry.url);
  }

  const [sp, ep] = _risPages(src.pages);
  switch (entry.type) {
    case 'journal':
      f('JO', src.journal_name);
      if (src.volume !== undefined) f('VL', src.volume);
      if (src.number !== undefined) f('IS', src.number);
      f('SP', sp); f('EP', ep);
      break;
    case 'conference':
      f('T2', src.proceedings);
      f('SP', sp); f('EP', ep);
      f('PB', entry.organization);
      f('CY', entry.location);
      break;
    case 'book':
      f('PB', src.publisher);
      f('SN', src.isbn);
      f('SP', sp); f('EP', ep);
      break;
    case 'thesis': {
      f('PB', src.institution);
      const dm = { doctoral: 'Doctoral dissertation', master: "Master's thesis", bachelor: "Bachelor's thesis" };
      f('M1', dm[src.degree] || '');
      break;
    }
    case 'report':
      f('PB', src.institution);
      f('M1', src.number);
      break;
    case 'patent':
      f('M1', src.patent_number);
      f('CY', src.country);
      break;
    case 'talk':
      f('T2', entry.venue);
      f('CY', entry.location);
      break;
    case 'award':
      f('PB', (src.org_giving_award || ''));
      break;
  }

  lines.push('ER  - ');
  return lines.join('\n');
}

// ---- CSL-JSON 変換 ----

const CSL_TYPE_MAP = {
  journal:    'article-journal',
  conference: 'paper-conference',
  book:       'book',
  thesis:     'thesis',
  report:     'report',
  patent:     'patent',
  talk:       'speech',
  award:      'article',
  misc:       'article',
  other:      'article',
};

function _dateToCSLIssued(date) {
  if (!date) return null;
  const parts = String(date).split('-').map(Number);
  return { 'date-parts': [parts] };
}

function entryToCSLJSON(entry) {
  const src = entry.source || {};
  const obj = {};

  obj.id = entry.id;
  obj.type = CSL_TYPE_MAP[entry.type] || 'article';
  if (entry.type === 'book' && (src.chapter || src.pages)) obj.type = 'chapter';

  const title = entry.title || entry.title_en || '';
  if (title) obj.title = title;

  if (entry.authors && entry.authors.length) {
    obj.author = entry.authors.map(a => ({ literal: a }));
  }

  const issued = _dateToCSLIssued(entry.date);
  if (issued) obj.issued = issued;

  if (entry.abstract) obj.abstract = entry.abstract;
  if (entry.language) obj.language = entry.language;

  const doiMatch = entry.url && entry.url.match(/^https?:\/\/doi\.org\/(.+)$/);
  if (doiMatch) {
    obj.DOI = doiMatch[1];
    obj.URL = entry.url;
  } else if (entry.url) {
    obj.URL = entry.url;
  }

  switch (entry.type) {
    case 'journal':
      if (src.journal_name) obj['container-title'] = src.journal_name;
      if (src.volume !== undefined) obj.volume = String(src.volume);
      if (src.number !== undefined) obj.issue = String(src.number);
      if (src.pages) obj.page = src.pages;
      if (src.doi) obj.DOI = src.doi;
      break;
    case 'conference':
      if (src.proceedings)     obj['container-title'] = src.proceedings;
      if (src.pages)           obj.page = src.pages;
      if (entry.organization)  obj.publisher = entry.organization;
      if (entry.location)      obj['publisher-place'] = entry.location;
      break;
    case 'book':
      if (src.publisher) obj.publisher = src.publisher;
      if (src.isbn)      obj.ISBN = src.isbn;
      if (src.editors && src.editors.length) obj.editor = src.editors.map(e => ({ literal: e }));
      if (src.chapter)   obj['chapter-number'] = src.chapter;
      if (src.pages)     obj.page = src.pages;
      break;
    case 'thesis': {
      if (src.institution) obj.publisher = src.institution;
      const dm = { doctoral: 'Doctoral dissertation', master: "Master's thesis", bachelor: "Bachelor's thesis" };
      if (src.degree && dm[src.degree]) obj.genre = dm[src.degree];
      break;
    }
    case 'report':
      if (src.institution) obj.publisher = src.institution;
      if (src.number)      obj.number = src.number;
      break;
    case 'patent':
      if (src.patent_number) obj.number = src.patent_number;
      if (src.country)       obj.jurisdiction = src.country;
      break;
    case 'talk':
      if (entry.venue)    obj['event-title'] = entry.venue;
      if (entry.location) obj['event-place'] = entry.location;
      break;
    case 'award':
      if (src.org_giving_award) obj.publisher = src.org_giving_award;
      break;
  }

  if (entry.note) obj.note = entry.note;
  return obj;
}

// ---- ダウンロード共通 ----

function download(filename, content, mimetype) {
  const type = mimetype.startsWith('text/') ? mimetype + '; charset=utf-8' : mimetype;
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---- 公開 API ----

function exportEntries(entries, format) {
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
  } else if (format === 'hayagriva') {
    const merged = Object.assign({}, ...entries.map(entryToHayagriva));
    const text = jsyaml.dump(merged, { indent: 2, lineWidth: -1, noRefs: true });
    download('publications-hayagriva.yml', text, 'text/yaml');
  } else if (format === 'ris') {
    const text = entries.map(entryToRIS).join('\n\n');
    download('publications.ris', text, 'text/plain');
  } else if (format === 'csl-json') {
    const arr = entries.map(entryToCSLJSON);
    download('publications.csl.json', JSON.stringify(arr, null, 2), 'application/json');
  }
}

// 一覧ページから呼ばれる（ALL_ENTRIES は index.html.j2 側で定義）
function exportAll(format) {
  exportEntries(typeof ALL_ENTRIES !== 'undefined' ? ALL_ENTRIES : [], format);
}
