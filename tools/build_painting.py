"""Build Painting (225, Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_painting.py

A lesson source (data/painting/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, mcq, case, case2, vsa, sa, la. Here `case` is a passage
with five 1-mark fill-in-the-blank questions and `case2` a passage with four 1-mark true/false
statements: {passage, items: [[question, answer], ...], years?}. Only the six lessons the NIOS
bifurcation marks for the public (theory) exam are included.

The April 2026 paper (14 questions, 30 marks; the layout used since April 2024) has: 6 MCQs; two
passages (five fill-in-the-blanks and four true/false statements); four 2-mark short questions, one
3-mark short answer and one 4-mark long answer, with internal choices.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'painting'
build_sci.NAME = 'Painting'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'painting'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 6),
    ('case', 'Read the passage and fill in the blanks.', 1, None, 1),
    ('case2', 'Read the passage and state whether each statement is true or false.', 1, None, 1),
    ('vsa', 'Short questions.', 2, '30–40 words', 4),
    ('sa', 'Short answer question.', 3, '50–60 words', 1),
    ('la', 'Long answer question.', 4, '70–80 words', 1),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 6
build_sci.META = 'Time: 2 hours · Maximum marks: 30 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–6 are MCQs (1 mark each). Section B: question 7 (passage with five fill-in-the-blanks) '
    'and question 8 (passage with four true/false statements), 1 mark each part.',
    'Section C: questions 9–12 carry 2 marks (30–40 words), question 13 carries 3 marks (50–60 words) and '
    'question 14 carries 4 marks (70–80 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
