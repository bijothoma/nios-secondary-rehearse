"""Build Tourism (337, Senior Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_tourism.py

Sources are in data/tourism/src (see build_opt.py). Only the public-exam lessons of the NIOS bifurcation are
included: 3, 4, 5, 7, 8, 9, 10, 13, 14, 18, 19 and the three lessons of either optional module. The optional
lessons are numbered 20-22 (Module 6A, Travel and Tour Operation Business) and 23-25 (Module 6B, Hospitality
Management) in the app; the textbook numbers them 20-22 in both modules.

The April 2026 paper (53 questions, 100 marks, 3 hours): Section A has 16 MCQs and 14 two-mark objective questions
(two parts of 1 mark); Section B has ten 2-mark very short, four 3-mark short and two 6-mark long answers;
Section C has, for the chosen optional module, 4 MCQs, one 2-mark objective question and two 3-mark short answers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_opt as b  # noqa: E402
from build_sci import APP_DIR  # noqa: E402

b.SUBJECT = 'tourism'
b.NAME = 'Tourism'
b.DATA = APP_DIR / 'data' / 'tourism'
b.TYPES = {
    'mcq': ('mcq', 'Choose the correct answer.', 1, None),
    'objective': ('objective', 'Objective type questions: each has two parts of 1 mark '
                               '(fill in the blanks, true/false, match the columns or one word).', 2, None),
    'vsa': ('vsa', 'Very short answer questions.', 2, '30–50 words'),
    'sa': ('sa', 'Short answer questions.', 3, '50–80 words'),
    'la': ('la', 'Long answer questions.', 6, '80–120 words'),
}
b.COMPULSORY = {'mcq': 16, 'objective': 14, 'vsa': 10, 'sa': 4, 'la': 2}
b.OPTIONAL = {'mcq': 4, 'objective': 1, 'sa': 2}
b.GROUPS = {'A': 'Module I (Travel and Tour Operation Business)', 'B': 'Module II (Hospitality Management)'}
b.META = 'Time: 3 hours · Maximum marks: 100 (with one optional module) · Modelled on the April 2026 NIOS paper'
b.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'Section A: MCQs carry 1 mark; objective questions carry 2 marks (two parts of 1 mark each).',
    'Section B: very short answers 2 marks (30–50 words), short answers 3 marks (50–80 words), long answers 6 marks (80–120 words).',
    'Section C: attempt either Optional Module I (Travel and Tour Operation Business) or Optional Module II '
    '(Hospitality Management) in all its questions.',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    b.main(min_lessons=17)
