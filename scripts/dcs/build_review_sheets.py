"""
build_review_sheets.py -- H975, generates 5 interactive review sheets (one per
queue A-E) from docs/queue_candidates/queue_*.json, via the shared csl_pyutil
emitter (per the org /review-sheet skill contract). Read-only against the
candidate JSON; writes only into the gitignored review/ folder.
"""
import sys, json, pathlib, html
sys.stdout.reconfigure(encoding='utf-8')
from csl_pyutil import render_review_sheet

ROOT = pathlib.Path(r"C:/Users/user/Documents/GitHub/WhitneyRoots-h877-H975")
CAND_DIR = ROOT / 'docs' / 'queue_candidates'
OUT_DIR = ROOT / 'review'
OUT_DIR.mkdir(parents=True, exist_ok=True)

GENERATED = '19-07-2026'

def esc(x):
    return html.escape(str(x)) if x is not None else ''

def kv_table(pairs):
    rows = ''.join(f'<tr><td style="font-weight:600;padding:2px 10px 2px 0;vertical-align:top;white-space:nowrap">{esc(k)}</td><td style="padding:2px 0">{v}</td></tr>' for k, v in pairs)
    return f'<table style="border-collapse:collapse">{rows}</table>'


# ---------- Queue A ----------
def build_a():
    data = json.load(open(CAND_DIR / 'queue_a.json', encoding='utf-8'))
    items = []
    for it in data['items']:
        risk = it.get('proposal') or '—'
        badges = [risk] if risk != '—' else []
        question = kv_table([
            ('Whitney Roots classes', esc(', '.join(it['whitney_roots_classes']) or '∅')),
            ('Current classes (with corpus add)', esc(', '.join(it['current_classes']))),
            ('Added class', f"<b>{esc(', '.join(it['added']))}</b>"),
            ('Method', esc(it['method'])),
            ('Grammar support for added class', esc(it.get('grammar_support_for_added') or 'not found')),
            ('Pre-computed lean (evidence only, NOT a decision)', f"<b>{esc(it.get('proposal') or '—')}</b>"),
        ])
        panels = [('Check against', f"<p>{esc(it['check_against'])}</p>")]
        items.append({
            'id': it['id'], 'filt': 'all',
            'title': f"#{it['id']} — {it['root']}",
            'badges': badges,
            'question': question,
            'panels': panels,
            'note_placeholder': 'Cite the § or Zalizniak vol/p. that settles this.',
        })
    html_out = render_review_sheet(items=items, config={
        'sheet_id': 'whitneyroots-queue-a_kept-class-additions',
        'title': 'WhitneyRoots — Queue A: сохранённые добавления классов',
        'subtitle': f'{len(items)} кандидатов · выработано {GENERATED} · Sonnet 5 (claude-sonnet-5), H975',
        'footer': 'Каждый пункт добавляет ОТДЕЛЬНЫЙ gaṇa-класс по эвристике корпуса поверх класса(ов) Whitney Roots. '
                   'Авторитет: Grammar > Whitney Roots > DCS corpus > Zalizniak (последняя инстанция).',
        'approve_label': 'Оставить добавленный класс (KEEP)',
        'reject_label': 'Откатить к Whitney Roots (REVERT)',
        'filters': [('all', 'Все')],
        'generated': GENERATED,
        'show_ids': True,
        'note_min_height_px': 88,
        'save_as': r'WhitneyRoots\review\whitneyroots-queue-a_kept-class-additions_decisions.json',
    })
    out = OUT_DIR / 'whitneyroots-queue-a_kept-class-additions_review.html'
    out.write_text(html_out, encoding='utf-8')
    print(f'  A -> {out}')


# ---------- Queue B ----------
def build_b():
    data = json.load(open(CAND_DIR / 'queue_b.json', encoding='utf-8'))
    items = []
    for it in data['items']:
        question = kv_table([
            ('Root frequency', esc(it.get('Root frequency'))),
            ('PPP forms listed', esc(it.get('PPP forms listed'))),
            ('Unattested form', f"<b>{esc(it.get('Unattested form'))}</b>"),
            ('Morphology', esc(it.get('Morphology'))),
        ])
        panels = [('Reasoning', f"<p>{esc(it.get('reasoning'))}</p>")]
        items.append({
            'id': it['id'], 'filt': 'all',
            'title': f"#{it['id']} — {it['root']}",
            'badges': ['high-frequency', 'unattested PPP'],
            'question': question,
            'panels': panels,
            'note_placeholder': 'Grammar § that confirms/corrects the PPP form.',
        })
    html_out = render_review_sheet(items=items, config={
        'sheet_id': 'whitneyroots-queue-b_suspicious-high-freq-ppp',
        'title': 'WhitneyRoots — Queue B: подозрительные высокочастотные ППП',
        'subtitle': f'{len(items)} кандидатов · выработано {GENERATED} · Sonnet 5 (claude-sonnet-5), H975',
        'footer': 'Корень встречается 1000+ раз в корпусе, но заявленная форма ППП (причастия прош. страд. '
                   'времени) там не засвидетельствована. Морфология формы чистая — вопрос в том, верна ли '
                   'форма, которую даёт Whitney, а не в её грамматической правильности.',
        'approve_label': 'Форма верна (редкая/поэтическая) — оставить',
        'reject_label': 'Ошибка источника — исправить по Grammar §',
        'filters': [('all', 'Все')],
        'generated': GENERATED,
        'show_ids': True,
        'note_min_height_px': 88,
        'save_as': r'WhitneyRoots\review\whitneyroots-queue-b_suspicious-high-freq-ppp_decisions.json',
    })
    out = OUT_DIR / 'whitneyroots-queue-b_suspicious-high-freq-ppp_review.html'
    out.write_text(html_out, encoding='utf-8')
    print(f'  B -> {out}')


# ---------- Queue C ----------
def build_c():
    data = json.load(open(CAND_DIR / 'queue_c.json', encoding='utf-8'))
    items = []
    for it in data['items']:
        question = kv_table([
            ('PPP forms listed (raw)', esc(it['ppp_str'])),
            ('Suspect form', f"<b>{esc(it['suspect_form'])}</b>"),
            ('Classification', esc(it['classification'])),
            ('Error likelihood', f"{it['error_likelihood_pct']}%"),
            ('Root frequency', f"{it['tokens']} tokens"),
        ])
        panels = [('Reasoning', f"<p>{esc(it['reasoning'])}</p>"),
                  ('Reviewer-guide default', '<p>Correct to the standard <code>-ta</code>/<code>-na</code> form, '
                                              'or delete the fragment; cite the § that gives the true PPP.</p>')]
        items.append({
            'id': it['id'], 'filt': it['classification'],
            'title': f"#{it['id']} — {it['root']}",
            'badges': [it['classification'], f"{it['error_likelihood_pct']}% likely error"],
            'question': question,
            'panels': panels,
            'note_placeholder': 'Corrected PPP form + citing §, or "delete fragment".',
        })
    filt_keys = sorted({it['classification'] for it in data['items']})
    html_out = render_review_sheet(items=items, config={
        'sheet_id': 'whitneyroots-queue-c_malformed-ppp',
        'title': 'WhitneyRoots — Queue C: дефектные ППП (вероятная ошибка)',
        'subtitle': f'{len(items)} кандидатов (полный список, без обрезки до 30) · выработано {GENERATED} · '
                     'Sonnet 5 (claude-sonnet-5), H975',
        'footer': 'Морфологически подозрительные формы ППП — вероятно артефакты извлечения из источника '
                   '(инфинитивные/сандхи-фрагменты типа -tos/-tvi/-tave/-dhyai), а не настоящие причастия.',
        'approve_label': 'Исправить на стандартную -ta/-na форму',
        'reject_label': 'Оставить как есть (форма верна)',
        'filters': [(k, k) for k in filt_keys],
        'generated': GENERATED,
        'show_ids': True,
        'note_min_height_px': 88,
        'save_as': r'WhitneyRoots\review\whitneyroots-queue-c_malformed-ppp_decisions.json',
    })
    out = OUT_DIR / 'whitneyroots-queue-c_malformed-ppp_review.html'
    out.write_text(html_out, encoding='utf-8')
    print(f'  C -> {out}')


# ---------- Queue D ----------
def build_d():
    data = json.load(open(CAND_DIR / 'queue_d.json', encoding='utf-8'))
    items = []
    for it in data['items']:
        risk_key = it['short_root_contamination_risk'].split(' ')[0]
        secs_html = ''
        for s in it['sections'][:12]:
            mark = '⚠ exception' if s.get('is_exception') else (s.get('type') or '?')
            snip = esc(s.get('snippet') or '(no snippet on file)')
            secs_html += f"<div style='margin-bottom:6px;padding:6px;border-left:3px solid #999'><b>{esc(s['label'])}</b> [{esc(mark)}]<br><span style='font-size:0.9em;color:#555'>{snip}</span></div>"
        if len(it['sections']) > 12:
            secs_html += f"<p><i>... +{len(it['sections'])-12} more sections (see queue_d.json id {it['id']})</i></p>"
        question = kv_table([
            ('Meaning', esc(it['meaning'])),
            ('Classes', esc(', '.join(it['classes'] or []) or '∅')),
            ('PPP', esc(', '.join(it['ppp'] or []) or '∅')),
            ('Section count', str(it['section_count'])),
            ('Short-root contamination risk', f"<b>{esc(it['short_root_contamination_risk'])}</b>"),
        ])
        panels = [('Cited sections (up to 12 shown)', secs_html)]
        items.append({
            'id': it['id'], 'filt': risk_key,
            'title': f"#{it['id']} — {it['root']}",
            'badges': [risk_key + ' risk', f"{it['section_count']} sections"],
            'question': question,
            'panels': panels,
            'note_placeholder': 'Which cited section(s), if any, genuinely describe this root deviating.',
        })
    html_out = render_review_sheet(items=items, config={
        'sheet_id': 'whitneyroots-queue-d_grammar-exception-tags',
        'title': 'WhitneyRoots — Queue D: метки «exception» в Grammar',
        'subtitle': f'{len(items)} кандидатов · выработано {GENERATED} · Sonnet 5 (claude-sonnet-5), H975',
        'footer': 'Метка type:"exception" ставилась автоматически, если ключевое слово-исключение оказывалось '
                   'в пределах ~100 символов от корня в тексте Grammar. Короткие корни (as, i, at, ad, am ...) '
                   'совпадают с английскими словами и посторонним текстом — часть меток ложные. '
                   'Совет: начните с HIGH-риска (spot-check ~20).',
        'approve_label': 'Реальное исключение — оставить exception',
        'reject_label': 'Ложное срабатывание — понизить до specific/generic',
        'filters': [('HIGH', 'HIGH риск'), ('MEDIUM', 'MEDIUM риск'), ('LOW', 'LOW риск')],
        'generated': GENERATED,
        'show_ids': True,
        'note_min_height_px': 88,
        'save_as': r'WhitneyRoots\review\whitneyroots-queue-d_grammar-exception-tags_decisions.json',
    })
    out = OUT_DIR / 'whitneyroots-queue-d_grammar-exception-tags_review.html'
    out.write_text(html_out, encoding='utf-8')
    print(f'  D -> {out}')


# ---------- Queue E ----------
def build_e():
    data = json.load(open(CAND_DIR / 'queue_e.json', encoding='utf-8'))
    items = []
    for it in data['items']:
        question = kv_table([
            ('Reverted from (corpus-inflated)', esc(', '.join(it['reverted_from']))),
            ('Restored to (pure Whitney Roots)', f"<b>{esc(', '.join(it['restored_to']))}</b>"),
            ('Reason', esc(it['reason'])),
        ])
        panels = [('Adjudicable by', f"<p>{esc(it['adjudicable_by'])}</p>"),
                  ('How to check', f"<p><code>git show {esc(it['source_commit'][:10])} -- src/app_data.json</code> "
                                    "then an accented source (VedaWeb) or Zalizniak.</p>")]
        items.append({
            'id': it['id'], 'filt': 'all',
            'title': f"#{it['id']} — {it['root']}",
            'badges': ['optional', 'needs accented source'],
            'question': question,
            'panels': panels,
            'note_placeholder': 'Accented-source or Zalizniak citation, if a real class split was found.',
        })
    html_out = render_review_sheet(items=items, config={
        'sheet_id': 'whitneyroots-queue-e_reverted-ivi-pairs',
        'title': 'WhitneyRoots — Queue E (опционально): откаты I/VI пар',
        'subtitle': f'{len(items)} кандидатов · НИЗШИЙ приоритет партии · выработано {GENERATED} · '
                     'Sonnet 5 (claude-sonnet-5), H975',
        'footer': 'Это НЕ ошибки Whitney — просто случаи, о которых неозвученный корпус DCS не может '
                   'высказаться (класс I и VI различаются только ударением). Разрешить их может только '
                   'акцентуированный источник (VedaWeb) или Зализняк. Опционально; наинизший приоритет.',
        'approve_label': 'Найден акцент/Зализняк — класс подтверждён',
        'reject_label': 'Оставить как откат (недостаточно данных)',
        'filters': [('all', 'Все')],
        'generated': GENERATED,
        'show_ids': True,
        'note_min_height_px': 88,
        'save_as': r'WhitneyRoots\review\whitneyroots-queue-e_reverted-ivi-pairs_decisions.json',
    })
    out = OUT_DIR / 'whitneyroots-queue-e_reverted-ivi-pairs_review.html'
    out.write_text(html_out, encoding='utf-8')
    print(f'  E -> {out}')


if __name__ == '__main__':
    print('Building H975 review sheets...')
    build_a()
    build_b()
    build_c()
    build_d()
    build_e()
    print('Done.')
