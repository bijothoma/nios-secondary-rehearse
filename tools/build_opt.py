"""Build lesson papers, summaries and full model papers for a subject that has optional modules
(Home Science 321 and Tourism 337, Senior Secondary).

A subject script (build_homesci.py, build_tourism.py) sets the fields below and calls main().

A lesson source (data/<subject>/src/lesson-<n>.json) has the same fields as a Science source (see build_sci.py):
lesson, title, module, summary, mcq, objective, vsa, sa, la, plus 'group' ('A' or 'B') for a lesson of an optional
module. The full papers draw the compulsory sections from the lessons without a group and add one extra block of
questions for each optional module, drawn only from that module's lessons (as the real paper asks Option A or B).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402
from build_sci import APP_DIR, build_question, write  # noqa: E402

SUBJECT = ''
NAME = ''
LEVEL = 'senior-secondary'
DATA = None
META = ''
FULL_PAPERS = 3
# key, title, marks per question, words
TYPES = {}
# questions in a full paper for the compulsory part and for each optional module, by key
COMPULSORY = {}
OPTIONAL = {}
GROUPS = {}  # group letter -> module name
INSTRUCTIONS_FULL = []
INSTRUCTIONS_CHAPTER = [
    'Practice set for this lesson in the question types of the April 2026 paper.',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]
ORDER = ['mcq', 'objective', 'vsa', 'sa', 'la']
OPTIONAL_SECTION_ORDER = ['mcq', 'objective', 'vsa', 'sa']
OFFSET = {'mcq': 0, 'objective': 3, 'vsa': 5, 'sa': 2, 'la': 1}


def make_section(no, key, questions, prefix=''):
    _, title, marks, words = TYPES[key]
    return {'no': no, 'title': prefix + title + (f' Answer in {words}.' if words else ''),
            'marks': f'{len(questions)} × {marks} = {len(questions) * marks}', 'questions': questions}


def chapter_sections(src):
    sections = []
    for key in ORDER:
        items = src.get(key) or []
        if items:
            no = len(sections) + 1
            sections.append(make_section(no, key, [build_question(it, f'{no}.{i + 1}') for i, it in enumerate(items)]))
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


def deal(lessons, key, count, p, used):
    """Take `count` unused questions of a type round-robin over the lessons, starting at a different lesson per paper."""
    picked = []
    n = len(lessons)
    start = (p * 4 + OFFSET.get(key, 0)) % n
    rounds = 0
    while len(picked) < count and rounds < 50:
        for k in range(n):
            if len(picked) >= count:
                break
            src = lessons[(start + k) % n]
            pool = [i for i in range(len(src.get(key) or [])) if (src['lesson'], key, i) not in used]
            if not pool:
                continue
            i = pool[(p * 3 + rounds) % len(pool)]
            used.add((src['lesson'], key, i))
            picked.append((src['lesson'], src[key][i]))
        rounds += 1
    if len(picked) < count:
        raise SystemExit(f'Not enough {key} questions for paper {p + 1}: need {count}, found {len(picked)}')
    picked.sort(key=lambda x: x[0])
    return picked


def to_section(no, key, picked, prefix=''):
    qs = []
    for i, (lesson, it) in enumerate(picked):
        q = build_question(it, f'{no}.{i + 1}')
        q['note'] = (q['note'] + ' ' if q.get('note') else '') + f'Lesson {lesson}.'
        qs.append(q)
    return make_section(no, key, qs, prefix)


def build_full_papers(sources):
    used = set()
    core = [s for s in sources if not s.get('group')]
    for p in range(FULL_PAPERS):
        sections = []
        for key in ORDER:
            count = COMPULSORY.get(key, 0)
            if count:
                sections.append(to_section(len(sections) + 1, key, deal(core, key, count, p, used)))
        for g, gname in GROUPS.items():
            lessons = [s for s in sources if s.get('group') == g]
            for key in OPTIONAL_SECTION_ORDER:
                count = OPTIONAL.get(key, 0)
                if count:
                    sections.append(to_section(len(sections) + 1, key, deal(lessons, key, count, p, used),
                                               f'Optional {gname}: '))
        write(f'paper-{p + 1}.json', {'subject': SUBJECT, 'lesson': 900 + p + 1,
                                      'title': f'Model Question Paper {p + 1}', 'meta': META,
                                      'instructions': INSTRUCTIONS_FULL, 'sections': sections})


def register(sources, papers):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next((s for s in data['subjects'] if s['id'] == SUBJECT), None)
    if subj is None:
        subj = {'id': SUBJECT}
        data['subjects'].append(subj)
    subj.update(name=NAME, label='', level=LEVEL)
    lessons = [{'no': s['lesson'], 'title': s['title'], 'file': f'data/{SUBJECT}/lesson-{s["lesson"]}.json',
                'summary': f'data/{SUBJECT}/summary/lesson-{s["lesson"]}.json'} for s in sources]
    for p in range(papers):
        lessons.append({'no': 900 + p + 1, 'tag': 'Full paper', 'title': f'Model Question Paper {p + 1}',
                        'file': f'data/{SUBJECT}/paper-{p + 1}.json'})
    subj['lessons'] = lessons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main(min_lessons=None):
    sys.stdout.reconfigure(encoding='utf-8')
    build_sci.SUBJECT = SUBJECT
    build_sci.DATA = DATA
    sources = sorted((json.loads(p.read_text(encoding='utf-8')) for p in (DATA / 'src').glob('lesson-*.json')),
                     key=lambda s: s['lesson'])
    for s in sources:
        print(f'Lesson {s["lesson"]}: {build_chapter(s)} questions')
    papers = 0
    if min_lessons is not None and len(sources) >= min_lessons:
        build_full_papers(sources)
        papers = FULL_PAPERS
        print(f'{FULL_PAPERS} full papers')
    register(sources, papers)
