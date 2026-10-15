"""Build Business Studies (215) chapter papers, summaries and full model papers.

Usage:
  python tools/build_bst.py

A chapter source (data/business-studies/src/lesson-<n>.json) has the same fields as a Science source
(see build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la.

The April 2026 paper (51 questions, 100 marks) has: 20 MCQs; fifteen 2-mark objective questions made
of two 1-mark parts; 6 very short (2), 6 short (3) and 4 long (5) answer questions, with internal
choices in Section C. There is no passage section: case-based questions are 5-mark long answers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'business-studies'
build_sci.NAME = 'Business Studies'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'business-studies'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 20),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(fill in the blanks, true/false, match, one word or identify).', 2, None, 15),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 6),
    ('sa', 'Short answer questions.', 3, '50–80 words', 6),
    ('la', 'Long answer questions, including case-based questions.', 5, '80–120 words', 4),
]
build_sci.META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–20 are MCQs (1 mark each). Section B: questions 21–35 have two parts '
    'of 1 mark each.',
    'Section C: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, 5-mark answers in '
    '80–120 words.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
