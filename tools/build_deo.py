"""Build Data Entry Operations chapter papers, summaries and full model papers.

Usage:
  python tools/build_deo.py

A chapter source (data/data-entry/src/lesson-<n>.json) has:
  lesson, title,
  summary  - list of paragraphs (a string starting "## " is a heading)
  mcq      - [question, [options], answer letter, years?, extra?]
  ar       - [assertion, reason, answer letter (A-D as in the April 2026 paper), years?, extra?]
  fill2, oneword, vsa, sa, la
           - [question, answer, years?, extra?]
  tf       - [statement, true/false, years?, extra?]
  extra is a dict: "or" ([question, answer]) for an internal choice, "note".

The April 2026 paper (25 questions, 40 marks) has: 7 MCQs; three 2-mark questions made of
two 1-mark parts (assertion-reason, fill in the blanks, true/false); 7 one-mark questions;
5 very short (2), 2 short (3) and 1 long (4) answer questions. Each chapter gets a practice
set in these question types and three full papers are drawn from all chapters without
repeating a question between them.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_ss import build_question  # noqa: E402
from convert_lesson import APP_DIR  # noqa: E402

SUBJECT = 'data-entry'
NAME = 'Data Entry Operations'
DATA = APP_DIR / 'data' / SUBJECT

AR_OPTIONS = [
    'Both A and R are true and R is the correct explanation of A.',
    'Both A and R are true but R is not the correct explanation of A.',
    'A is true but R is false.',
    'A is false but R is true.',
]

# key, title, marks per question, words, questions in a full paper
SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 7),
    ('ar', 'Assertion (A) and Reason (R): choose the correct option.', 1, None, 2),
    ('fill2', 'Fill in the blanks.', 1, None, 2),
    ('tf', 'State True or False.', 1, None, 2),
    ('oneword', 'Fill in the blank or answer in one word.', 1, None, 7),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 5),
    ('sa', 'Short answer questions.', 3, '50–80 words', 2),
    ('la', 'Long answer question.', 4, '80–120 words', 1),
]

# Order in which chapters are visited when dealing questions to the full papers; the
# bigger chapters (Word, formulas and charts, PowerPoint) come up more often.
DEAL_ORDER = {
    'la': [5, 9, 8, 4, 1, 7],
    'sa': [1, 9, 4, 8, 5, 7, 9, 1, 4, 8, 5, 9],
}
DEFAULT_ORDER = [4, 8, 9, 1, 7, 5, 4, 8, 9, 1, 5, 7]
FULL_PAPERS = 3

META = 'Time: 2 hours · Maximum marks: 40 · Modelled on the April 2026 NIOS paper'
INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–7 are MCQs (1 mark each); questions 8–10 have two parts of 1 mark each '
    '(assertion–reason, fill in the blanks, true/false); questions 11–17 carry 1 mark each.',
    'Section B: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, the 4-mark answer in 80–120 words.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]
INSTRUCTIONS_CHAPTER = [
    'Practice set for this chapter in the question types of the April 2026 paper.',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def normalise(key, item):
    """Turn the short source forms into the forms build_question understands."""
    if key == 'ar':
        assertion, reason, answer, *rest = item
        return [f'Assertion (A): {assertion} — Reason (R): {reason}', AR_OPTIONS, answer, *rest]
    if key == 'tf':
        statement, is_true, *rest = item
        return [statement, ['True', 'False'], 'A' if is_true else 'B', *rest]
    return item


def question(key, item, qid):
    q = build_question(normalise(key, item), qid)
    if key in ('ar', 'tf'):
        q['fixed'] = True  # options keep their printed order
    return q


def section(no, key, questions):
    _, title, marks, words, _ = next(s for s in SECTIONS if s[0] == key)
    return {'no': no, 'title': title + (f' Answer in {words}.' if words else ''),
            'marks': f'{len(questions)} × {marks} = {len(questions) * marks}',
            'questions': questions}


def build_chapter(src):
    n = src['lesson']
    sections = []
    for key, *_ in SECTIONS:
        items = src.get(key) or []
        if items:
            no = len(sections) + 1
            sections.append(section(no, key, [question(key, it, f'{no}.{i + 1}') for i, it in enumerate(items)]))
    write(f'lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'title': src['title'],
                               'meta': 'Chapter practice set · Question types of the April 2026 NIOS paper',
                               'instructions': INSTRUCTIONS_CHAPTER, 'sections': sections})

    blocks = [{'type': 'title', 'parts': [['tx', f'Lesson {n}: {src["title"]} — Summary']]}]
    for p in src['summary']:
        kind = 'heading' if p.startswith('## ') else 'para'
        blocks.append({'type': kind, 'parts': [['tx', p[3:] if kind == 'heading' else p]]})
    write(f'summary/lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'blocks': blocks})
    return sum(len(s['questions']) for s in sections)


def build_full_papers(sources):
    by_no = {s['lesson']: s for s in sources}
    used = set()
    for p in range(FULL_PAPERS):
        sections = []
        for key, _, _, _, count in SECTIONS:
            order = [c for c in DEAL_ORDER.get(key, DEFAULT_ORDER) if c in by_no]
            start = p * count
            picked = []
            k = 0
            while len(picked) < count and k < 10 * len(order):
                lesson = order[(start + k) % len(order)]
                k += 1
                pool = [(i, it) for i, it in enumerate(by_no[lesson].get(key) or [])
                        if (lesson, key, i) not in used]
                if not pool:
                    continue
                i, it = pool[(p * 5 + k) % len(pool)]
                used.add((lesson, key, i))
                picked.append((lesson, it))
            if len(picked) < count:
                raise SystemExit(f'Not enough {key} questions for full paper {p + 1}')
            picked.sort(key=lambda x: x[0])  # chapter order, like the real paper
            no = len(sections) + 1
            qs = []
            for i, (lesson, it) in enumerate(picked):
                q = question(key, it, f'{no}.{i + 1}')
                q['note'] = (q['note'] + ' ' if q.get('note') else '') + f'Lesson {lesson}.'
                qs.append(q)
            sections.append(section(no, key, qs))
        write(f'paper-{p + 1}.json', {'subject': SUBJECT, 'lesson': 900 + p + 1,
                                      'title': f'Model Question Paper {p + 1}', 'meta': META,
                                      'instructions': INSTRUCTIONS_FULL, 'sections': sections})


def write(rel, obj):
    path = DATA / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def register(sources):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next(s for s in data['subjects'] if s['id'] == SUBJECT)
    subj.update(name=NAME, label='')
    lessons = [{'no': s['lesson'], 'title': s['title'], 'file': f'data/{SUBJECT}/lesson-{s["lesson"]}.json',
                'summary': f'data/{SUBJECT}/summary/lesson-{s["lesson"]}.json'} for s in sources]
    for p in range(FULL_PAPERS):
        lessons.append({'no': 900 + p + 1, 'tag': 'Full paper', 'title': f'Model Question Paper {p + 1}',
                        'file': f'data/{SUBJECT}/paper-{p + 1}.json'})
    subj['lessons'] = lessons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sources = sorted((json.loads(p.read_text(encoding='utf-8')) for p in (DATA / 'src').glob('lesson-*.json')),
                     key=lambda s: s['lesson'])
    for s in sources:
        print(f'Lesson {s["lesson"]}: {build_chapter(s)} questions')
    build_full_papers(sources)
    print(f'{FULL_PAPERS} full papers')
    register(sources)


if __name__ == '__main__':
    main()
