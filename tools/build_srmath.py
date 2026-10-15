"""Build Senior Secondary Mathematics (311) chapter papers, summaries and full model papers.

Usage:
  python tools/build_srmath.py

A chapter source (data/sr-maths/src/lesson-<n>.json) has the same fields as a Secondary Maths source
(see build_math.py), plus two extra objective blocks:
  objective4 - [question, worked answer, years?, extra?]   4 marks: four 1-mark parts
  objective6 - [question, worked answer, years?, extra?]   6 marks: six 1-mark parts
Every answer shows the working; MCQs carry it in {"work": ...}. Only the 23 lessons the NIOS
bifurcation marks for the public (theory) exam are included.

The April 2026 paper (45 questions, 100 marks) has: 20 MCQs; four 2-mark and four 4-mark objective
questions; one 6-mark objective question; 9 short answers of 2 marks, 5 of 4 marks and 2 of 6 marks,
with internal choices in Section B.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'sr-maths'
build_sci.NAME = 'Mathematics'
build_sci.LEVEL = 'senior-secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'sr-maths'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 20),
    ('objective', 'Objective type questions of two 1-mark parts.', 2, None, 4),
    ('objective4', 'Objective type questions of four 1-mark parts.', 4, None, 4),
    ('objective6', 'Objective type question of six 1-mark parts.', 6, None, 1),
    ('vsa', 'Answer the following (2 marks each).', 2, None, 9),
    ('sa', 'Answer the following (4 marks each).', 4, None, 5),
    ('la', 'Answer the following (6 marks each).', 6, None, 2),
]
build_sci.META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–20 are MCQs (1 mark each); 21–24 have two 1-mark parts; 25–28 have four '
    '1-mark parts; 29 has six 1-mark parts.',
    'Section B: questions 30–38 carry 2 marks, 39–43 carry 4 marks and 44–45 carry 6 marks.',
    'Every answer shows the working. Questions from previous NIOS papers show the exam they appeared in.',
]
build_sci.INSTRUCTIONS_CHAPTER = [
    'Practice set for this lesson in the question types of the April 2026 paper.',
    'Every answer shows the working. Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

_build_question = build_sci.build_question


def build_question(item, qid):
    """Allow the extra dict straight after the answer when a question has no years."""
    at = 3 if len(item) >= 3 and isinstance(item[1], list) else 2
    if len(item) > at and isinstance(item[at], dict):
        item = list(item[:at]) + [None] + list(item[at:])
    return _build_question(item, qid)


build_sci.build_question = build_question

if __name__ == '__main__':
    build_sci.main()
