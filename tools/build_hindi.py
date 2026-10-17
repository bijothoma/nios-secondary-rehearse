"""Build Hindi (201) lesson practice sets and full model papers in the April 2026 layout.

Usage:
  python tools/build_hindi.py

A lesson source (data/hindi/src/lesson-<n>.json) has lesson, title, author, genre ('poem',
'prose' or 'writing') and lists of questions in short form; every item may end with
[years, note]:
  mcq       [q, [options], answer letter]         1 mark
  mcq2      [q with two blanks, [options], letter] 2 marks (two 1-mark blanks)
  fill      [q, answer]                           1 mark (fill in the blank / one word)
  fill2     [q with two blanks, answer]           2 marks
  truefalse [statement, true|false]               1 mark (सही / गलत)
  match     [left, right]                         1 mark (lesson and character, word and meaning…)
  speaker   [quoted words, who says them]         1 mark ("किसका कथन है?")
  grammar   [q, answer] or [q, [options], letter]  1 mark
  short     [q, answer]                           2 marks, 20–25 words
  beauty    [stanza, answer]                      4 marks, काव्य-सौंदर्य (poems)
  explain   [extract, answer]                     सप्रसंग व्याख्या: 3 marks (poems), 5 (prose)
  passage   [extract + questions, answer]         5 marks, गद्यांश (prose)
  writing   [task, model answer]                  सार (5), पत्र (5) or निबंध (7)

data/hindi/src/papers.json holds the parts of a paper that do not come from a lesson, one entry per
full paper: unseen poem (Q6) and passage (Q20) with four MCQs each, grammar (Q21–27) and the सार
passage (Q35). Lesson questions are dealt to the three papers without repeats.

Quotes and explanations for 1-mark questions live in data/hindi/quotes.json (and, for lessons still
under copyright, local/hindi/quotes.json), keyed "<lesson>|<question text>" as for Malayalam.
"""
import json
import re
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
SUBJECT = 'hindi'
DATA = APP_DIR / 'data' / SUBJECT
FULL_PAPERS = 3
TRUE_FALSE = ['सही', 'गलत']
POEMS = [2, 4, 7, 8, 14]

# key, title, marks per question (None: by genre)
LESSON_SECTIONS = [
    ('mcq', 'सही विकल्प चुनकर लिखिए।', 1),
    ('mcq2', 'सही विकल्प चुनकर रिक्त स्थानों की पूर्ति कीजिए।', 2),
    ('fill', 'रिक्त स्थान एक शब्द या वाक्यांश से भरिए।', 1),
    ('fill2', 'रिक्त स्थान भरिए।', 2),
    ('truefalse', 'नीचे दिए गए कथन सही हैं या गलत, बताइए।', 1),
    ('match', 'सही युग्म मिलाइए।', 1),
    ('speaker', 'निम्नलिखित कथन किसके हैं? पहचान कीजिए।', 1),
    ('grammar', 'भाषा-प्रयोग: निर्देशानुसार उत्तर दीजिए।', 1),
    ('short', 'निम्नलिखित प्रश्नों के उत्तर 20 से 25 शब्दों में लिखिए।', 2),
    ('beauty', 'निम्नलिखित काव्यांश के कवि और कविता का नामोल्लेख करते हुए काव्य-सौंदर्य स्पष्ट कीजिए।', 4),
    ('explain', 'निम्नलिखित अवतरण की सप्रसंग व्याख्या कीजिए।', None),
    ('passage', 'निम्नलिखित गद्यांश को ध्यानपूर्वक पढ़िए और पूछे गए प्रश्नों के उत्तर लिखिए।', 5),
    ('writing', 'लेखन-कौशल', None),
]
INSTRUCTIONS_LESSON = [
    'इस पाठ के प्रश्न अप्रैल 2026 के प्रश्न-पत्र के प्रश्न-प्रकारों में दिए गए हैं।',
    'एक अंक के प्रश्नों के उत्तर के साथ पाठ का वह अंश और उसकी व्याख्या दी गई है, जिसमें उत्तर मिलता है।',
    'पिछले प्रश्न-पत्रों में आए प्रश्नों के साथ परीक्षा का महीना और वर्ष दिया गया है।',
]
META = 'समय: 3 घंटे · पूर्णांक: 100 · अप्रैल 2026 के प्रश्न-पत्र के अनुसार'
INSTRUCTIONS_FULL = [
    'प्रश्न-पत्र में 37 प्रश्न हैं और सभी प्रश्न अनिवार्य हैं। जिन प्रश्नों में "अथवा" है, उनमें से एक का उत्तर दीजिए।',
    'खंड "अ" (वस्तुनिष्ठ): प्रश्न 1–5 पठित कविता, 6 अपठित काव्यांश, 7–19 पठित गद्य, 20 अपठित गद्यांश और 21–27 व्याकरण पर।',
    'खंड "ब" (वर्णनात्मक): प्रश्न 28–30 पठित कविता, 31–34 पठित गद्य और 35–37 लेखन-कौशल (सार, पत्र, निबंध) पर।',
    'हर प्रश्न के उत्तर के साथ उसका पाठ दिया गया है; पिछले प्रश्न-पत्रों में आए प्रश्नों के साथ परीक्षा का वर्ष भी।',
]


def extra(item, start):
    out = {}
    rest = item[start:]
    if rest and rest[0]:
        out['years'] = rest[0]
    if len(rest) > 1 and rest[1]:
        out['note'] = rest[1]
    return out


def question(key, item):
    if key in ('truefalse',):
        q, is_true = item[:2]
        return {'type': 'mcq', 'q': q, 'options': TRUE_FALSE, 'answer': 'A' if is_true else 'B', **extra(item, 2)}
    if key == 'match':
        left, right = item[:2]
        return {'type': 'match', 'left': left, 'right': right, 'answer': f'{left} — {right}', **extra(item, 2)}
    if key == 'speaker':
        words, who = item[:2]
        return {'type': 'open', 'q': f'“{words}”', 'answer': who, **extra(item, 2)}
    if len(item) >= 3 and isinstance(item[1], list):
        q, options, answer = item[:3]
        if answer not in 'ABCD'[:len(options)] or len(set(options)) != len(options):
            raise ValueError(f'bad options/answer for {q[:40]}')
        return {'type': 'mcq', 'q': q, 'options': options, 'answer': answer, **extra(item, 3)}
    q, answer = item[:2]
    return {'type': 'open', 'q': q, 'answer': answer, **extra(item, 2)}


def item_marks(src, key, item=None):
    marks = next(m for k, _, m in LESSON_SECTIONS if k == key)
    if marks is not None:
        return marks
    if key == 'explain':
        return 3 if src['genre'] == 'poem' else 5
    text = item[0] if item else ''
    return 7 if 'निबंध' in text else 5


def section(no, title, marks, questions, passage=None):
    for i, q in enumerate(questions):
        q['id'] = f'{no}.{i + 1}'
    sec = {'no': no, 'title': title, 'marks': marks, 'questions': questions}
    if passage:
        sec['passage'] = passage
        sec['fixed'] = True
    return sec


def build_lesson(src):
    sections = []
    for key, title, _ in LESSON_SECTIONS:
        items = src.get(key) or []
        if not items:
            continue
        no = len(sections) + 1
        marks = [item_marks(src, key, it) for it in items]
        label = f'{len(items)} × {marks[0]} = {sum(marks)}' if len(set(marks)) == 1 else f'{sum(marks)}'
        sections.append(section(no, title, label, [question(key, it) for it in items]))
    paper = {'subject': SUBJECT, 'lesson': src['lesson'], 'title': src['title'], 'author': src.get('author', ''),
             'meta': 'पाठ-अभ्यास · अप्रैल 2026 के प्रश्न-पत्र के प्रश्न-प्रकार', 'instructions': INSTRUCTIONS_LESSON,
             'sections': sections}
    write(f'lesson-{src["lesson"]}.json', paper)
    return sum(len(s['questions']) for s in sections)


class Dealer:
    """Hands out lesson questions of one kind, round-robin over lessons, never twice."""

    def __init__(self, sources):
        self.sources = sources
        self.used = set()
        self.turn = {}

    def take(self, key, lessons, n, paper, distinct=True, test=None):
        lessons = [l for l in lessons if any(s['lesson'] == l for s in self.sources)]
        start = self.turn.get(key, paper * 2) % max(len(lessons), 1)
        picked = []
        for step in range(len(lessons) * 40):
            if len(picked) == n:
                break
            lesson = lessons[(start + step) % len(lessons)]
            if distinct and any(l == lesson for l, _, _ in picked) and step < len(lessons) * 2:
                continue
            src = next(s for s in self.sources if s['lesson'] == lesson)
            pool = [(i, it) for i, it in enumerate(src.get(key) or [])
                    if (lesson, key, i) not in self.used and (test is None or test(it))]
            if not pool:
                continue
            i, it = pool[(paper * 3 + step) % len(pool)]
            self.used.add((lesson, key, i))
            picked.append((lesson, src, it))
        self.turn[key] = start + n
        if len(picked) < n:
            raise SystemExit(f'Not enough {key} questions for paper {paper + 1}')
        return picked


def tagged(key, lesson, src, it):
    q = question(key, it)
    tag = f'पाठ {lesson}: {src["title"]}'
    q['note'] = (q['note'] + ' · ' if q.get('note') else '') + tag
    return q


def build_full_papers(sources, extras):
    poems = [s['lesson'] for s in sources if s['genre'] == 'poem']
    prose = [s['lesson'] for s in sources if s['genre'] != 'poem']
    stories = [s['lesson'] for s in sources if s['genre'] == 'prose']
    deal = Dealer(sources)
    for p in range(FULL_PAPERS):
        ex = extras[p]
        secs = []

        def add(title, marks, picks, key):
            secs.append(section(len(secs) + 1, title, marks, [tagged(key, l, s, it) for l, s, it in picks]))

        def add_plain(title, marks, qs, passage=None):
            secs.append(section(len(secs) + 1, title, marks, [question(k, it) for k, it in qs], passage))

        # खंड अ — पठित कविता
        add('रिक्त स्थान भरिए।', '1', deal.take('fill', poems, 1, p), 'fill')
        add('सही विकल्प चुनकर लिखिए।', '1', deal.take('mcq', poems, 1, p), 'mcq')
        add('रिक्त स्थान एक शब्द या वाक्यांश से भरिए।', '3 × 1 = 3', deal.take('fill', poems, 3, p), 'fill')
        add('रिक्त स्थान भरिए।', '2 × 2 = 4', deal.take('fill2', poems, 2, p), 'fill2')
        add('रिक्त स्थान एक शब्द या वाक्यांश से भरिए।', '2 × 2 = 4', deal.take('fill2', poems, 2, p), 'fill2')
        add_plain('निम्नलिखित अपठित काव्यांश को ध्यानपूर्वक पढ़िए और सही विकल्प चुनिए।', '4 × 1 = 4',
                  [('mcq', it) for it in ex['poem']['items']], ex['poem']['text'])
        # पठित गद्य
        add('सही विकल्प चुनकर रिक्त स्थान भरिए।', '1', deal.take('mcq', prose, 1, p), 'mcq')
        add('सही विकल्प चुनकर रिक्त स्थान भरिए।', '1', deal.take('mcq', prose, 1, p), 'mcq')
        for _ in range(3):
            add('सही विकल्प चुनकर लिखिए।', '1', deal.take('mcq', prose, 1, p), 'mcq')
        add('रिक्त स्थान एक शब्द या वाक्यांश से भरिए।', '1', deal.take('fill', prose, 1, p), 'fill')
        add('रिक्त स्थान एक शब्द या वाक्यांश से भरिए।', '1', deal.take('fill', prose, 1, p), 'fill')
        add('रिक्त स्थानों की पूर्ति कीजिए।', '2 × 1 = 2', deal.take('fill', prose, 2, p), 'fill')
        add('निम्नलिखित संवाद किस पात्र के हैं? पहचान कीजिए।', '2 × 1 = 2', deal.take('speaker', stories, 2, p), 'speaker')
        add('नीचे दिए गए कथन सही हैं या गलत, बताइए।', '2 × 1 = 2', deal.take('truefalse', prose, 2, p), 'truefalse')
        add('सही विकल्प चुनकर रिक्त स्थानों की पूर्ति कीजिए।', '1 + 1 = 2', deal.take('mcq2', prose, 1, p), 'mcq2')
        add('नीचे दिए गए पाठों और पात्रों के सही युग्म चुनिए।', '2 × 1 = 2', deal.take('match', prose, 2, p), 'match')
        add('रिक्त स्थानों की पूर्ति कीजिए।', '2 × 1 = 2', deal.take('fill', prose, 2, p), 'fill')
        add_plain('निम्नलिखित अपठित गद्यांश को ध्यानपूर्वक पढ़िए और सही विकल्प चुनिए।', '4 × 1 = 4',
                  [('mcq', it) for it in ex['prose']['items']], ex['prose']['text'])
        # व्याकरण
        for g in ex['grammar']:
            add_plain(g['title'], g['marks'], [('grammar', it) for it in g['items']])
        # खंड ब
        add('निम्नलिखित काव्यांश के कवि और कविता का नामोल्लेख करते हुए काव्य-सौंदर्य स्पष्ट कीजिए। (कोई एक)', '4',
            deal.take('beauty', poems, 2, p), 'beauty')
        add('निम्नलिखित अवतरण की सप्रसंग व्याख्या कीजिए। (कोई एक)', '3', deal.take('explain', poems, 2, p), 'explain')
        add('निम्नलिखित प्रश्नों में से किन्हीं तीन के उत्तर 20 से 25 शब्दों में लिखिए।', '3 × 2 = 6',
            deal.take('short', poems, 4, p), 'short')
        add('निम्नलिखित प्रश्नों में से किन्हीं तीन के उत्तर 20 से 25 शब्दों में लिखिए।', '3 × 2 = 6',
            deal.take('short', stories, 4, p), 'short')
        add('निम्नलिखित प्रश्नों में से किन्हीं दो के उत्तर 20 से 25 शब्दों में लिखिए।', '2 × 2 = 4',
            deal.take('short', prose, 3, p), 'short')
        add('निम्नलिखित गद्यांश को ध्यानपूर्वक पढ़िए और पूछे गए प्रश्नों के उत्तर लिखिए। (कोई एक)', '5',
            deal.take('passage', stories, 2, p), 'passage')
        add('निम्नलिखित अवतरण की सप्रसंग व्याख्या कीजिए। (कोई एक)', '5', deal.take('explain', stories, 2, p), 'explain')
        add_plain('निम्नलिखित गद्यांश का सार एक-तिहाई शब्दों में लिखिए।', '5', [('writing', ex['saar'])])
        add('पत्र लिखिए। (कोई एक)', '5', deal.take('writing', [21], 2, p, distinct=False), 'writing')
        add('निम्नलिखित में से किसी एक विषय पर लगभग 300 शब्दों में निबंध लिखिए।', '7',
            deal.take('writing', [22], 4, p, distinct=False), 'writing')
        total = sum(int(eval(s['marks'].split('=')[-1])) for s in secs)
        if len(secs) != 37 or total != 100:
            raise SystemExit(f'paper {p + 1}: {len(secs)} questions, {total} marks')
        write(f'paper-{p + 1}.json', {'subject': SUBJECT, 'lesson': 900 + p + 1, 'title': f'मॉडल प्रश्न-पत्र {p + 1}',
                                      'meta': META, 'instructions': INSTRUCTIONS_FULL, 'sections': secs})


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
    old = {l['no']: l for l in subj.get('lessons', [])}
    subj.update(name='Hindi', label='हिंदी', level='secondary', quotes=f'data/{SUBJECT}/quotes.json',
                quoteHeads=['पाठ का अंश', 'व्याख्या'])
    lessons = []
    for s in sources:
        n = s['lesson']
        entry = {'no': n, 'title': s['title'], 'file': f'data/{SUBJECT}/lesson-{n}.json'}
        for k in ('text', 'summary'):
            if k in old.get(n, {}):
                entry[k] = old[n][k]
        lessons.append(entry)
    for p in range(papers):
        lessons.append({'no': 900 + p + 1, 'tag': 'Full paper', 'title': f'मॉडल प्रश्न-पत्र {p + 1}',
                        'file': f'data/{SUBJECT}/paper-{p + 1}.json'})
    subj['lessons'] = lessons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def check_quotes(sources):
    """Warn about quote keys that no 1-mark question uses (e.g. after a question was reworded)."""
    keys = set()
    for s in sources:
        for key in ('mcq', 'mcq2', 'fill', 'fill2', 'truefalse', 'match', 'speaker', 'grammar'):
            for it in s.get(key) or []:
                q = question(key, it)
                keys.add(f'{s["lesson"]}|{q["left"] if q["type"] == "match" else q["q"]}')
    for path in (DATA / 'quotes.json', APP_DIR / 'local' / SUBJECT / 'quotes.json'):
        if path.exists():
            for k in json.loads(path.read_text(encoding='utf-8')):
                if k not in keys:
                    print(f'WARNING: {path.name}: no question for quote key {k}')


def write_quotes(sources):
    """Quotes of public lessons go to data/hindi/quotes.json, those of lessons under copyright
    (source has "local": true) to local/hindi/quotes.json, which is not committed."""
    out = {False: {}, True: {}}
    for s in sources:
        for text, entry in (s.get('quotes') or {}).items():
            out[bool(s.get('local'))][f'{s["lesson"]}|{text}'] = entry
    for local, path in ((False, DATA / 'quotes.json'), (True, APP_DIR / 'local' / SUBJECT / 'quotes.json')):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out[local], ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sources = sorted((json.loads(p.read_text(encoding='utf-8')) for p in (DATA / 'src').glob('lesson-*.json')),
                     key=lambda s: s['lesson'])
    for s in sources:
        print(f'पाठ {s["lesson"]}: {build_lesson(s)} questions')
    papers = 0
    extras_path = DATA / 'src' / 'papers.json'
    if len(sources) == 14 and extras_path.exists():
        build_full_papers(sources, json.loads(extras_path.read_text(encoding='utf-8')))
        papers = FULL_PAPERS
        print(f'{papers} full papers')
    write_quotes(sources)
    register(sources, papers)
    check_quotes(sources)


if __name__ == '__main__':
    main()
