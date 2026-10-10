"""Convert a model question paper + answer key (.docx) into lesson JSON for the app.

Usage:
  python tools/convert_lesson.py --subject malayalam --lesson 16 \
      --questions "path/to/question paper.docx" --answers "path/to/answer key.docx"

Writes data/<subject>/lesson-<n>.json and registers the lesson in data/subjects.json.
Questions and exam references gathered from old question papers live in
data/<subject>/past/lesson-<n>.json and are merged in on every run.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
APP_DIR = Path(__file__).resolve().parent.parent

SEC_RE = re.compile(r'^(\d+)\.\s+(.*?)\s*\(([^()]*[×x][^()]*)\)\s*$')
SEC_PLAIN_RE = re.compile(r'^(\d+)\.\s+(.*)$')
MARKS_LINE_RE = re.compile(r'\[([^\[\]]*[×x][^\[\]]*)\]\s*$')
Q_RE = re.compile(r'^(\d+)\.(\d+)\.?\s+(.*)$')
QID_RE = re.compile(r'^(\d+\.\d+)\.?(?:\s|$)')
# "(2025 April)" or "[2025 ഏപ്രിൽ, ചോ. 1.1]"
YEAR_RE = re.compile(r'\s*(?:\((\d{4}\s+[A-Za-z]+)\)|\[(\d{4}[^\[\]]*)\])')
LETTER_RE = re.compile(r'^\(([A-H])\)\s*(.*)$')
OPT_SPLIT = re.compile(r'\s*\(([A-H])\)\s*')
BLANK_RE = re.compile(r'_{3,}')


def docx_lines(path):
    """Return the non-empty paragraphs of a .docx; table rows become 'cell | cell'."""
    root = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))

    def text(p):
        return ''.join(t.text or '' for t in p.iter(W + 't')).strip()

    lines = []
    for el in root.find(W + 'body'):
        if el.tag == W + 'p':
            if text(el):
                lines.append(text(el))
        elif el.tag == W + 'tbl':
            for tr in el.iter(W + 'tr'):
                cells = [' '.join(text(p) for p in tc.iter(W + 'p')).strip() for tc in tr.iter(W + 'tc')]
                lines.append(' | '.join(cells))
    return lines


def parse_options(line):
    parts = OPT_SPLIT.split(line)
    return [parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)]


def parse_header(paper, header):
    """Title, author and meta from the lines above the instructions."""
    lesson_line = next((l for l in header if l.startswith('പാഠം:')), None)
    author_line = next((l for l in header if 'രചയിതാവ്:' in l), None)
    if lesson_line:
        # e.g. 'പാഠം: “എൻ്റെ ഭാഷ” — വള്ളത്തോൾ നാരായണമേനോൻ'
        title, _, author = lesson_line.split(':', 1)[1].partition(' — ')
        paper['title'] = title.strip().strip('“”"')
        if author.strip():
            paper['author'] = author.strip()
        rest = [l for l in header[1:] if l is not lesson_line]
    else:
        # "<title> — മാതൃകാ ചോദ്യപേപ്പർ" or "മാതൃകാ ചോദ്യപേപ്പർ — <title>"
        parts = [p.strip() for p in header[0].split(' — ')]
        paper['title'] = next((p for p in parts if 'ചോദ്യപേപ്പർ' not in p), parts[0])
        rest = header[1:]
    if author_line:
        # e.g. 'വിഷയം: മലയാളം (232) പാഠം 14: … രചയിതാവ്: എസ്. കെ. പൊറ്റെക്കാട്ട്'
        paper['author'] = author_line.split('രചയിതാവ്:', 1)[1].strip()
        rest = [l for l in rest if l is not author_line]
    # Join label/value pairs split over two lines ("സമയം", "3 മണിക്കൂർ").
    meta = []
    for line in rest:
        if meta and meta[-1].endswith(':'):
            meta[-1] += ' ' + line
        elif ':' not in line and not line[0].isdigit():
            meta.append(line + ':')
        else:
            meta.append(line)
    paper['meta'] = ' · '.join(m.rstrip(':') for m in meta)


MONTHS = {
    'january': 'January', 'ജനുവരി': 'January',
    'march': 'March', 'മാർച്ച്': 'March',
    'april': 'April', 'ഏപ്രിൽ': 'April',
    'october': 'October', 'ഒക്ടോബർ': 'October',
    'november': 'November', 'നവംബർ': 'November',
}
MONTH_ORDER = ['January', 'March', 'April', 'October', 'November']
PAST_PAPER = 'Past paper'  # a ★ question whose exam is not named yet


def english_year(raw):
    """'2025 ഏപ്രിൽ, ചോ. 1.1' or '2025 April' → 'April 2025'."""
    year = re.search(r'\d{4}', raw)
    month = next((m for k, m in MONTHS.items() if k in raw.lower()), None)
    if not year:
        return raw.strip()
    return f'{month} {year[0]}' if month else year[0]


def year_key(label):
    parts = label.split()
    month = MONTH_ORDER.index(parts[0]) if parts[0] in MONTH_ORDER else 0
    return (int(parts[-1]) if parts[-1].isdigit() else 0, month)


def new_question(qid, text):
    q = {'id': qid}
    year = YEAR_RE.search(text)
    if year:
        q['years'] = [english_year(year[1] or year[2])]
        text = YEAR_RE.sub('', text).strip()
    if text.startswith('★'):
        q.setdefault('years', [PAST_PAPER])
        text = text.lstrip('★ ')
    return q, text


def parse_paper(lines):
    paper = {'title': '', 'meta': '', 'instructions': [], 'sections': []}
    start = next((n for n, l in enumerate(lines) if l == 'നിർദ്ദേശങ്ങൾ' or SEC_PLAIN_RE.match(l)), len(lines))
    parse_header(paper, lines[:start] or lines[:1])
    sec = q = None
    in_instructions = False
    for line in lines[start:]:
        if line == 'നിർദ്ദേശങ്ങൾ':
            in_instructions = True
            continue
        m_sec, m_q = SEC_RE.match(line), Q_RE.match(line)
        m_plain = SEC_PLAIN_RE.match(line)
        next_no = len(paper['sections']) + 1
        if m_sec and not m_q:
            in_instructions = False
            marks = m_sec[3].replace('മാർക്ക്', '').strip()
            sec = {'no': int(m_sec[1]), 'title': m_sec[2], 'marks': marks, 'questions': []}
            paper['sections'].append(sec)
        elif m_plain and not m_q and int(m_plain[1]) == next_no:
            # Heading without marks; marks follow on the next line as "[20 × 1 = 20]".
            in_instructions = False
            sec = {'no': next_no, 'title': m_plain[2], 'marks': '', 'questions': []}
            paper['sections'].append(sec)
        elif sec and not sec['marks'] and not sec['questions'] and MARKS_LINE_RE.search(line):
            sec['marks'] = MARKS_LINE_RE.search(line)[1].strip()
        elif ' | ' in line and sec and QID_RE.match(line):
            # Two-column match table: "5.1. left | (A) right-hand item"
            left, right = [c.strip() for c in line.split(' | ', 1)]
            m_left = Q_RE.match(left)
            q, text = new_question(f'{m_left[1]}.{m_left[2]}', m_left[3])
            q.update(type='match', left=text)
            sec['questions'].append(q)
            m_right = LETTER_RE.match(right)
            if m_right:
                sec.setdefault('_pool', {})[m_right[1]] = m_right[2]
        elif m_q and sec:
            q, text = new_question(f'{m_q[1]}.{m_q[2]}', m_q[3])
            if BLANK_RE.search(text) and text.endswith(')'):
                body, opts = text[:-1].rsplit('(', 1)
                sep = '/' if '/' in opts else ','
                q.update(type='mcq', q=body.strip(), options=[o.strip() for o in opts.split(sep)])
            elif ' — ' in text:
                left, right = text.split(' — ', 1)
                q.update(type='match', left=left.strip(), right=right.strip(), _text=text)
            else:
                q.update(type='open', q=text)
            sec['questions'].append(q)
        elif line.startswith('(A)') and q:
            q['type'] = 'mcq'
            q['options'] = parse_options(line)
        elif in_instructions:
            paper['instructions'].append(line)

    # "left — right" is a match pair only when the whole section is pairs; elsewhere
    # the dash is part of the question (e.g. a quoted line — then the question).
    for sec in paper['sections']:
        pairs_only = all(q['type'] == 'match' for q in sec['questions'])
        for q in sec['questions']:
            text = q.pop('_text', None)
            if text and not pairs_only:
                del q['left'], q['right']
                q['q'] = text
                if q['type'] == 'match':
                    q['type'] = 'open'
    return paper


def split_inline_answers(lines):
    """'3.1. a 3.2. b 3.3. c' on one line → one line per answer."""
    out = []
    for line in lines:
        if QID_RE.match(line) and ' | ' not in line:
            out.extend(re.split(r'\s+(?=\d+\.\d+\.\s)', line))
        else:
            out.append(line)
    return out


def parse_answers(lines):
    answers, notes, sec_notes, cur = {}, {}, {}, None
    sec_no = None
    for line in split_inline_answers(lines[1:]):
        if line.startswith('കുറിപ്പ്:') and sec_no:
            # A remark for the whole section, e.g. on spelling conventions.
            sec_notes[sec_no] = line.split(':', 1)[1].strip()
            cur = None
            continue
        if line.startswith('അധ്യാപകർക്കുള്ള കുറിപ്പ്'):
            cur = None  # general remark to teachers; not shown in the app
            continue
        if line.startswith('ശ്രദ്ധിക്കുക:'):
            # A remark about a specific question, e.g. "ശ്രദ്ധിക്കുക: 1.2-ലെ ഓപ്ഷനുകൾ …"
            ref = re.search(r'(\d+\.\d+)-', line)
            if ref:
                notes[ref[1]] = line.split(':', 1)[1].strip()
            continue
        if ' | ' in line:
            qid, ans = [c.strip() for c in line.split(' | ', 1)]
            m_id = QID_RE.match(qid)
            if m_id:
                answers[m_id[1]] = {'inline': ans, 'more': []}
            continue
        m_q = Q_RE.match(line)
        if m_q:
            cur = answers[f'{m_q[1]}.{m_q[2]}'] = {'inline': m_q[3], 'more': []}
        elif re.match(r'^\d+\.\s', line):
            cur = None  # section heading
            sec_no = int(line.split('.', 1)[0])
        elif cur:
            cur['more'].append(line)
        # Anything else above the first section (e.g. "answers are only models") is a
        # general remark about the key and is left out.
    return answers, notes, sec_notes


TRUE_FALSE = ['ശരി', 'തെറ്റ്']


def as_true_false(q, text):
    """Turn a ശരിയോ തെറ്റോ question into a two-button choice; any reason becomes a note."""
    verdict, _, reason = text.partition('—')
    verdict = verdict.strip().rstrip('.')
    if verdict not in TRUE_FALSE:
        return False
    q.update(type='mcq', options=TRUE_FALSE, answer=chr(65 + TRUE_FALSE.index(verdict)))
    if reason.strip():
        q['note'] = reason.strip()
    return True


def merge(paper, answers, notes, sec_notes):
    problems = []
    for sec in paper['sections']:
        if sec['no'] in sec_notes:
            sec['note'] = sec_notes[sec['no']]
        pool = sec.pop('_pool', {})
        true_false = 'ശരിയോ തെറ്റോ' in sec['title']
        for q in sec['questions']:
            if true_false and q['id'] in answers and as_true_false(q, answers[q['id']]['inline']):
                continue
            if q['id'] in notes:
                q['note'] = notes[q['id']]
            a = answers.get(q['id'])
            if not a:
                problems.append(f"{q['id']}: no answer found")
                continue
            # Long answers restate the question on the id line; the answer follows.
            text = '\n'.join(a['more']) if a['more'] else a['inline']
            if q['type'] == 'match' and 'right' not in q:
                # Table layout: the key gives the letter of the right-hand item.
                m = LETTER_RE.match(text)
                right = pool.get(m[1]) if m else None
                if right is None:
                    problems.append(f"{q['id']}: match answer '{text}' not in the right-hand column")
                    continue
                q['right'] = right
                text = f"{q['left']} — {right}"
            if q['type'] == 'mcq':
                letter = re.match(r'^\(([A-H])\)', text)
                if letter:
                    q['answer'] = letter[1]
                else:
                    clean = text.rstrip('.').strip()
                    idx = next((n for n, o in enumerate(q['options']) if o == clean), None)
                    if idx is None:
                        problems.append(f"{q['id']}: answer '{clean}' not among options")
                    else:
                        q['answer'] = chr(65 + idx)
            else:
                q['answer'] = text
        types = {q['type'] for q in sec['questions']}
        sec['type'] = types.pop() if len(types) == 1 else 'mixed'
    return problems


def merge_past(paper, past):
    """Add questions and exam references collected from old question papers.

    past = {"refs": {"<id>": ["April 2022", ...]},
            "add": [{"section": 9, "type": "open", "q": ..., "answer": ..., "years": [...]}, ...]}
    """
    problems = []
    by_id = {q['id']: q for s in paper['sections'] for q in s['questions']}
    for qid, years in past.get('refs', {}).items():
        q = by_id.get(qid)
        if not q:
            problems.append(f'past refs: no question {qid}')
            continue
        q['years'] = [y for y in q.get('years', []) if y != PAST_PAPER] + years
    sections = {s['no']: s for s in paper['sections']}
    for item in past.get('add', []):
        sec = sections.get(item['section'])
        if not sec:
            problems.append(f"past add: no section {item['section']}")
            continue
        q = {'id': f"{sec['no']}.{len(sec['questions']) + 1}",
             **{k: v for k, v in item.items() if k != 'section'}}
        if q['type'] == 'mcq' and q.get('answer') not in [chr(65 + i) for i in range(len(q['options']))]:
            problems.append(f"past add: bad answer for {q['q'][:40]}")
        sec['questions'].append(q)
        types = {x['type'] for x in sec['questions']}
        sec['type'] = types.pop() if len(types) == 1 else 'mixed'
    for q in (q for s in paper['sections'] for q in s['questions']):
        if 'years' in q:
            q['years'] = sorted(dict.fromkeys(q['years']), key=year_key, reverse=True)
    return problems


def register(subject, lesson_no, title, rel_path):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    subj = next((s for s in data['subjects'] if s['id'] == subject), None)
    if subj is None:
        sys.exit(f"Unknown subject '{subject}'. Add it to data/subjects.json first.")
    subj['lessons'] = [l for l in subj['lessons'] if l['no'] != lesson_no]
    subj['lessons'].append({'no': lesson_no, 'title': title, 'file': rel_path})
    subj['lessons'].sort(key=lambda l: l['no'])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', required=True)
    ap.add_argument('--lesson', required=True, type=int)
    ap.add_argument('--questions', required=True)
    ap.add_argument('--answers', required=True)
    args = ap.parse_args()

    paper = parse_paper(docx_lines(args.questions))
    answers, notes, sec_notes = parse_answers(docx_lines(args.answers))
    problems = merge(paper, answers, notes, sec_notes)
    past_file = APP_DIR / 'data' / args.subject / 'past' / f'lesson-{args.lesson}.json'
    if past_file.exists():
        problems += merge_past(paper, json.loads(past_file.read_text(encoding='utf-8')))
    paper = {'subject': args.subject, 'lesson': args.lesson, **paper}

    rel = f'data/{args.subject}/lesson-{args.lesson}.json'
    out = APP_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    register(args.subject, args.lesson, paper['title'], rel)

    sys.stdout.reconfigure(encoding='utf-8')
    counts = ', '.join(f"§{s['no']} {s['type']}×{len(s['questions'])}" for s in paper['sections'])
    print(f'Wrote {rel}: {counts}')
    for p in problems:
        print('WARNING', p)


if __name__ == '__main__':
    main()
