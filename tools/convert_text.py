"""Convert a lesson text .docx (Malayalam with English translation) into JSON for the app.

Usage:
  python tools/convert_text.py --subject malayalam --lesson 16 --docx "path/to/lesson.docx"
  python tools/convert_text.py --subject malayalam --lesson 2 --txt data/malayalam/src/text-2.txt

A .txt source has blocks separated by blank lines. "# ml | en" is the title,
"@ ml | en" the author and "## ml | en" a heading. In other blocks, lines starting
with "> " are English and the rest Malayalam (line breaks are kept for poems).

The translation may be given as whole English paragraphs, or inline in (round) or
[square] brackets after each sentence. Each paragraph is stored as a list of parts,
["ml", text] or ["en", text], so the app can show the lesson with or without English.
Writes data/<subject>/text/lesson-<n>.json and links it from data/subjects.json.
With --local it writes local/<subject>/text/lesson-<n>.json and lists it in
local/texts.json instead; local/ is not committed, so the text stays on this computer.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_lesson import APP_DIR  # noqa: E402

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MALAYALAM = re.compile(r'[ഀ-ൿ]')
LATIN = re.compile(r'[A-Za-z]')
GROUP = re.compile(r'\s*(\([^()]*\)|\[[^\[\]]*\])')
PAGE = re.compile(r'^(പേജ്|Page)\s*\d+$')


def is_english(text):
    return len(LATIN.findall(text)) > len(MALAYALAM.findall(text))


def paragraphs(path):
    """(text, style, bold) per non-empty paragraph; line breaks kept as \\n."""
    root = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
    for p in root.find(W + 'body').iter(W + 'p'):
        text = ''
        for node in p.iter():
            if node.tag == W + 't':
                text += node.text or ''
            elif node.tag in (W + 'br', W + 'cr'):
                text += '\n'
            elif node.tag == W + 'tab':
                text += ' '
        text = '\n'.join(line.strip() for line in text.split('\n')).strip()
        if not text:
            continue
        style = p.find(f'{W}pPr/{W}pStyle')
        style = style.get(W + 'val') if style is not None else ''
        bold = any(r.find(f'{W}rPr/{W}b') is not None for r in p.iter(W + 'r'))
        yield text, style, bold


def split_parts(text):
    """Split a paragraph into Malayalam and English parts."""
    if not MALAYALAM.search(text):
        return [['en' if LATIN.search(text) else 'ml', text]]
    parts, pos = [], 0
    for m in GROUP.finditer(text):
        inner = m.group(1)[1:-1]
        if not is_english(inner):
            continue
        if text[pos:m.start()].strip():
            parts.append(['ml', text[pos:m.start()].strip()])
        parts.append(['en', inner.strip()])
        pos = m.end()
    if text[pos:].strip():
        parts.append(['ml', text[pos:].strip()])
    return parts


def split_heading(text):
    """'എൻ്റെ ഭാഷ — My Mother Tongue' → ml + en parts; drops a 'Lesson 14—' prefix."""
    text = re.sub(r'^Lesson\s*\d+\s*[—–-]\s*', '', text)
    left, sep, right = text.partition(' — ')
    if sep and is_english(right) and not is_english(left):
        return [['ml', left.strip()], ['en', right.strip()]]
    return split_parts(text)


def convert(path):
    blocks = []
    for text, style, bold in paragraphs(path):
        if PAGE.match(text):
            blocks.append({'type': 'page', 'parts': [['ml', text]]})
        elif not blocks:
            blocks.append({'type': 'title', 'parts': split_heading(text)})
        elif len(blocks) == 1:
            blocks.append({'type': 'author', 'parts': split_heading(text)})
        elif style.startswith('Heading') or (bold and len(text) < 60):
            blocks.append({'type': 'heading', 'parts': split_heading(text)})
        else:
            blocks.append({'type': 'para', 'parts': split_parts(text)})
    return blocks


def convert_txt(path):
    blocks = []
    kinds = {'#': 'title', '@': 'author', '##': 'heading'}
    for chunk in re.split(r'\n\s*\n', Path(path).read_text(encoding='utf-8').strip()):
        lines = [l.rstrip() for l in chunk.strip().split('\n')]
        mark, _, rest = lines[0].partition(' ')
        if mark in kinds and len(lines) == 1:
            ml, _, en = rest.partition(' | ')
            parts = [['ml', ml.strip()]] + ([['en', en.strip()]] if en.strip() else [])
            blocks.append({'type': kinds[mark], 'parts': parts})
            continue
        parts = []
        for line in lines:
            kind, text = ('en', line[2:]) if line.startswith('> ') else ('ml', line)
            if parts and parts[-1][0] == kind:
                parts[-1][1] += '\n' + text
            else:
                parts.append([kind, text])
        blocks.append({'type': 'para', 'parts': parts})
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', required=True)
    ap.add_argument('--lesson', required=True, type=int)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--docx')
    src.add_argument('--txt')
    ap.add_argument('--local', action='store_true', help='keep the text out of git (copyrighted lessons)')
    args = ap.parse_args()

    blocks = convert(args.docx) if args.docx else convert_txt(args.txt)
    rel = f'{"local" if args.local else "data"}/{args.subject}/text/lesson-{args.lesson}.json'
    out = APP_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'subject': args.subject, 'lesson': args.lesson, 'blocks': blocks},
                              ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    if args.local:
        path = APP_DIR / 'local' / 'texts.json'
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        data.setdefault(args.subject, {})[str(args.lesson)] = rel
    else:
        path = APP_DIR / 'data' / 'subjects.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        subj = next(s for s in data['subjects'] if s['id'] == args.subject)
        lesson = next((l for l in subj['lessons'] if l['no'] == args.lesson), None)
        if lesson is None:
            sys.exit(f'Lesson {args.lesson} is not in data/subjects.json yet; add its question paper first.')
        lesson['text'] = rel
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    sys.stdout.reconfigure(encoding='utf-8')
    count = {}
    for b in blocks:
        count[b['type']] = count.get(b['type'], 0) + 1
    en = sum(1 for b in blocks for p in b['parts'] if p[0] == 'en')
    print(f'Wrote {rel}: {count}, {en} English parts')


if __name__ == '__main__':
    main()
