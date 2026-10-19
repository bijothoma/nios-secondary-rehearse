"""Build Basic Computing (608, Secondary, vocational) lesson papers, summaries and full model papers.

Usage:
  python tools/build_computing.py

A lesson source (data/basic-computing/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, q1, q2, q3, q4. Every question is
[question, answer, years?, extra?]. q1 is a 1-mark one-line answer, q2 a 2-mark short answer, q3 a
3-mark answer and q4 the 4-mark word-processing question that asks for the steps (only the Digital
Documentation lesson has it). All 15 lessons of the textbook are included: NIOS has no bifurcation
for this vocational course.

The April 2026 paper (21 questions, 40 marks, 2 hours) has: eight 1-mark, eight 2-mark and four 3-mark
questions, then one 4-mark question on a given paragraph in MS Word.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'basic-computing'
build_sci.NAME = 'Basic Computing'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'basic-computing'
build_sci.SECTIONS = [
    ('q1', 'Answer in one line.', 1, None, 8),
    ('q2', 'Short answer questions.', 2, '30–50 words', 8),
    ('q3', 'Answer the questions.', 3, '50–80 words', 4),
    ('q4', 'Word-processing task: write the steps for each part.', 4, None, 1),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 10
build_sci.META = 'Time: 2 hours · Maximum marks: 40 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory and carry marks as indicated against each question.',
    'Questions 1–8 carry 1 mark, questions 9–16 carry 2 marks, questions 17–20 carry 3 marks and '
    'question 21 carries 4 marks.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
