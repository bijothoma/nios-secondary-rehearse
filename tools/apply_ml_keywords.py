"""Add the 'keywords' block to the 3- and 5-mark answers of the Secondary Malayalam papers.

Usage:
  python tools/apply_ml_keywords.py

data/malayalam/keywords/lesson-<n>.json holds, for sections 9 (3 marks) and 10 (5 marks) of lesson n, one list of
keywords per question, in question order. This script stamps them into data/malayalam/lesson-<n>.json and, matched
by answer text, into the model papers (data/malayalam/paper-*.json, including OR alternatives). It is safe to run
again; build_lesson.py and build_ml_papers.py call it after writing their files.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data' / 'malayalam'
SECTIONS = (9, 10)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def stamp_lesson(path, kw):
    paper = load(path)
    for sec in paper['sections']:
        if str(sec['no']) in kw and sec['no'] in SECTIONS:
            for q, words in zip(sec['questions'], kw[str(sec['no'])]):
                q['keywords'] = words
    save(path, paper)
    return paper


def main():
    by_answer = {}
    for kpath in sorted((DATA / 'keywords').glob('lesson-*.json')):
        n = re.findall(r'(\d+)', kpath.name)[-1]
        lpath = DATA / f'lesson-{n}.json'
        if not lpath.exists():
            continue
        lesson = stamp_lesson(lpath, load(kpath))
        for sec in lesson['sections']:
            if sec['no'] in SECTIONS:
                for q in sec['questions']:
                    if q.get('keywords'):
                        by_answer[q['answer']] = q['keywords']
    stamped = 0
    for ppath in sorted(DATA.glob('paper-*.json')):
        paper = load(ppath)
        for sec in paper['sections']:
            if sec['no'] not in SECTIONS:
                continue
            for q in sec['questions']:
                for item in (q, q.get('or')):
                    if item and item.get('answer') in by_answer:
                        item['keywords'] = by_answer[item['answer']]
                        stamped += 1
        save(ppath, paper)
    print(f'Keywords stamped into {len(by_answer)} lesson answers and {stamped} paper answers')


if __name__ == '__main__':
    main()
