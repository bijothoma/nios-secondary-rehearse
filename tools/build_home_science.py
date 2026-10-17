"""Build Home Science (216, Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_home_science.py

A lesson source (data/home-science/src/lesson-<n>.json) has the same fields as a Science source
(see build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la. An objective question
is one 2-mark question of four statements or pairs (true/false, match the columns, fill in the blanks,
arrange in sequence), shown as [question, answer, years?, extra?]. Only the 15 lessons the NIOS
bifurcation marks for the public (theory) exam are included.

The April 2026 paper (47 questions, 85 marks; the layout used since April 2024) has: 19 MCQs; twelve
2-mark objective questions; ten 2-mark very short, four 3-mark short and two 5-mark long answer
questions, with internal choices.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'home-science'
build_sci.NAME = 'Home Science'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'home-science'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 19),
    ('objective', 'Objective type questions: each has four statements or pairs of ½ mark '
                  '(true/false, match the columns, fill in the blanks or arrange in sequence).', 2, None, 12),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 10),
    ('sa', 'Short answer questions.', 3, '50–80 words', 4),
    ('la', 'Long answer questions.', 5, '80–120 words', 2),
]
build_sci.META = 'Time: 2½ hours · Maximum marks: 85 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–19 are MCQs (1 mark each); questions 20–31 are objective questions of 2 marks each.',
    'Section B: questions 32–41 carry 2 marks (30–50 words), questions 42–45 carry 3 marks (50–80 words) '
    'and questions 46–47 carry 5 marks (80–120 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
