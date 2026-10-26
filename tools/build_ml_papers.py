"""Build full Malayalam model question papers from the lesson papers.

Usage:
  python tools/build_ml_papers.py

Every data/malayalam/lesson-<n>.json already follows the April 2026 layout
(10 sections). This script mixes questions from all lessons into three full papers
in the same layout, without reusing a question across the papers:
  1 MCQ 20, 2 one word 5, 3 fill in 5, 4 true/false 5, 5 match 5, 6 synonyms 5,
  7 join 5, 8 short 15 (answer any 10), 9 medium 8 (answer any 5),
  10 long 3, each with an OR question from another lesson.
Each question gets a note naming its lesson. The papers are registered in
data/subjects.json as lessons 901-903 with the tag 'Full paper'.
"""
import json
import random
import re
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
SUBJECT = 'malayalam'
DATA = APP_DIR / 'data' / SUBJECT
PAPERS = 3
SEED = 2026

TRUE_FALSE = {'ശരി', 'തെറ്റ്'}

# Questions that point at 'this poem', 'here' etc. need the lesson name once mixed.
CONTEXT = re.compile(r'ഈ (പാഠ|കവിത|കഥ|ലേഖന|ഭാഗ)|ഇവിടെ|പ്രസ്തുത')

# section no, title, marks, number of questions
SECTIONS = [
    (1, 'ശരിയായ ഉത്തരം തെരഞ്ഞെടുത്ത് എഴുതുക.', '20 × 1 = 20', 20),
    (2, 'ഒറ്റവാക്കിൽ ഉത്തരമെഴുതുക.', '5 × 1 = 5', 5),
    (3, 'വിട്ടുപോയ ഭാഗം ബ്രാക്കറ്റിൽനിന്ന് ശരിയായത് തെരഞ്ഞെടുത്ത് പൂരിപ്പിക്കുക.', '5 × 1 = 5', 5),
    (4, 'താഴെ തന്നിരിക്കുന്നവ ശരിയോ തെറ്റോ എന്ന് രേഖപ്പെടുത്തുക.', '5 × 1 = 5', 5),
    (5, 'ചേരുംപടി ചേർക്കുക.', '5 × 1 = 5', 5),
    (6, 'പകരം പദം എഴുതുക.', '5 × 1 = 5', 5),
    (7, 'ചേർത്തെഴുതുക.', '5 × 1 = 5', 5),
    (8, 'ഏതെങ്കിലും 10 ചോദ്യങ്ങൾക്ക് 20–25 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '10 × 2 = 20', 15),
    (9, 'ഏതെങ്കിലും 5 ചോദ്യങ്ങൾക്ക് 40–45 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '5 × 3 = 15', 8),
    (10, 'താഴെ പറയുന്ന ചോദ്യങ്ങൾക്ക് 100–150 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '3 × 5 = 15', 3),
]

META = 'സമയം: 3 മണിക്കൂർ · ആകെ മാർക്ക്: 100 · 2026 ഏപ്രിൽ ചോദ്യപേപ്പറിന്റെ മാതൃകയിൽ'
INSTRUCTIONS = [
    'എല്ലാ പാഠങ്ങളിൽനിന്നുമുള്ള ചോദ്യങ്ങൾ ചേർത്ത് തയ്യാറാക്കിയ മുഴുവൻ ചോദ്യപേപ്പർ.',
    'എല്ലാ ചോദ്യങ്ങൾക്കും നിർദ്ദേശാനുസരണം ഉത്തരം എഴുതുക.',
    '8-ാം ചോദ്യത്തിൽ ഏതെങ്കിലും 10 ചോദ്യങ്ങൾക്കും 9-ാം ചോദ്യത്തിൽ ഏതെങ്കിലും 5 ചോദ്യങ്ങൾക്കും ഉത്തരം എഴുതുക.',
    '10-ാം ചോദ്യത്തിൽ “അല്ലെങ്കിൽ” എന്ന് നൽകിയിട്ടുള്ളവയിൽ ഏതെങ്കിലും ഒന്നിന് ഉത്തരം എഴുതുക.',
    'ഓരോ ചോദ്യവും ഏത് പാഠത്തിൽനിന്നാണെന്ന് ഉത്തരത്തോടൊപ്പം നൽകിയിട്ടുണ്ട്.',
    'മുൻവർഷ ചോദ്യപേപ്പറുകളിൽ വന്ന ചോദ്യങ്ങൾക്കൊപ്പം പരീക്ഷയുടെ മാസവും വർഷവും നൽകിയിട്ടുണ്ട്.',
]


def usable(sec_no, q):
    """Keep each section to the question type the April 2026 paper uses there."""
    if sec_no == 4:  # some lessons use section 4 for 'complete the lines'
        return q['type'] == 'mcq' and set(q['options']) == TRUE_FALSE
    if sec_no in (1, 3):
        return q['type'] == 'mcq'
    if sec_no == 5:
        return q['type'] == 'match'
    return q['type'] == 'open'


def label(lesson):
    return f'പാഠം {lesson["lesson"]}: {lesson["title"]}'


def with_context(text, lesson):
    return f'(‘{lesson["title"]}’) {text}' if CONTEXT.search(text) else text


def tagged(q, lesson, sec_no):
    out = {k: v for k, v in q.items() if k != 'id'}
    if sec_no != 3 and 'q' in out:  # section 3 quotes the text itself
        out['q'] = with_context(out['q'], lesson)
    out['note'] = (q['note'] + ' · ' if q.get('note') else '') + label(lesson)
    return out


def pick(rng, lessons, sec_no, count, used, avoid=()):
    """Pick `count` unused questions, spreading them over the lessons in turn."""
    order = [l for l in lessons if l['lesson'] not in avoid]
    rng.shuffle(order)
    picked, taken = [], set()
    while len(picked) < count:
        progress = False
        for lesson in order:
            if len(picked) == count:
                break
            sec = next(s for s in lesson['sections'] if s['no'] == sec_no)
            pool = [q for q in sec['questions']
                    if usable(sec_no, q) and (lesson['lesson'], sec_no, q['id']) not in used]
            if sec_no == 5:  # match options must stay distinct within the section
                pool = [q for q in pool if q['left'] not in taken and q['right'] not in taken]
            if not pool:
                continue
            q = rng.choice(pool)
            used.add((lesson['lesson'], sec_no, q['id']))
            if sec_no == 5:
                taken.update((q['left'], q['right']))
            picked.append((lesson, q))
            progress = True
        if not progress:
            raise SystemExit(f'not enough questions for section {sec_no}')
    return picked


def build_paper(rng, lessons, used, n):
    sections = []
    for no, title, marks, count in SECTIONS:
        if no == 10:
            mains = pick(rng, lessons, 10, count, used)
            alts = pick(rng, lessons, 10, count, used, avoid={l['lesson'] for l, _ in mains})
            questions = []
            for (lesson, q), (alt_lesson, alt) in zip(mains, alts):
                item = tagged(q, lesson, 10)
                item['note'] = 'ചോദ്യം: ' + label(lesson) + ' · അല്ലെങ്കിൽ: ' + label(alt_lesson)
                item['or'] = {'q': with_context(alt['q'], alt_lesson), 'answer': alt['answer']}
                questions.append(item)
        else:
            questions = [tagged(q, lesson, no) for lesson, q in pick(rng, lessons, no, count, used)]
        for i, q in enumerate(questions):
            q['id'] = f'{no}.{i + 1}'
        sections.append({'no': no, 'title': title, 'marks': marks, 'questions': questions})
    return {'subject': SUBJECT, 'lesson': 900 + n, 'title': f'മാതൃകാ ചോദ്യപേപ്പർ {n}',
            'meta': META, 'instructions': INSTRUCTIONS, 'sections': sections}


def register(titles):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next(s for s in data['subjects'] if s['id'] == SUBJECT)
    subj['lessons'] = [l for l in subj['lessons'] if l['no'] < 900]
    for n, title in titles:
        subj['lessons'].append({'no': 900 + n, 'tag': 'Full paper', 'title': title,
                                'file': f'data/{SUBJECT}/paper-{n}.json'})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    lessons = sorted((json.loads(p.read_text(encoding='utf-8')) for p in DATA.glob('lesson-*.json')),
                     key=lambda l: l['lesson'])
    rng = random.Random(SEED)
    used = set()
    titles = []
    for n in range(1, PAPERS + 1):
        paper = build_paper(rng, lessons, used, n)
        (DATA / f'paper-{n}.json').write_text(json.dumps(paper, ensure_ascii=False, indent=2) + '\n',
                                              encoding='utf-8')
        titles.append((n, paper['title']))
        print(f'paper-{n}.json: {sum(len(s["questions"]) for s in paper["sections"])} questions')
    register(titles)
    if SUBJECT == 'malayalam':
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import apply_ml_keywords
        apply_ml_keywords.main()


if __name__ == '__main__':
    main()
