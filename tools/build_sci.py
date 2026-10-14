"""Build Science and Technology chapter papers, summaries and full model papers.

Usage:
  python tools/build_sci.py

A chapter source (data/science/src/lesson-<n>.json) has:
  lesson, title, module (1-7),
  summary   - list of paragraphs (a string starting "## " is a heading)
  mcq       - [question, [options], answer letter, years?, extra?]
  objective - [question, answer, years?, extra?]   2 marks: two 1-mark parts (fill in the blanks,
              match the columns, true/false, or a short passage with two questions)
  case      - {passage, items: [[question, [options], answer letter], ...], years?}   5 × 1 mark
  vsa, sa, la
            - [question, answer, years?, extra?]
  extra is a dict: "or" ([question, answer]) for an internal choice, "note".

The April 2026 paper (43 questions, 85 marks) has: 17 MCQs; ten 2-mark objective questions made
of two 1-mark parts; one passage with five 1-mark MCQs; 6 very short (2), 7 short (3) and
2 long (5) answer questions. Each chapter gets a practice set in these question types and three
full papers are drawn from all chapters without repeating a question between them.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_ss import build_question  # noqa: E402
from convert_lesson import APP_DIR  # noqa: E402

SUBJECT = 'science'
NAME = 'Science and Technology'
DATA = APP_DIR / 'data' / SUBJECT

# key, title, marks per question, words, questions in a full paper
SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 17),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(fill in the blanks, match the columns, true/false or a short passage).', 2, None, 10),
    ('case', 'Read the passage and answer the questions that follow.', 1, None, 1),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 6),
    ('sa', 'Short answer questions.', 3, '50–80 words', 7),
    ('la', 'Long answer questions.', 5, '80–120 words', 2),
]
FULL_PAPERS = 3

META = 'Time: 2½ hours · Maximum marks: 85 · Modelled on the April 2026 NIOS paper'
INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–17 are MCQs (1 mark each); questions 18–27 have two parts of 1 mark each; '
    'question 28 is a passage with five 1-mark questions.',
    'Section B: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, 5-mark answers in 80–120 words.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]
INSTRUCTIONS_CHAPTER = [
    'Practice set for this lesson in the question types of the April 2026 paper.',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def section(no, key, questions, passage=None, years=None):
    _, title, marks, words, _ = next(s for s in SECTIONS if s[0] == key)
    sec = {'no': no, 'title': title + (f' Answer in {words}.' if words else ''),
           'marks': f'{len(questions)} × {marks} = {len(questions) * marks}',
           'questions': questions}
    if key == 'case':
        sec['fixed'] = True  # the questions follow the passage in order
    if passage:
        sec['passage'] = passage + (f' ({", ".join(years)})' if years else '')
    return sec


def case_section(no, case, note=None):
    qs = [build_question(it, f'{no}.{i + 1}') for i, it in enumerate(case['items'])]
    if note:
        qs[0]['note'] = note
    return section(no, 'case', qs, case['passage'], case.get('years'))


def chapter_sections(src):
    sections = []
    for key, *_ in SECTIONS:
        no = len(sections) + 1
        if key == 'case':
            cases = src.get('case') or []
            for case in (cases if isinstance(cases, list) else [cases]):
                sections.append(case_section(len(sections) + 1, case))
            continue
        items = src.get(key) or []
        if items:
            sections.append(section(no, key, [build_question(it, f'{no}.{i + 1}') for i, it in enumerate(items)]))
    return sections


def build_chapter(src):
    n = src['lesson']
    sections = chapter_sections(src)
    write(f'lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'title': src['title'],
                               'meta': 'Lesson practice set · Question types of the April 2026 NIOS paper',
                               'instructions': INSTRUCTIONS_CHAPTER, 'sections': sections})

    blocks = [{'type': 'title', 'parts': [['tx', f'Lesson {n}: {src["title"]} — Summary']]}]
    for p in src['summary']:
        kind = 'heading' if p.startswith('## ') else 'para'
        blocks.append({'type': kind, 'parts': [['tx', p[3:] if kind == 'heading' else p]]})
    write(f'summary/lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'blocks': blocks})
    return sum(len(s['questions']) for s in sections)


def cases_of(src):
    cases = src.get('case') or []
    return cases if isinstance(cases, list) else [cases]


def build_full_papers(sources):
    """Deal questions round-robin over the lessons, starting at a different lesson for each paper."""
    used = set()
    order = [s['lesson'] for s in sources]
    by_no = {s['lesson']: s for s in sources}
    for p in range(FULL_PAPERS):
        sections = []
        for key, _, _, _, count in SECTIONS:
            no = len(sections) + 1
            if key == 'case':
                pool = [(s['lesson'], i, c) for s in sources for i, c in enumerate(cases_of(s))
                        if (s['lesson'], 'case', i) not in used]
                lesson, i, case = pool[(p * 7) % len(pool)]
                used.add((lesson, 'case', i))
                sections.append(case_section(no, case, f'Lesson {lesson}.'))
                continue
            start = (p * 11 + {'mcq': 0, 'objective': 3, 'vsa': 5, 'sa': 9, 'la': 13}[key]) % len(order)
            picked = []
            k = 0
            while len(picked) < count and k < 10 * len(order):
                lesson = order[(start + k * (1 if count > 6 else 3)) % len(order)]
                k += 1
                pool = [(i, it) for i, it in enumerate(by_no[lesson].get(key) or [])
                        if (lesson, key, i) not in used]
                if not pool or any(l == lesson for l, _ in picked) and count <= len(order):
                    continue
                i, it = pool[(p * 5 + k) % len(pool)]
                used.add((lesson, key, i))
                picked.append((lesson, it))
            if len(picked) < count:
                raise SystemExit(f'Not enough {key} questions for full paper {p + 1}')
            picked.sort(key=lambda x: x[0])  # lesson order, like the real paper
            qs = []
            for i, (lesson, it) in enumerate(picked):
                q = build_question(it, f'{no}.{i + 1}')
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


def register(sources, papers):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next((s for s in data['subjects'] if s['id'] == SUBJECT), None)
    if subj is None:
        subj = {'id': SUBJECT}
        data['subjects'].append(subj)
    subj.update(name=NAME, label='')
    lessons = [{'no': s['lesson'], 'title': s['title'], 'file': f'data/{SUBJECT}/lesson-{s["lesson"]}.json',
                'summary': f'data/{SUBJECT}/summary/lesson-{s["lesson"]}.json'} for s in sources]
    for p in range(papers):
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
    papers = 0
    if len(sources) >= 10:
        build_full_papers(sources)
        papers = FULL_PAPERS
        print(f'{FULL_PAPERS} full papers')
    register(sources, papers)


if __name__ == '__main__':
    main()
