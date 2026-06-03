'use strict';

const MESSAGES = {
  ja: {
    // 種別
    'type.conference': '会議',
    'type.journal':    '論文誌',
    'type.talk':       '講演',
    'type.patent':     '特許',
    'type.award':      '受賞',
    'type.book':       '書籍',
    'type.misc':       '解説等',
    'type.other':      'その他',
    'type.thesis':     '学位論文',
    'type.report':     '技術レポート',
    // バッジ
    'badge.invited':       '招待',
    'badge.reviewed':      '査読',
    'badge.domestic':      '国内',
    'badge.international': '国際',
    'badge.invited.detail':  '招待講演',
    'badge.reviewed.detail': '査読あり',
    // フィルター
    'filter.label.type':     '種別',
    'filter.label.year':     '年',
    'filter.label.scope':    '国内/国際',
    'filter.label.reviewed': '査読',
    'filter.label.invited':  '招待',
    'filter.all':            'すべて',
    'filter.domestic':       '国内',
    'filter.international':  '国際',
    'filter.reviewed.yes':   '査読あり',
    'filter.reviewed.no':    '査読なし',
    'filter.invited.yes':    '招待あり',
    'filter.invited.no':     '招待なし',
    // テーブルヘッダー
    'col.year':    '年',
    'col.type':    '種別',
    'col.title':   'タイトル',
    'col.authors': '著者',
    'col.venue':   '掲載先・会議',
    // 検索
    'search.placeholder': 'タイトル・著者・会議名で検索...',
    // エクスポート（一覧）
    'export.all.yaml':      '全件 YAML',
    'export.all.json':      '全件 JSON',
    'export.all.bibtex':    '全件 BibTeX',
    'export.all.hayagriva': '全件 Hayagriva',
    // エクスポート（詳細）
    'export.one.title': 'このエントリをエクスポート',
    // カウント（関数）: shown=表示件数, total=絞り込み後の全件数
    'count': (shown, total) => shown < total ? `${shown} / ${total} 件表示` : `${shown} 件表示`,
    // サマリー（関数）
    'summary.total': n => `全 <strong>${n}</strong> 件`,
    // ページネーション
    'btn.show.more': 'さらに表示',
    'btn.show.all':  '全件表示',
    // 前後ナビゲーション
    'nav.prev': '← 前の業績',
    'nav.next': '次の業績 →',
    // 詳細ラベル
    'detail.authors':          '著者',
    'detail.date':             '日付',
    'detail.presenter':        '登壇者',
    'detail.organization':     '組織・学会',
    'detail.venue.conference': '会議名',
    'detail.venue.talk':       '会場・イベント',
    'detail.location':         '開催地',
    'detail.proceedings':      '論文集',
    'detail.pages':            'ページ',
    'detail.journal':          '誌名',
    'detail.vol_no':           '巻・号',
    'detail.doi':              'DOI',
    'detail.award_name':       '賞名',
    'detail.org_giving_award': '授与機関',
    'detail.publisher':        '出版社',
    'detail.isbn':             'ISBN',
    'detail.editors':          '編者',
    'detail.chapter':          '章',
    'detail.source':           '出典',
    'detail.url':              'URL / DOI',
    'detail.note':             '備考',
    'detail.patent_number':    '特許番号',
    'detail.country':          '国',
    'detail.status':           '状態',
    'detail.institution':      '機関',
    'detail.report_number':    'レポート番号',
    'detail.degree':           '学位',
    'detail.abstract':         'アブストラクト',
    'detail.publisher_institution': '発行機関',
    // 特許状態
    'patent.granted': '登録',
    'patent.applied': '出願',
    // 学位
    'degree.doctoral': '博士論文',
    'degree.master':   '修士論文',
    'degree.bachelor': '学士論文',
    // 添付ファイル
    'section.files': '添付ファイル',
  },
  en: {
    // Types
    'type.conference': 'Conference',
    'type.journal':    'Journal',
    'type.talk':       'Talk',
    'type.patent':     'Patent',
    'type.award':      'Award',
    'type.book':       'Book',
    'type.misc':       'Article/Misc',
    'type.other':      'Other',
    'type.thesis':     'Thesis',
    'type.report':     'Tech Report',
    // Badges
    'badge.invited':       'Invited',
    'badge.reviewed':      'Reviewed',
    'badge.domestic':      'Domestic',
    'badge.international': 'Intl.',
    'badge.invited.detail':  'Invited',
    'badge.reviewed.detail': 'Peer-reviewed',
    // Filters
    'filter.label.type':     'Type',
    'filter.label.year':     'Year',
    'filter.label.scope':    'Scope',
    'filter.label.reviewed': 'Review',
    'filter.label.invited':  'Invited',
    'filter.all':            'All',
    'filter.domestic':       'Domestic',
    'filter.international':  'International',
    'filter.reviewed.yes':   'Reviewed',
    'filter.reviewed.no':    'Not reviewed',
    'filter.invited.yes':    'Invited',
    'filter.invited.no':     'Not invited',
    // Table headers
    'col.year':    'Year',
    'col.type':    'Type',
    'col.title':   'Title',
    'col.authors': 'Authors',
    'col.venue':   'Venue',
    // Search
    'search.placeholder': 'Search by title, author, venue…',
    // Export (index)
    'export.all.yaml':      'All YAML',
    'export.all.json':      'All JSON',
    'export.all.bibtex':    'All BibTeX',
    'export.all.hayagriva': 'All Hayagriva',
    // Export (detail)
    'export.one.title': 'Export this entry',
    // Count (function)
    'count': (shown, total) => shown < total ? `Showing ${shown} of ${total}` : `Showing ${shown} ${shown === 1 ? 'entry' : 'entries'}`,
    // Summary (function)
    'summary.total': n => `Total <strong>${n}</strong> ${n === 1 ? 'entry' : 'entries'}`,
    // Pagination
    'btn.show.more': 'Show more',
    'btn.show.all':  'Show all',
    // Entry navigation
    'nav.prev': '← Previous',
    'nav.next': 'Next →',
    // Detail labels
    'detail.authors':          'Authors',
    'detail.date':             'Date',
    'detail.presenter':        'Presenter',
    'detail.organization':     'Organization',
    'detail.venue.conference': 'Venue',
    'detail.venue.talk':       'Venue / Event',
    'detail.location':         'Location',
    'detail.proceedings':      'Proceedings',
    'detail.pages':            'Pages',
    'detail.journal':          'Journal',
    'detail.vol_no':           'Vol./No.',
    'detail.doi':              'DOI',
    'detail.award_name':       'Award',
    'detail.org_giving_award': 'Awarded by',
    'detail.publisher':        'Publisher',
    'detail.isbn':             'ISBN',
    'detail.editors':          'Editors',
    'detail.chapter':          'Chapter',
    'detail.source':           'Source',
    'detail.url':              'URL / DOI',
    'detail.note':             'Note',
    'detail.patent_number':    'Patent No.',
    'detail.country':          'Country',
    'detail.status':           'Status',
    'detail.institution':      'Institution',
    'detail.report_number':    'Report No.',
    'detail.degree':           'Degree',
    'detail.abstract':         'Abstract',
    'detail.publisher_institution': 'Publisher / Institution',
    // Patent status
    'patent.granted': 'Granted',
    'patent.applied': 'Applied',
    // Degree
    'degree.doctoral': 'Doctoral dissertation',
    'degree.master':   "Master's thesis",
    'degree.bachelor': "Bachelor's thesis",
    // Files section
    'section.files': 'Attachments',
  },
};

const _LANG_KEY = 'scholist-lang';

function t(key, ...args) {
  const lang = localStorage.getItem(_LANG_KEY) || 'ja';
  const val = (MESSAGES[lang] || MESSAGES.ja)[key] ?? MESSAGES.ja[key] ?? key;
  return typeof val === 'function' ? val(...args) : val;
}

function applyLanguage(lang) {
  localStorage.setItem(_LANG_KEY, lang);
  document.documentElement.lang = lang;
  const msgs = MESSAGES[lang] || MESSAGES.ja;

  // テキスト置換
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const val = msgs[el.dataset.i18n] ?? MESSAGES.ja[el.dataset.i18n];
    if (typeof val === 'string') el.textContent = val;
  });

  // placeholder 置換
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const val = msgs[el.dataset.i18nPlaceholder] ?? MESSAGES.ja[el.dataset.i18nPlaceholder];
    if (typeof val === 'string') el.placeholder = val;
  });

  // 種別バッジのテキスト置換
  document.querySelectorAll('[data-i18n-type]').forEach(el => {
    const val = msgs['type.' + el.dataset.i18nType] ?? MESSAGES.ja['type.' + el.dataset.i18nType];
    if (val) el.textContent = val;
  });

  // 言語ボタンのアクティブ状態を更新
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('lang-btn-active', btn.dataset.lang === lang);
  });

  // サマリーと件数表示を再描画（ページにその関数が存在する場合）
  if (typeof buildSummary === 'function') buildSummary();
  if (typeof updateCount === 'function') {
    const shown = typeof _lastShown !== 'undefined' ? _lastShown : (_lastVisibleCount || 0);
    const total = typeof _lastTotal !== 'undefined' ? _lastTotal : shown;
    updateCount(shown, total);
  }
}

function initLang() {
  const stored = localStorage.getItem(_LANG_KEY);
  if (stored) { applyLanguage(stored); return; }

  // SCHOLIST_DEFAULT_LANG はテンプレートが <script> で定義する
  const def = (typeof SCHOLIST_DEFAULT_LANG !== 'undefined') ? SCHOLIST_DEFAULT_LANG : 'auto';
  if (def === 'ja') { applyLanguage('ja'); return; }
  if (def === 'en') { applyLanguage('en'); return; }
  // auto: ブラウザ言語で判定（ja 以外は英語）
  applyLanguage(navigator.language.startsWith('ja') ? 'ja' : 'en');
}
