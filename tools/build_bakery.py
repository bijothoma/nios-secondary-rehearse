"""Build Bakery and Confectionery (256, Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_bakery.py

A lesson source (data/bakery/src/lesson-<n>.json) has: lesson, title, module, summary (see build_sci.py) and
the question lists fill, tf and sa, each item [question, answer, years?]. The course is a vocational one whose
theory paper (the layout used since 2022) has 3 questions, 40 marks, 2 hours: fifteen fill-in-the-blanks (1 mark),
fifteen true/false statements (1 mark) and four short answers of 2.5 marks (five points each). The nine lessons
of the NIOS book are covered except lesson 9, the glossary of bakery terms, which is not examined as a lesson.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'bakery'
build_sci.NAME = 'Bakery and Confectionery'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'bakery'
build_sci.SECTIONS = [
    ('fill', 'Fill in the blanks and write the correct answers.', 1, None, 15),
    ('tf', 'State whether the following statements are True or False.', 1, None, 15),
    ('sa', 'Answer the following questions (five points each).', 2.5, None, 4),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 8
build_sci.META = 'Time: 2 hours · Maximum marks: 40 · Modelled on the April 2026 NIOS paper (code 256)'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory and carry marks as indicated against each question.',
    'Question 1: fifteen fill-in-the-blanks (1 mark each). Question 2: fifteen True/False statements (1 mark each). '
    'Question 3: four questions of 2½ marks each.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
