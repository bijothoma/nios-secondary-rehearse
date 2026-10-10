"""Build a lesson JSON in the April 2026 exam layout from a compact source file.

Usage:
  python tools/build_lesson.py data/malayalam/src/lesson-10.json

Used for lessons that have no Word question paper. The source lists questions per
section in short form (see data/malayalam/src/*.json); this script adds ids, section
titles and marks, and registers the lesson in data/subjects.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_lesson import APP_DIR, register  # noqa: E402

TRUE_FALSE = ['ശരി', 'തെറ്റ്']

# key in source, title, marks, kind
SECTIONS = [
    ('mcq', 'ശരിയായ ഉത്തരം തെരഞ്ഞെടുത്ത് എഴുതുക.', '20 × 1 = 20', 'choice'),
    ('oneword', 'ഒറ്റവാക്കിൽ ഉത്തരമെഴുതുക.', '5 × 1 = 5', 'open'),
    ('fill', 'വിട്ടുപോയ ഭാഗം ബ്രാക്കറ്റിൽനിന്ന് ശരിയായത് തെരഞ്ഞെടുത്ത് പൂരിപ്പിക്കുക.', '5 × 1 = 5', 'choice'),
    ('truefalse', 'താഴെ തന്നിരിക്കുന്നവ ശരിയോ തെറ്റോ എന്ന് രേഖപ്പെടുത്തുക.', '5 × 1 = 5', 'tf'),
    ('match', 'ചേരുംപടി ചേർക്കുക.', '5 × 1 = 5', 'match'),
    ('synonym', 'പകരം പദം എഴുതുക.', '5 × 1 = 5', 'open'),
    ('join', 'ചേർത്തെഴുതുക.', '5 × 1 = 5', 'open'),
    ('short', 'ഏതെങ്കിലും 10 ചോദ്യങ്ങൾക്ക് 20–25 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '10 × 2 = 20', 'open'),
    ('medium', 'ഏതെങ്കിലും 5 ചോദ്യങ്ങൾക്ക് 40–45 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '5 × 3 = 15', 'open'),
    ('long', 'താഴെ പറയുന്നവയിൽ 3 ചോദ്യങ്ങൾക്ക് 100–150 വാക്കുകളിൽ ഉത്തരമെഴുതുക.', '3 × 5 = 15', 'open'),
]

INSTRUCTIONS = [
    'എല്ലാ ചോദ്യങ്ങൾക്കും നിർദ്ദേശാനുസരണം ഉത്തരം എഴുതുക.',
    '8-ാം ചോദ്യത്തിൽ ഏതെങ്കിലും 10 ചോദ്യങ്ങൾക്കും 9-ാം ചോദ്യത്തിൽ ഏതെങ്കിലും 5 ചോദ്യങ്ങൾക്കും ഉത്തരം എഴുതുക.',
    'മുൻവർഷ ചോദ്യപേപ്പറുകളിൽ വന്ന ചോദ്യങ്ങൾക്കൊപ്പം പരീക്ഷയുടെ മാസവും വർഷവും നൽകിയിട്ടുണ്ട്.',
]


def extra(item, start):
    """Optional trailing [years, note] entries."""
    out = {}
    rest = item[start:]
    if rest and rest[0]:
        out['years'] = rest[0]
    if len(rest) > 1 and rest[1]:
        out['note'] = rest[1]
    return out


def build_question(kind, item):
    if kind == 'choice':
        q, options, answer = item[:3]
        if answer not in 'ABCDEFGH'[:len(options)]:
            raise ValueError(f'bad answer {answer!r} for {q[:40]}')
        return {'type': 'mcq', 'q': q, 'options': options, 'answer': answer, **extra(item, 3)}
    if kind == 'tf':
        q, is_true = item[:2]
        return {'type': 'mcq', 'q': q, 'options': TRUE_FALSE,
                'answer': 'A' if is_true else 'B', **extra(item, 2)}
    if kind == 'match':
        left, right = item[:2]
        return {'type': 'match', 'left': left, 'right': right,
                'answer': f'{left} — {right}', **extra(item, 2)}
    q, answer = item[:2]
    return {'type': 'open', 'q': q, 'answer': answer, **extra(item, 2)}


def main():
    src_path = Path(sys.argv[1])
    src = json.loads(src_path.read_text(encoding='utf-8'))
    sections = []
    for no, (key, title, marks, kind) in enumerate(SECTIONS, start=1):
        questions = []
        for n, item in enumerate(src[key], start=1):
            questions.append({'id': f'{no}.{n}', **build_question(kind, item)})
        types = {q['type'] for q in questions}
        sections.append({'no': no, 'title': title, 'marks': marks, 'questions': questions,
                         'type': types.pop() if len(types) == 1 else 'mixed'})

    subject = src.get('subject', 'malayalam')
    paper = {
        'subject': subject,
        'lesson': src['lesson'],
        'title': src['title'],
        'author': src['author'],
        'meta': 'സമയം: 3 മണിക്കൂർ · ആകെ മാർക്ക്: 100 · 2026 ഏപ്രിൽ ചോദ്യപേപ്പറിന്റെ മാതൃകയിൽ',
        'instructions': INSTRUCTIONS,
        'sections': sections,
    }
    rel = f"data/{subject}/lesson-{src['lesson']}.json"
    (APP_DIR / rel).write_text(json.dumps(paper, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    register(subject, src['lesson'], src['title'], rel)

    sys.stdout.reconfigure(encoding='utf-8')
    counts = ', '.join(f"§{s['no']}×{len(s['questions'])}" for s in sections)
    tagged = sum(1 for s in sections for q in s['questions'] if q.get('years'))
    print(f'Wrote {rel}: {counts}; {tagged} with exam tags')


if __name__ == '__main__':
    main()
