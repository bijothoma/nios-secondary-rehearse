"""Build Home Science (321, Senior Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_homesci.py

Sources are in data/sr-home-science/src (see build_opt.py). The subject id is 'sr-home-science' so it stays separate
from the Secondary 'home-science'. Only the public-exam lessons of the NIOS bifurcation are included: 2, 5, 6, 9, 12,
13, 14, 15, 16, 17, 19, 20, 21, 24, 26, 27 and lessons 29-31 of either optional module. The optional lessons are
numbered 29-31 (Module 6A, Housekeeping) and 32-34 (Module 6B, Creative Hand Embroidery) in the app; the textbook
numbers them 29-31 in both modules.

The April 2026 paper (43 questions, 80 marks, 3 hours): 16 MCQs (three of them from the optional module), twelve
2-mark objective questions (one optional), nine 2-mark very short answers (two optional), four 3-mark short answers
(one optional) and two 5-mark long answers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_opt as b  # noqa: E402
from build_sci import APP_DIR  # noqa: E402

b.SUBJECT = 'sr-home-science'
b.NAME = 'Home Science'
b.DATA = APP_DIR / 'data' / 'sr-home-science'
b.TYPES = {
    'mcq': ('mcq', 'Choose the correct answer.', 1, None),
    'objective': ('objective', 'Objective type questions: each has two parts of 1 mark '
                               '(true/false, match the columns, fill in the blanks or give reasons).', 2, None),
    'vsa': ('vsa', 'Very short answer questions.', 2, '30–50 words'),
    'sa': ('sa', 'Short answer questions.', 3, '50–80 words'),
    'la': ('la', 'Long answer questions.', 5, '80–120 words'),
}
b.COMPULSORY = {'mcq': 13, 'objective': 11, 'vsa': 7, 'sa': 3, 'la': 2}
b.OPTIONAL = {'mcq': 3, 'objective': 1, 'vsa': 2, 'sa': 1}
b.GROUPS = {'A': 'Module A (Housekeeping)', 'B': 'Module B (Creative Hand Embroidery)'}
b.META = 'Time: 3 hours · Maximum marks: 80 (with one optional module) · Modelled on the April 2026 NIOS paper'
b.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: MCQs carry 1 mark; objective questions carry 2 marks.',
    'Section B: very short answers 2 marks (30–50 words), short answers 3 marks (50–80 words), long answers 5 marks '
    '(80–120 words).',
    'Attempt the questions of either Optional Module A (Housekeeping) or Optional Module B (Creative Hand Embroidery) '
    'in all sections.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    b.main(min_lessons=22)
