"""Build Social Science chapter papers, summaries and full model papers.

Usage:
  python tools/build_ss.py            # every data/social-science/src/lesson-*.json
  python tools/build_ss.py 3 4        # only these chapters (full papers are rebuilt every time)

A chapter source (data/social-science/src/lesson-<n>.json) has:
  lesson, title, group (H history, G geography, P polity, C contemporary India),
  summary  - list of paragraphs (a string starting "## " is a heading)
  mcq      - [question, [options], answer letter, years?, extra?]
  objective, vsa, sa, map, la
           - open:   [question, answer, years?, extra?]
             choice: [question, [options], answer letter, years?, extra?]
  extra is a dict merged into the question: "image" (path under data/social-science/),
  "or" ([question, answer]) for an internal choice, "note".

Each chapter gets a practice paper in the April 2026 layout, sized to the chapter, and
three full papers (51 questions, April 2026 layout) are drawn from all chapters without
repeating a question between them.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_lesson import APP_DIR  # noqa: E402

SUBJECT = 'social-science'
DATA = APP_DIR / 'data' / SUBJECT
LETTERS = 'ABCDEFGH'

# key, title, marks per question, words
SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None),
    ('objective', 'Objective type questions (2 parts of 1 mark, or 4 parts of ½ mark).', 2, None),
    ('vsa', 'Very short answer questions.', 2, '30–50 words'),
    ('sa', 'Short answer questions.', 3, '50–80 words'),
    ('map', 'Map-based questions (skill).', 4, None),
    ('la', 'Long answer questions.', 6, '80–120 words'),
]

# Full paper: how many questions of each kind come from each chapter group (April 2026 paper).
FULL_PAPER = {
    'mcq': {'H': 6, 'G': 5, 'P': 6, 'C': 3},
    'objective': {'H': 5, 'G': 4, 'P': 5, 'C': 1},
    'vsa': {'H': 2, 'P': 2, 'C': 2},
    'sa': {'H': 2, 'G': 2, 'C': 2},
    'map': {'G': 2},
    'la': {'H': 1, 'P': 1},
}
FULL_PAPERS = 3

META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–20 carry 1 mark each; questions 21–35 carry 2 marks each.',
    'Section B: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, 6-mark answers in 80–120 words. Map questions carry 4 marks.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]
INSTRUCTIONS_CHAPTER = [
    'Practice set for this chapter in the question types of the April 2026 paper.',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def build_question(item, qid):
    if len(item) >= 3 and isinstance(item[1], list):
        q, options, answer = item[:3]
        if answer not in LETTERS[:len(options)]:
            raise ValueError(f'bad answer {answer!r} in {qid}: {q[:50]}')
        if len(set(options)) != len(options):
            raise ValueError(f'duplicate options in {qid}')
        out = {'id': qid, 'type': 'mcq', 'q': q, 'options': options, 'answer': answer}
        rest = item[3:]
    else:
        q, answer = item[:2]
        out = {'id': qid, 'type': 'open', 'q': q, 'answer': answer}
        rest = item[2:]
    if rest and rest[0]:
        out['years'] = rest[0]
    if len(rest) > 1 and rest[1]:
        extra = dict(rest[1])
        if 'or' in extra:
            alt_q, alt_a = extra.pop('or')
            out['or'] = {'q': alt_q, 'answer': alt_a}
        out.update(extra)
    return out


def section(no, key, questions):
    _, title, marks, words = next(s for s in SECTIONS if s[0] == key)
    sec = {'no': no, 'title': title + (f' Answer in {words}.' if words else ''),
           'marks': f'{len(questions)} × {marks} = {len(questions) * marks}'.replace('.0', ''),
           'type': 'mcq' if key == 'mcq' else 'open', 'questions': questions}
    return sec


def build_chapter(src):
    n = src['lesson']
    sections = []
    for key, *_ in SECTIONS:
        items = src.get(key) or []
        if not items:
            continue
        no = len(sections) + 1
        sections.append(section(no, key, [build_question(it, f'{no}.{i + 1}') for i, it in enumerate(items)]))
    paper = {'subject': SUBJECT, 'lesson': n, 'title': src['title'], 'meta': 'Chapter practice set · Question types of the April 2026 NIOS paper',
             'instructions': INSTRUCTIONS_CHAPTER, 'sections': sections}
    write(f'lesson-{n}.json', paper)

    blocks = [{'type': 'title', 'parts': [['tx', f'Lesson {n}: {src["title"]} — Summary']]}]
    for p in src['summary']:
        if p.startswith('## '):
            blocks.append({'type': 'heading', 'parts': [['tx', p[3:]]]})
        else:
            blocks.append({'type': 'para', 'parts': [['tx', p]]})
    write(f'summary/lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'blocks': blocks})
    return sum(len(s['questions']) for s in sections)


def build_full_papers(sources):
    """Deal questions to the full papers round-robin across the chapters of each group."""
    used = set()
    for p in range(FULL_PAPERS):
        sections = []
        for key, plan in FULL_PAPER.items():
            picked = []
            for group, count in plan.items():
                chapters = [s for s in sources if s['group'] == group]
                k = 0
                tries = 0
                while count and tries < 400:
                    s = chapters[(k + p) % len(chapters)]
                    k += 1
                    tries += 1
                    pool = [(i, it) for i, it in enumerate(s.get(key) or []) if (s['lesson'], key, i) not in used]
                    if not pool:
                        continue
                    i, it = pool[(p * 7 + k) % len(pool)]
                    used.add((s['lesson'], key, i))
                    picked.append((s['lesson'], it))
                    count -= 1
                if count:
                    raise SystemExit(f'Not enough {key} questions in group {group} for full paper {p + 1}')
            no = len(sections) + 1
            picked.sort(key=lambda x: x[0])  # chapter order, like the real paper
            qs = []
            for i, (lesson, it) in enumerate(picked):
                q = build_question(it, f'{no}.{i + 1}')
                q['note'] = (q.get('note', '') + ' ' if q.get('note') else '') + f'Chapter {lesson}.'
                qs.append(q)
            sections.append(section(no, key, qs))
        title = f'Model Question Paper {p + 1}'
        write(f'paper-{p + 1}.json', {'subject': SUBJECT, 'lesson': 900 + p + 1, 'title': title, 'meta': META,
                                      'instructions': INSTRUCTIONS_FULL, 'sections': sections})


def write(rel, obj):
    path = DATA / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def register(sources):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next(s for s in data['subjects'] if s['id'] in (SUBJECT, 'social-studies'))
    subj.update(id=SUBJECT, name='Social Science', label='')
    lessons = [{'no': s['lesson'], 'title': s['title'], 'file': f'data/{SUBJECT}/lesson-{s["lesson"]}.json',
                'summary': f'data/{SUBJECT}/summary/lesson-{s["lesson"]}.json'} for s in sources]
    for p in range(FULL_PAPERS):
        lessons.append({'no': 900 + p + 1, 'tag': 'Full paper', 'title': f'Model Question Paper {p + 1}',
                        'file': f'data/{SUBJECT}/paper-{p + 1}.json'})
    subj['lessons'] = lessons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    only = {int(a) for a in sys.argv[1:]}
    sources = sorted((json.loads(p.read_text(encoding='utf-8')) for p in (DATA / 'src').glob('lesson-*.json')),
                     key=lambda s: s['lesson'])
    for s in sources:
        if not only or s['lesson'] in only:
            print(f'Lesson {s["lesson"]}: {build_chapter(s)} questions')
    if {s['group'] for s in sources} >= set('HGPC'):
        build_full_papers(sources)
        print(f'{FULL_PAPERS} full papers')
    register(sources)


if __name__ == '__main__':
    main()
