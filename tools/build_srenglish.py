"""Build Senior Secondary English (302, new syllabus): summaries, lesson practice sets and full papers.

Usage:
  python tools/build_srenglish.py

Lesson sources (data/sr-english/src/lesson-<n>.json) have lesson, title, kind, author, summary
(paragraphs; "## " starts a heading) and any of these question lists:
  mcq       [question, options, answer letter, years?, extra?]      1 mark
  tf        [statement, true/false, years?, extra?]                 1 mark
  match     [{title, pairs: [[left, right]], years?}]               1 mark per pair
  passages  [{title, text, years?, mcq: [...], tf: [...], sa: [[q, a]]}]  reading lessons
  blanks    [sentence with a blank, answer, years?]                 1 mark
  grammar   [task, answer, years?]                                  1 mark, from the lesson's language section
  sa2       [question, answer, years?, {or: [q, a]}?]               2 marks, 30-40 words
  sa3       [question, answer, years?, {or: [q, a]}?]               3 marks
  la4       [task, model answer, years?]                            4 marks (letters, memos, reports)
data/sr-english/src/papers.json holds the unseen passages, grammar and writing tasks of the three
full papers; the lesson-based questions are dealt to them from the lessons (PLAN below), so no
question repeats across papers. The full papers follow April 2026 (new syllabus): 27 questions, 100 marks.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_english import Dealer, marks_total, match_question, open_question, tf_question  # noqa: E402
from build_ss import build_question  # noqa: E402
from convert_lesson import APP_DIR  # noqa: E402

SUBJECT = 'sr-english'
NAME = 'English'
LEVEL = 'senior-secondary'
DATA = APP_DIR / 'data' / SUBJECT

# Which lesson each lesson-based question of a full paper comes from.
# q2: [lesson, passage index]; q4: [lesson, match-set index]; or-pairs: [main, alternative].
PLAN = [
    {'q1': [12, 13, 17], 'q2': [16, 0], 'q3': [3, 4, 7, 8], 'q4': [4, 0], 'q13': [23, 24, 25, 26],
     'q14': [12, 13], 'q15': 12, 'q20': [7, 3]},
    {'q1': [13, 12, 17], 'q2': [18, 0], 'q3': [4, 7, 8, 3], 'q4': [3, 1], 'q13': [24, 25, 26, 23],
     'q14': [13, 12], 'q15': 17, 'q20': [4, 9]},
    {'q1': [17, 13, 12], 'q2': [19, 1], 'q3': [7, 8, 3, 4], 'q4': [9, 0], 'q13': [25, 26, 23, 24],
     'q14': [12, 13], 'q15': 13, 'q20': [8, 3]},
]

META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper (new syllabus)'
INSTRUCTIONS_FULL = [
    'The question paper consists of 27 questions. All questions are compulsory; where there is an OR, answer one.',
    'Questions 1–13 are objective (MCQ, True/False, match, fill in the blanks, one word) of 1 mark per part.',
    'Questions 14–19 carry 2 marks (30–40 words). Question 21 has five parts of 2 marks. Questions 20 and 27 '
    'carry 3 marks, 22 and 24–26 carry 4 marks, and 23 carries 6 marks (150–200 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]
INSTRUCTIONS_LESSON = [
    'Practice for this lesson in the question types of the April 2026 paper (new syllabus).',
    'Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def fixed_tf(q):
    q['fixed'] = True
    return q


def section(no, title, marks, questions, passage=None):
    for i, q in enumerate(questions):
        q['id'] = f'{no}.{i + 1}'
    sec = {'no': no, 'title': title, 'marks': marks, 'fixed': True, 'questions': questions}
    if passage:
        sec['passage'] = passage
    return sec


def tagged(item, years):
    """Add the exam tags of a whole block (e.g. a passage) to an item that has none of its own."""
    if not years:
        return item
    item = list(item)
    pos = 3 if len(item) >= 3 and isinstance(item[1], list) else 2
    while len(item) <= pos:
        item.append(None)
    item[pos] = item[pos] or years
    return item


def mcq(item, years=None):
    return build_question(tagged(item, years), '')


def opn(item, years=None):
    return open_question(tagged(item, years), '')


def tf(item, years=None):
    return tf_question(tagged(item, years), '')


def matches(pairs, years=None):
    out = [match_question(l, r, '', years) for l, r in pairs]
    return out


# ---------- lesson practice sets ----------

def build_lesson(src):
    n = src['lesson']
    secs = []

    def add(title, each, questions, passage=None):
        secs.append(section(len(secs) + 1, title, marks_total(f'{len(questions)} × {each}'), questions, passage))

    if src.get('mcq'):
        add('Choose the correct option.', 1, [mcq(it) for it in src['mcq']])
    if src.get('tf'):
        add('Identify the following sentences as True or False.', 1, [tf(it) for it in src['tf']])
    for m in src.get('match') or []:
        add(m['title'], 1, matches(m['pairs'], m.get('years')))
    for p in src.get('passages') or []:
        ys = p.get('years')
        if p.get('mcq'):
            add('Read the text carefully and choose the correct alternatives.', 1, [mcq(it, ys) for it in p['mcq']], p['text'])
        if p.get('tf'):
            add('Based on the passage above, identify the sentences as True or False.', 1, [tf(it, ys) for it in p['tf']])
        if p.get('sa'):
            add('Answer in about 30 words (passage above).', 2, [opn(it, ys) for it in p['sa']])
    if src.get('blanks'):
        add('Fill in the blanks.', 1, [opn(it) for it in src['blanks']])
    if src.get('grammar'):
        add('Do as directed (language).', 1, [opn(it) for it in src['grammar']])
    if src.get('sa2'):
        add('Answer in 30–40 words.', 2, [opn(it) for it in src['sa2']])
    if src.get('sa3'):
        add('Answer in about 50–60 words.', 3, [opn(it) for it in src['sa3']])
    if src.get('la4'):
        add('Writing task (80–100 words).', 4, [opn(it) for it in src['la4']])

    write(f'lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'title': src['title'],
                               'author': src.get('author') or None,
                               'meta': f'{src.get("kind", "")} · Practice set'.strip(' ·'),
                               'instructions': INSTRUCTIONS_LESSON, 'sections': secs})
    by = f' — {src["author"]}' if src.get('author') else ''
    blocks = [{'type': 'title', 'parts': [['tx', f'Lesson {n}: {src["title"]} — Summary']]},
              {'type': 'para', 'parts': [['tx', f'{src.get("kind", "")}{by}'.strip(' —')]]}]
    for p in src['summary']:
        kind = 'heading' if p.startswith('## ') else 'para'
        blocks.append({'type': kind, 'parts': [['tx', p[3:] if kind == 'heading' else p]]})
    write(f'summary/lesson-{n}.json', {'subject': SUBJECT, 'lesson': n, 'blocks': blocks})
    return sum(len(s['questions']) for s in secs)


# ---------- full papers ----------

def with_title(item, title):
    return [f'{item[0]} ({title})', *item[1:]]


def build_paper(p, src, deal, lessons):
    plan = PLAN[p]
    ys = src.get('years')
    secs = []

    def add(title, marks, questions, passage=None):
        secs.append(section(len(secs) + 1, title, marks, questions, passage))

    def t(n):
        return lessons[n]['title']

    def or_item(main_lesson, alt_lesson, key):
        a = with_title(deal.take(main_lesson, key)[0], t(main_lesson))
        b = with_title(deal.take(alt_lesson, key)[0], t(alt_lesson))
        a = list(a) + [None] * (4 - len(a))
        a[3] = {'or': [b[0], b[1]]}
        return opn(a)

    # 1-13: objective, 1 mark each
    add('Choose the correct option from the given alternatives.', '1 × 3 = 3',
        [mcq(with_title(deal.take(n, 'mcq')[0], t(n))) for n in plan['q1']])
    ln, pi = plan['q2']
    psg = lessons[ln]['passages'][pi]
    deal.used.add((ln, 'passage', pi))
    add('Read the text carefully and choose the correct alternatives.', '1 × 5 = 5',
        [mcq(it, psg.get('years')) for it in psg['mcq'][:5]], psg['text'])
    add('Identify the following sentences as True or False.', '1 × 4 = 4',
        [tf(with_title(deal.take(n, 'tf')[0], t(n))) for n in plan['q3']])
    ln, mi = plan['q4']
    mset = lessons[ln]['match'][mi]
    deal.used.add((ln, 'match', mi))
    add(f"Match Column I with Column II in reference to '{t(ln)}'.", '1 × 3 = 3',
        matches(mset['pairs'][:3], mset.get('years')))
    add('Read the text carefully and choose the correct alternatives.', '1 × 5 = 5',
        [mcq(it, ys) for it in src['q5']['mcq']], src['q5']['passage'])
    add('Read the passage and identify the sentences as True or False.', '1 × 5 = 5',
        [tf(it, ys) for it in src['q6']['tf']], src['q6']['passage'])
    add('Fill in the blanks with the proper tense of the verbs given in brackets.', '1 × 4 = 4',
        [opn(it, ys) for it in src['q7']])
    add('Match Column I with Column II (one-word substitution).', '1 × 4 = 4', matches(src['q8'], ys))
    add('Fill in the blanks with appropriate question words.', '1 × 3 = 3', [opn(it, ys) for it in src['q9']])
    q10 = src['q10']
    add(f"Match the word '{q10['word']}' in Column I with its correct meaning in Column II.", '1 × 4 = 4',
        matches(q10['pairs'], ys))
    add('Fill in the blanks with the correct forms of the words given in brackets.', '1 × 3 = 3',
        [opn(it, ys) for it in src['q11']])
    add('Read the poem and answer the questions.', '1 × 3 = 3', [mcq(it, ys) for it in src['q12']['mcq']],
        src['q12']['poem'])
    add('Choose the correct alternatives (writing skills).', '1 × 4 = 4',
        [mcq(with_title(deal.take(n, 'mcq')[0], t(n))) for n in plan['q13']])

    # 14-20: literature, 30-40 words
    a, b = plan['q14']
    add('Answer in 30–40 words.', '2', [or_item(a, b, 'sa2')])
    add('Answer in 30–40 words.', '2', [opn(with_title(deal.take(plan['q15'], 'sa2')[0], t(plan['q15'])))])
    add('Answer in 30–40 words.', '2', [or_item(9, 9, 'sa2')])
    add('Answer in 30–40 words.', '2', [opn(with_title(deal.take(7, 'sa2')[0], t(7)))])
    add('Answer in 30–40 words.', '2', [or_item(8, 8, 'sa2')])
    add('Answer in 30–40 words.', '2', [opn(with_title(deal.take(10, 'sa2')[0], t(10)))])
    a, b = plan['q20']
    add('Answer in about 50–60 words.', '3', [or_item(a, b, 'sa3')])

    # 21-27: reading, grammar, writing
    add('Read the passage carefully and answer the questions in about 30 words each.', '2 × 5 = 10',
        [opn(it, ys) for it in src['q21']['items']], src['q21']['passage'])
    add('Do as directed.', '1 × 4 = 4', [opn(it, ys) for it in src['q22']])
    add('Answer any one in 150–200 words.', '6', [opn(src['q23'][:2] + [ys, src['q23'][2]])])
    q24 = src['q24']
    add('Answer in 80–100 words.', '4', [opn(q24['q'][:2] + [ys, q24['q'][2]])], q24['passage'])
    add('Writing task (letter or memo).', '4', [or_item(23, 23, 'la4')])
    add('Writing task (report).', '4', [or_item(25, 25, 'la4')])
    add('Writing task (e-mail or job application).', '3', [or_item(24, 26, 'sa3')])

    for s in secs:
        for q in s['questions']:
            if q.get('type') == 'mcq' and q['options'] in (['True', 'False'],):
                q['fixed'] = True
    return {'subject': SUBJECT, 'lesson': 900 + p + 1, 'title': f'Model Question Paper {p + 1}', 'meta': META,
            'instructions': INSTRUCTIONS_FULL, 'sections': secs}


def check_paper(paper):
    marks = 0
    for s in paper['sections']:
        spec = s['marks'].split(' = ')[-1]
        marks += int(spec)
    assert len(paper['sections']) == 27, len(paper['sections'])
    assert marks == 100, marks


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
    subj.update(name=NAME, label='', level=LEVEL)
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
        print(f'Lesson {s["lesson"]}: {build_lesson(s)} questions')
    lessons = {s['lesson']: s for s in sources}
    deal = Dealer(lessons)
    full = json.loads((DATA / 'src' / 'papers.json').read_text(encoding='utf-8'))['papers']
    for p, src in enumerate(full):
        paper = build_paper(p, src, deal, lessons)
        check_paper(paper)
        write(f'paper-{p + 1}.json', paper)
        print(f'paper-{p + 1}: {len(paper["sections"])} questions, 100 marks')
    register(sources, len(full))


if __name__ == '__main__':
    main()
