"""Build Business Studies (319, Senior Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_sr_business.py

A lesson source (data/sr-business-studies/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la. The subject id is 'sr-business-studies'
so it stays separate from the Secondary 'business-studies'. Only the public-exam lessons of the NIOS bifurcation
are included.

The April 2026 paper (51 questions, 100 marks, 3 hours) has: 20 MCQs, fifteen 2-mark objective questions (two
parts of 1 mark), six 2-mark very short, six 3-mark short and four 5-mark long answers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'sr-business-studies'
build_sci.NAME = 'Business Studies'
build_sci.LEVEL = 'senior-secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'sr-business-studies'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 20),
    ('objective', 'Objective type questions: each has two parts of 1 mark.', 2, None, 15),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 6),
    ('sa', 'Short answer questions.', 3, '50–80 words', 6),
    ('la', 'Long answer questions.', 5, '80–120 words', 4),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 10
build_sci.META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'MCQs carry 1 mark; objective questions carry 2 marks (two parts of 1 mark each); very short answers carry 2 marks '
    '(30–50 words); short answers 3 marks (50–80 words); long answers 5 marks (80–120 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
