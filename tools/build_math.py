"""Build Mathematics (211) chapter papers, summaries and full model papers.

Usage:
  python tools/build_math.py

A chapter source (data/maths/src/lesson-<n>.json) has the same fields as a Science source
(see build_sci.py). Every answer shows the working, not just the result:
  mcq       - [question, [options], answer letter, years?, {"work": "step\\nstep"}]
              the working is shown under the question once it has been answered
  objective, vsa, sa, la
            - [question, "worked answer, one step per line (\\n)", years?, extra?]

The April 2026 paper (44 questions, 85 marks) has: 17 MCQs; ten 2-mark objective questions made
of two 1-mark parts; one case study with five 1-mark MCQs; 9 very short (2), 5 short (3) and
2 long (5) answer questions, with internal choices in Section B.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'maths'
build_sci.NAME = 'Mathematics'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'maths'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 17),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(fill in the blanks, match the columns or true/false).', 2, None, 10),
    ('case', 'Case study: read the information and answer the questions that follow.', 1, None, 1),
    ('vsa', 'Very short answer questions.', 2, None, 9),
    ('sa', 'Short answer questions.', 3, None, 5),
    ('la', 'Long answer questions.', 5, None, 2),
]
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–17 are MCQs (1 mark each); questions 18–27 have two parts of 1 mark each; '
    'question 28 is a case study with five 1-mark questions.',
    'Section B: questions 29–37 carry 2 marks, 38–42 carry 3 marks and 43–44 carry 5 marks.',
    'Every answer shows the working. Questions from previous NIOS papers show the exam they appeared in.',
]
build_sci.INSTRUCTIONS_CHAPTER = [
    'Practice set for this lesson in the question types of the April 2026 paper.',
    'Every answer shows the working. Where a question has OR, answer either one.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

_build_question = build_sci.build_question


def build_question(item, qid):
    """Allow the extra dict straight after the answer when a question has no years (case items)."""
    at = 3 if len(item) >= 3 and isinstance(item[1], list) else 2
    if len(item) > at and isinstance(item[at], dict):
        item = list(item[:at]) + [None] + list(item[at:])
    return _build_question(item, qid)


build_sci.build_question = build_question

if __name__ == '__main__':
    build_sci.main()
