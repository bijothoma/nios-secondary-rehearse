"""Build Mass Communication (335, Senior Secondary) lesson papers, summaries and full model papers.

Usage:
  python tools/build_mass_comm.py

A lesson source (data/mass-communication/src/lesson-<n>.json) has the same fields as a Science source (see
build_sci.py): lesson, title, module, summary, mcq, objective, vsa, sa, la. Every question is a plain
[question, answer, years?, extra?] (MCQs have options and a letter). The Optional Modules are separate lessons with
their own keys: lessons 27 and 28 hold Module A (Traditional Media) and lessons 29 and 30 Module B
(Photojournalism), with keys mcqA/objA/vsaA/laA and mcqB/objB/vsaB/laB. Only the 16 core lessons and the
optional lessons the NIOS bifurcation marks for the public exam are included.

The April 2026 paper (43 questions, 80 marks, 3 hours) has: 16 MCQs, twelve 2-mark objective questions
(two parts of 1 mark), seven 2-mark very short, six 3-mark short and two 4-mark long answers. The optional
questions are given for both modules; a student answers one module. A full model paper therefore shows both
Module A and Module B sections.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sci  # noqa: E402

build_sci.SUBJECT = 'mass-communication'
build_sci.NAME = 'Mass Communication'
build_sci.LEVEL = 'senior-secondary'
build_sci.DATA = build_sci.APP_DIR / 'data' / 'mass-communication'
OPT = 'Optional Module %s (%s): attempt %s or Module %s. '
build_sci.SECTIONS = [
    ('mcq', 'Choose the correct answer.', 1, None, 15),
    ('mcqA', OPT % ('A', 'Traditional Media', 'A', 'B') + 'Choose the correct answer.', 1, None, 1),
    ('mcqB', OPT % ('B', 'Photojournalism', 'B', 'A') + 'Choose the correct answer.', 1, None, 1),
    ('objective', 'Objective type questions: each has two parts of 1 mark.', 2, None, 9),
    ('objA', OPT % ('A', 'Traditional Media', 'A', 'B') + 'Objective type questions: two parts of 1 mark.', 2, None, 3),
    ('objB', OPT % ('B', 'Photojournalism', 'B', 'A') + 'Objective type questions: two parts of 1 mark.', 2, None, 3),
    ('vsa', 'Very short answer questions.', 2, '30–50 words', 5),
    ('vsaA', OPT % ('A', 'Traditional Media', 'A', 'B') + 'Very short answer questions.', 2, '30–50 words', 2),
    ('vsaB', OPT % ('B', 'Photojournalism', 'B', 'A') + 'Very short answer questions.', 2, '30–50 words', 2),
    ('sa', 'Short answer questions.', 3, '50–80 words', 6),
    ('la', 'Long answer question.', 4, '80–120 words', 1),
    ('laA', OPT % ('A', 'Traditional Media', 'A', 'B') + 'Long answer question.', 4, '80–120 words', 1),
    ('laB', OPT % ('B', 'Photojournalism', 'B', 'A') + 'Long answer question.', 4, '80–120 words', 1),
]
build_sci.MIN_LESSONS_FOR_PAPERS = 10
build_sci.META = 'Time: 3 hours · Maximum marks: 80 · Modelled on the April 2026 NIOS paper'
build_sci.INSTRUCTIONS_FULL = [
    'All questions are compulsory. Where a question has OR, answer either one.',
    'For the Optional Modules, attempt Module A (Traditional Media) or Module B (Photojournalism) in the sections that '
    'have both.',
    'MCQs carry 1 mark; objective questions carry 2 marks (two parts of 1 mark each); very short answers carry 2 marks '
    '(30–50 words); short answers 3 marks (50–80 words); the long answer 4 marks (80–120 words).',
    'Questions from previous NIOS papers show the exam they appeared in.',
]

if __name__ == '__main__':
    build_sci.main()
