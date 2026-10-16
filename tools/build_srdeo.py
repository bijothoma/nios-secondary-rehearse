"""Build Senior Secondary Data Entry Operations (336): summaries, lesson practice sets and full papers.

Usage:
  python tools/build_srdeo.py

Uses build_deo.py (the Secondary course, 229) with the same source format, read from
data/sr-deo/src/lesson-<n>.json. Lessons 1-9 share the 229 textbook; 336 adds lesson 10
(Introduction to Internet). The April 2026 paper (24 questions, 40 marks) has 7 MCQs, three
2-mark questions of two 1-mark parts (assertion-reason, true/false, fill in the blanks),
7 one-mark questions, 2 very short (2), 4 short (3) and 1 long (4) answer questions; since
2024 the short answers come from lessons 1, 5, 5 and 10 and the long answer from lesson 10.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_deo  # noqa: E402
from convert_lesson import APP_DIR  # noqa: E402

build_deo.SUBJECT = 'sr-deo'
build_deo.NAME = 'Data Entry Operations'
build_deo.DATA = APP_DIR / 'data' / build_deo.SUBJECT
LEVEL = 'senior-secondary'

build_deo.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 7),
    ('ar', 'Assertion (A) and Reason (R): choose the correct option.', 1, None, 2),
    ('tf', 'State True or False.', 1, None, 2),
    ('fill2', 'Fill in the blanks.', 2, None, 1),  # one question with two 1-mark blanks
    ('oneword', 'Fill in the blank or answer in one word.', 1, None, 7),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 2),
    ('sa', 'Short answer questions.', 3, '50–80 words', 4),
    ('la', 'Long answer question.', 4, '80–120 words', 1),
]
build_deo.DEAL_ORDER = {
    'vsa': [1],
    'sa': [1, 5, 5, 10] * 3,
    'la': [10],
}
build_deo.DEFAULT_ORDER = [4, 8, 9, 1, 5, 4, 8, 9, 10, 4, 8, 1]
build_deo.META = 'Time: 2 hours · Maximum marks: 40 · Modelled on the April 2026 NIOS paper (336)'
build_deo.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–7 are MCQs (1 mark each); questions 8–10 have two parts of 1 mark each '
    '(assertion–reason, true/false, fill in the blanks); questions 11–17 carry 1 mark each.',
    'Section B: questions 18–19 carry 2 marks (30–50 words), 20–23 carry 3 marks (50–80 words) '
    'and 24 carries 4 marks (80–120 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]


def register(sources):
    path = APP_DIR / 'data' / 'subjects.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    sid = build_deo.SUBJECT
    subj = next((s for s in data['subjects'] if s['id'] == sid), None)
    if subj is None:
        subj = {'id': sid}
        data['subjects'].append(subj)
    subj.update(name=build_deo.NAME, label='', level=LEVEL)
    lessons = [{'no': s['lesson'], 'title': s['title'], 'file': f'data/{sid}/lesson-{s["lesson"]}.json',
                'summary': f'data/{sid}/summary/lesson-{s["lesson"]}.json'} for s in sources]
    for p in range(build_deo.FULL_PAPERS):
        lessons.append({'no': 900 + p + 1, 'tag': 'Full paper', 'title': f'Model Question Paper {p + 1}',
                        'file': f'data/{sid}/paper-{p + 1}.json'})
    subj['lessons'] = lessons
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


build_deo.register = register

if __name__ == '__main__':
    build_deo.main()
