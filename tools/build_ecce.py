"""Build Early Childhood Care and Education (376, Senior Secondary) chapter papers, summaries and full papers.

Usage:
  python tools/build_ecce.py

A chapter source (data/ecce/src/lesson-<n>.json) has the same fields as a Science source
(see build_sci.py): lesson, title, module, summary, mcq, objective, case, vsa, sa, la. Here a case is
{passage, items: [[question, answer], ...], years?} with six 1-mark open questions. Only the 14 lessons
the NIOS bifurcation marks for the public (theory) exam are included.

The April 2026 paper (43 questions, 80 marks; the same layout since April 2024) has: 16 MCQs; a reading
passage with three questions of two 1-mark parts (6 marks); a 4-mark match, 4 marks of true/false,
4 marks of fill in the blanks and 6 marks of one-word answers (here nine 2-mark objective questions of
two 1-mark parts); 6 very short (2), 6 short (3) and 2 long (5) answer questions, with internal choices.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'ecce'
build_sci.NAME = 'Early Childhood Care and Education'
build_sci.LEVEL = 'senior-secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'ecce'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 16),
    ('case', 'Read the passage and answer the questions that follow.', 1, None, 1),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(match the columns, true/false, fill in the blanks or one-word answers).', 2, None, 9),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 6),
    ('sa', 'Short answer questions.', 3, '50–80 words', 6),
    ('la', 'Long answer questions.', 5, '80–120 words', 2),
]
build_sci.META = 'Time: 3 hours · Maximum marks: 80 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: 16 MCQs (1 mark each); a reading passage with six 1-mark questions; nine questions with two '
    'parts of 1 mark each (match the columns, true/false, fill in the blanks, one-word answers).',
    'Section B: 2-mark answers in 30–50 words, 3-mark answers in 50–80 words, 5-mark answers in 80–120 words.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
