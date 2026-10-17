"""Build Indian Culture and Heritage (223, Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_ich.py

A lesson source (data/ich/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la. An objective question is one
2-mark question of two parts (fill in the blanks, true/false, one word or phrase, match, short phrases):
[question, answer, years?, extra?]. Only the 12 lessons the NIOS syllabus bifurcation marks for the
public (theory) exam are included.

The April 2026 paper (50 questions, 100 marks) has: 20 MCQs; fifteen 2-mark objective questions; five
2-mark very short, five 3-mark short and five 5-mark long answer questions, with internal choices.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'ich'
build_sci.NAME = 'Indian Culture and Heritage'
build_sci.LEVEL = 'secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'ich'
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 20),
    ('objective', 'Objective type questions: each has two parts of 1 mark '
                  '(fill in the blanks, true/false, one word or phrase, match).', 2, None, 15),
    ('vsa', 'Very short answer questions.', 2, 'about 25 words', 5),
    ('sa', 'Short answer questions.', 3, '40–50 words', 5),
    ('la', 'Long answer questions.', 5, '150–200 words', 5),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 10
build_sci.META = 'Time: 3 hours · Maximum marks: 100 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: questions 1–20 are MCQs (1 mark each). Section B: questions 21–35 are objective questions of 2 marks '
    '(two parts of 1 mark each).',
    'Section C: questions 36–40 carry 2 marks (about 25 words); Section D: questions 41–45 carry 3 marks '
    '(40–50 words); Section E: questions 46–50 carry 5 marks (150–200 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
