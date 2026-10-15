"""Build Physics (312, Senior Secondary) chapter papers, summaries and full model papers.

Usage:
  python tools/build_phy.py

A chapter source (data/physics/src/lesson-<n>.json) has the same fields as a Science source
(see build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la. Only the 18 lessons
the NIOS bifurcation marks for the public (theory) exam are included.

The April 2026 paper (43 questions, 80 marks) has: 16 MCQs; twelve 2-mark objective questions made
of two 1-mark parts; 9 very short (2), 4 short (3) and 2 long (5) answer questions, with internal
choices in Section B. There is no passage section.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'physics'
build_sci.NAME = 'Physics'
build_sci.LEVEL = 'senior-secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'physics'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 16),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(fill in the blanks, true/false, match or one word).', 2, None, 12),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 9),
    ('sa', 'Short answer questions.', 3, '50–80 words', 4),
    ('la', 'Long answer questions.', 5, '80–120 words', 2),
]
build_sci.META = 'Time: 3 hours · Maximum marks: 80 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–16 are MCQs (1 mark each). Questions 17–28 have two parts of 1 mark each.',
    'Section B: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, 5-mark answers in '
    '80–120 words. Show the working in numerical questions.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
