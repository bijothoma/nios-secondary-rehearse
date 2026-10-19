"""Build Psychology (222, Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_psychology.py

A lesson source (data/psychology/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, mcq, objective, objective4, vsa, sa, la. `objective` is a
2-mark question of two parts of 1 mark, `objective4` a 4-mark question of four parts of 1 mark:
[question, answer, years?, extra?]. Only the 16 lessons the NIOS bifurcation marks for the public
(theory) exam are included.

The April 2026 paper (48 questions, 100 marks) has: 20 MCQs; nine 2-mark and three 4-mark objective
questions; six 2-mark very short, six 3-mark short and four 5-mark long answer questions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'psychology'
build_sci.NAME = 'Psychology'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'psychology'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 20),
    ('objective', 'Objective type questions: each has two parts of 1 mark.', 2, None, 9),
    ('objective4', 'Objective type questions: each has four parts of 1 mark.', 4, None, 3),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 6),
    ('sa', 'Short answer questions.', 3, '50–80 words', 6),
    ('la', 'Long answer questions.', 5, '80–120 words', 4),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 10
build_sci.META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–20 are MCQs (1 mark each); questions 21–29 carry 2 marks (two parts of 1 mark each) '
    'and questions 30–32 carry 4 marks (four parts of 1 mark each).',
    'Section B: questions 33–38 carry 2 marks (30–50 words), questions 39–44 carry 3 marks (50–80 words) and '
    'questions 45–48 carry 5 marks (80–120 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
