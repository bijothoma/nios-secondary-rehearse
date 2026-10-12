"""Build English chapter practice sets, summaries and full model papers.

Usage:
  python tools/build_english.py

Chapter sources (data/english/src/lesson-<n>.json) have: lesson, title, kind, author,
summary (paragraphs; "## " starts a heading), and literature questions in the April 2026
types:
  tf         [statement, true/false, years?, extra?]
  characters [name, role]            (match the character)
  extracts   {passage, items: [[question, answer]], years?}
  complete   [sentence with a blank, answer, years?]
  sa2        [question, answer, years?, extra?]       2 marks, about 30 words
  sa3        [question, answer, years?, {or: [q, a]}] 3 marks, about 40 words
data/english/src/papers.json holds the reading, writing and grammar parts of the three
full papers; the literature questions are dealt to them from the chapters (PLAN below).
The full papers follow April 2026: 35 questions, 100 marks.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_ss import build_question  # noqa: E402
from convert_lesson import APP_DIR  # noqa: E402

SUBJECT = 'english'
DATA = APP_DIR / 'data' / SUBJECT
TF = ['True', 'False']

# Literature questions in each full paper: which chapter each question comes from.
PLAN = [
    {'q12': 19, 'q13': 8, 'q14': [24, 23, 1], 'q15': 5, 'q16': 26, 'q29': 1, 'q30': [22, 13, 23, 14, 3, 12]},
    {'q12': 16, 'q13': 14, 'q14': [13, 26, 27], 'q15': 3, 'q16': 24, 'q29': 13, 'q30': [9, 6, 5, 8, 27, 19]},
    {'q12': 22, 'q13': 27, 'q14': [3, 5, 8], 'q15': 13, 'q16': 1, 'q29': 24, 'q30': [16, 1, 26, 24, 23, 12]},
]

META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
INSTRUCTIONS_FULL = [
    'There are 35 questions in two parts. All questions are compulsory; where there is an OR, answer one.',
    'Part A (questions 1–16) and questions 24–28: objective questions of 1 mark each.',
    'Questions 17–20, 23 and 30–35: 2 marks each, up to 30 words. Question 29: 3 marks, up to 40 words. '
    'Question 22: 4 marks, about 100 words. Question 21: 6 marks, 150–200 words.',
    'Literature questions from previous NIOS papers show the exam they appeared in.',
]
INSTRUCTIONS_CHAPTER = [
    'Literature practice for this lesson in the question types of the April 2026 paper.',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def tf_question(item, qid):
    statement, is_true, *rest = item
    q = build_question([statement, TF, 'A' if is_true else 'B', *rest], qid)
    q['fixed'] = True
    return q


def open_question(item, qid):
    if len(item) == 3 and isinstance(item[2], dict):  # [q, a, {or}] without years
        item = [item[0], item[1], None, item[2]]
    return build_question(item, qid)


def match_question(left, right, qid, years=None):
    q = {'id': qid, 'type': 'match', 'left': left, 'right': right, 'answer': f'{left} — {right}'}
    if years:
        q['years'] = years
    return q


def section(no, title, marks, questions, passage=None):
    sec = {'no': no, 'title': title, 'marks': marks, 'fixed': True, 'questions': questions}
    if passage:
        sec['passage'] = passage
    return sec


def ids(no, items, make):
    return [make(it, f'{no}.{i + 1}') for i, it in enumerate(items)]


# ---------- chapter practice sets ----------

def build_chapter(src):
    n = src['lesson']
    secs = []

    def add(title, marks, questions, passage=None):
        secs.append(section(len(secs) + 1, title, marks, questions, passage))

    no = lambda: len(secs) + 1  # noqa: E731
    if src.get('tf'):
        add('Identify the following sentences as True or False.', f'{len(src["tf"])} × 1', ids(no(), src['tf'], tf_question))
    chars = src.get('characters') or []
    if len(chars) >= 2:
        add('Match the character (or speaker) with the description.', f'{len(chars)} × 1',
            [match_question(c, r, f'{no()}.{i + 1}') for i, (c, r) in enumerate(chars)])
    for ex in src.get('extracts') or []:
        items = [[q, a, ex.get('years')] for q, a in ex['items']]
        add('Read the passage and fill in the blanks.', f'{len(items)} × 1', ids(no(), items, open_question), ex['passage'])
    if src.get('complete'):
        add('Complete the following sentences.', f'{len(src["complete"])} × 1', ids(no(), src['complete'], open_question))
    if src.get('sa2'):
        add('Answer in one or two sentences (about 30 words).', f'{len(src["sa2"])} × 2', ids(no(), src['sa2'], open_question))
    if src.get('sa3'):
        add('Answer in about 40 words.', f'{len(src["sa3"])} × 3', ids(no(), src['sa3'], open_question))
    for s in secs:
        s['marks'] = marks_total(s['marks'])

    title = src['title']
    write(f'lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'title': title,
                               'author': src.get('author') or None,
                               'meta': f'{src.get("kind", "")} · Literature practice set'.strip(' ·'),
                               'instructions': INSTRUCTIONS_CHAPTER, 'sections': secs})
    by = f' — {src["author"]}' if src.get('author') else ''
    blocks = [{'type': 'title', 'parts': [['tx', f'Lesson {n}: {title} — Summary']]},
              {'type': 'para', 'parts': [['tx', f'{src.get("kind", "")}{by}'.strip(' —')]]}]
    for p in src['summary']:
        kind = 'heading' if p.startswith('## ') else 'para'
        blocks.append({'type': kind, 'parts': [['tx', p[3:] if kind == 'heading' else p]]})
    write(f'summary/lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'blocks': blocks})
    return sum(len(s['questions']) for s in secs)


def marks_total(spec):
    count, each = (int(x) for x in spec.split(' × '))
    return f'{count} × {each} = {count * each}'


# ---------- full papers ----------

class Dealer:
    """Hands out unused literature items so the three papers never repeat a question."""

    def __init__(self, chapters):
        self.ch = chapters
        self.used = set()

    def take(self, lesson, key, k=1):
        items = self.ch[lesson].get(key) or []
        out = []
        for i, it in enumerate(items):
            if (lesson, key, i) not in self.used and len(out) < k:
                self.used.add((lesson, key, i))
                out.append(it)
        if len(out) < k:
            raise SystemExit(f'Lesson {lesson} has too few "{key}" items')
        return out


def with_title(item, title):
    return [f'{item[0]} ({title})', *item[1:]]


def build_paper(p, src, deal, chapters):
    plan = PLAN[p]
    secs = []

    def add(title, marks, questions, passage=None):
        no = len(secs) + 1
        for i, q in enumerate(questions):
            q['id'] = f'{no}.{i + 1}'
        secs.append(section(no, title, marks, questions, passage))

    def t(lesson):
        return chapters[lesson]['title']

    ra = src['readingA']
    # PART A — Section A: Reading (7)
    add('PART A · Section A: Reading. Answer in ONE word.', '3 × 1 = 3',
        ids(1, ra['oneword'], open_question), ra['passage'])
    add('Choose the correct option (from the passage above).', '1 × 1 = 1', [build_question(ra['synonym'], '')])
    add('Based on the passage above, write True or False.', '3 × 1 = 3', ids(3, ra['tf'], tf_question))
    # Section B: Writing (13)
    for key, title, n in (('notice', 'notice', 4), ('article', 'article', 4), ('letter', 'letter', 5)):
        w = src[key]
        add(f'Section B: Writing ({title}). Answer the questions with reference to the context.',
            f'{n} × 1 = {n}', [build_question(it, '') for it in w['mcq']], w['task'])
    # Section C: Grammar (15)
    add('Section C: Grammar. Choose the correct option to complete the note.', '3 × 1 = 3',
        [build_question(it, '') for it in src['note']['mcq']], src['note']['text'])
    add('Fill in the blanks with the correct form of the verbs given in brackets.', '3 × 1 = 3',
        [open_question(it, '') for it in src['verbs3']['items']], src['verbs3']['text'])
    add('Choose the correct option to fill in the blanks.', '3 × 1 = 3', [build_question(it, '') for it in src['choose']])
    add('Fill in the blanks with the correct prepositions.', '4 × 1 = 4', [open_question(it, '') for it in src['prep4']])
    add('Fill in the blanks with the correct conjunctions.', '2 × 1 = 2', [open_question(it, '') for it in src['conj2']])
    # Section D: Literature (15)
    for key in ('q12', 'q13'):
        lesson = plan[key]
        add(f'Section D: Literature. Identify the sentences as True or False ({t(lesson)}).' if key == 'q12'
            else f'Identify the sentences as True or False ({t(lesson)}).', '3 × 1 = 3',
            [tf_question(it, '') for it in deal.take(lesson, 'tf', 3)])
    matches = []
    for lesson in plan['q14']:
        name, _ = deal.take(lesson, 'characters')[0]
        matches.append(match_question(name, t(lesson), ''))
    add('Match the characters with the story.', '3 × 1 = 3', matches)
    ex = deal.take(plan['q15'], 'extracts')[0]
    add(f'Read the passage and fill in the blanks ({t(plan["q15"])}).', '3 × 1 = 3',
        [open_question([q, a, ex.get('years')], '') for q, a in ex['items'][:3]], ex['passage'])
    add(f'Complete the following sentences ({t(plan["q16"])}).', '3 × 1 = 3',
        [open_question(it, '') for it in deal.take(plan['q16'], 'complete', 3)])

    rb = src['readingB']
    # PART B — Section A: Reading (8)
    add('PART B · Section A: Reading. Find words from the passage.', '1 × 2 = 2',
        [open_question(rb['words'], '')], rb['passage'])
    for q in rb['qa']:
        add('Answer the question (passage above).', '1 × 2 = 2', [open_question(q, '')])
    # Section B: Writing (12)
    add('Section B: Writing. Answer in 150–200 words.', '1 × 6 = 6', [open_question(src['long'], '')])
    add('Answer in about 100 words.', '1 × 4 = 4', [open_question(src['letter4'], '')])
    add('Write the message (about 40 words).', '1 × 2 = 2', [open_question(src['message'], '')])
    # Section C: Grammar (15)
    add('Section C: Grammar. Change into reported speech.', '3 × 1 = 3', [open_question(it, '') for it in src['reported']])
    add('Fill in the blanks with appropriate prepositions.', '2 × 1 = 2', [open_question(it, '') for it in src['prep2']])
    add('Complete the dialogue with suitable words.', '2 × 1 = 2',
        [open_question(it, '') for it in src['dialogue']['items']], src['dialogue']['text'])
    add('Fill in the blanks with the correct form of the verbs.', '4 × 1 = 4', [open_question(it, '') for it in src['verbs4']])
    add('Complete the sentences using proper conjunctions.', '4 × 1 = 4', [open_question(it, '') for it in src['conj4']])
    # Section D: Literature (15)
    sa3 = deal.take(plan['q29'], 'sa3')[0]
    sa3 = with_title(sa3, t(plan['q29']))
    add('Section D: Literature. Answer in about 40 words.', '1 × 3 = 3', [open_question(sa3, '')])
    for lesson in plan['q30']:
        item = with_title(deal.take(lesson, 'sa2')[0], t(lesson))
        add('Answer in one or two sentences (about 30 words).', '1 × 2 = 2', [open_question(item, '')])

    for s in secs:
        for q in s['questions']:
            if q.get('type') == 'mcq' and len(q['options']) == 2:
                q['fixed'] = True
    return {'subject': SUBJECT, 'lesson': 900 + p + 1, 'title': f'Model Question Paper {p + 1}', 'meta': META,
            'instructions': INSTRUCTIONS_FULL, 'sections': secs}


def write(rel, obj):
    path = DATA / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def register(sources, papers):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next(s for s in data['subjects'] if s['id'] == SUBJECT)
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
    chapters = {s['lesson']: s for s in sources}
    deal = Dealer(chapters)
    full = json.loads((DATA / 'src' / 'papers.json').read_text(encoding='utf-8'))['papers']
    for p, src in enumerate(full):
        paper = build_paper(p, src, deal, chapters)
        write(f'paper-{p + 1}.json', paper)
        print(f'paper-{p + 1}: {len(paper["sections"])} questions')
    register(sources, len(full))


if __name__ == '__main__':
    main()
