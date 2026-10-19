# NIOS Secondary Rehearse

Practice app for NIOS Secondary (10th) and Senior Secondary (12th) model question papers, one paper
per lesson. The home page lists the courses in `levels` of `data/subjects.json`; each subject has a
`level` (Secondary if missing), and `#/secondary` or `#/senior-secondary` lists that course's subjects.
Multiple-choice, fill-in-the-blank, true/false and match-the-following questions are
tappable; the rest have a **Show answer** button. Questions and options are shuffled on
every try, while sections keep the exam order.

## Run locally

Double-click `start.bat` (needs Python), or:

```
python -m http.server 8000
```

then open http://localhost:8000. Opening `index.html` directly does not work, because
the browser blocks loading the JSON data from disk.

## Add a lesson

Each lesson comes from two Word files: the model question paper and its answer key.

```
python tools/convert_lesson.py --subject malayalam --lesson 17 \
    --questions "path/to/question paper.docx" --answers "path/to/answer key.docx"
```

This writes `data/<subject>/lesson-<n>.json` and lists it in `data/subjects.json`.
Fix any `WARNING` lines it prints before committing.

Lessons without a Word paper are written in short form in `data/<subject>/src/lesson-<n>.json`
and built in the April 2026 exam layout with:

```
python tools/build_lesson.py data/malayalam/src/lesson-10.json
```

Questions taken from old NIOS papers are kept separately in
`data/<subject>/past/lesson-<n>.json` and merged in on every conversion:
`refs` adds exam tags (e.g. `"April 2022"`) to existing question ids, and `add`
appends extra questions to a section. Answers marked `"drafted": true` were written
for the app rather than taken from an answer key.

A lesson's text with its English translation (in brackets after each sentence, or as
separate English paragraphs) is added from a Word file with:

```
python tools/convert_text.py --subject malayalam --lesson 16 --docx "path/to/lesson.docx"
```

Lessons typed from the textbook are kept as plain text in `data/<subject>/src/text-<n>.txt`
(see the format at the top of `tools/convert_text.py`) and converted with `--txt` instead of `--docx`.

Lessons whose text is still under copyright are converted with `--local`: the files go to
`local/` (not committed) and are listed in `local/texts.json`, so their text shows only when
the app runs on this computer. On the public site those lessons open the question paper directly.

Summaries are added the same way with `--summary` (a .docx with the Malayalam summary
followed by its English translation, or `data/<subject>/src/summary-<n>.txt`).

The lesson then opens with a menu: Lesson, Lesson with translation, and the model question paper.

Malayalam 1-mark questions show, with their answer, the stanza or sentence of the lesson that holds
the answer (പാഠഭാഗം) and, where useful, a short explanation (വിശദീകരണം). These live in
`data/malayalam/quotes.json` (named by `quotes` in `data/subjects.json`), keyed by
`"<lesson no>|<question text>"` (the left item for a match question), each with `quote` and/or `note`.
Quotes from lessons under copyright are kept in `local/malayalam/quotes.json`, listed under `quotes` in
`local/texts.json`. Because the files are keyed by question text, rebuilding the lesson and full papers
keeps them, but a reworded question loses its quote until its key is updated. A `note` here replaces the
question's own short note.

## Layout

- `index.html`, `app.js`, `style.css`: the app (no build step)
- `data/subjects.json`: subjects and their lessons
- `data/<subject>/lesson-<n>.json`: questions and answers for one lesson (generated)
- `data/<subject>/past/lesson-<n>.json`: additions from old question papers
- `tools/convert_lesson.py`: Word → JSON converter
- `tools/build_ss.py`: builds Social Science from `data/social-science/src/lesson-<n>.json`
  (summary, chapter practice set and three full papers in the April 2026 layout).
  Run `python tools/build_ss.py` after editing a source file. Map pictures live in
  `data/social-science/maps/`.
- `tools/build_ml_papers.py`: mixes questions from all Malayalam lesson papers into three
  full model papers (`data/malayalam/paper-1..3.json`) in the April 2026 layout.
  Re-run it after changing a lesson paper.
- `tools/build_deo.py`: builds Data Entry Operations from `data/data-entry/src/lesson-<n>.json`
  (summary, chapter practice set and three full papers in the April 2026 layout: 25 questions, 40 marks).
- `tools/build_english.py`: builds English from `data/english/src/lesson-<n>.json` (summary and literature
  practice set per lesson) and `data/english/src/papers.json` (reading, writing and grammar of three full
  papers in the April 2026 layout: 35 questions, 100 marks).
- `tools/build_sci.py`: builds Science and Technology from `data/science/src/lesson-<n>.json` (summary,
  chapter practice set and three full papers in the April 2026 layout: 43 questions, 85 marks). Only the
  19 public-exam lessons of the NIOS syllabus bifurcation are included.
- `tools/build_math.py`: builds Mathematics from `data/maths/src/lesson-<n>.json` with the same layout as
  Science (44 questions, 85 marks). Every answer carries its working; for MCQs the `work` field is shown
  once the question is answered. Only the 16 public-exam lessons are included.
- `tools/build_bst.py`: builds Business Studies from `data/business-studies/src/lesson-<n>.json` with the same
  source format (51 questions, 100 marks; no passage section — case questions are long answers). Only the
  13 public-exam (theory) lessons of the NIOS syllabus bifurcation are included.
- `tools/build_eco.py`: builds Economics from `data/economics/src/lesson-<n>.json` with the same source
  format (54 questions, 100 marks). Numerical answers (cost, revenue, credit, mean) show their working.
  Only the 14 public-exam (theory) lessons of the NIOS syllabus bifurcation are included.
- `tools/build_phy.py`: builds Senior Secondary Physics (312) from `data/physics/src/lesson-<n>.json` with the
  same source format (43 questions, 80 marks) and registers it with `level` `senior-secondary`
  (`build_sci.LEVEL`). Only the 18 public-exam lessons of the NIOS syllabus bifurcation are included.
- `tools/build_srmath.py`: builds Senior Secondary Mathematics (311) from `data/sr-maths/src/lesson-<n>.json`
  (45 questions, 100 marks). Besides the usual blocks it has `objective4` (four 1-mark parts) and
  `objective6` (six 1-mark parts). Every answer shows its working. Only the 23 public-exam lessons are included.
- `tools/build_srenglish.py`: builds Senior Secondary English (302, new syllabus) from
  `data/sr-english/src/lesson-<n>.json` (summary and practice set per lesson: MCQ, true/false, match,
  reading passages, blanks, language, 2-, 3- and 4-mark answers) and `data/sr-english/src/papers.json`
  (unseen passages, grammar and writing tasks of three full papers in the April 2026 new-syllabus layout:
  27 questions, 100 marks; lesson questions are dealt to the papers without repeats). Only the 16
  public-exam lessons are included; Model Question Paper 1 reuses the April 2026 unseen sections.
- `tools/build_srdeo.py`: builds Senior Secondary Data Entry Operations (336) from `data/sr-deo/src/lesson-<n>.json`
  with `build_deo.py` and the 336 layout (24 questions, 40 marks: 2 very short, 4 short and 1 long answer; short
  answers from lessons 1, 5, 5 and 10). Lessons 1–9 share the 229 textbook, so their sources started from the
  Secondary ones with the exam tags replaced by 336 ones; lesson 10 (Internet) is 336 only. Only the 6
  public-exam lessons (1, 4, 5, 8, 9, 10) are included.
- `tools/build_ecce.py`: builds Senior Secondary Early Childhood Care and Education (376) from
  `data/ecce/src/lesson-<n>.json` with `build_sci.py` (43 questions, 80 marks: 16 MCQs, a passage with six 1-mark
  questions, nine 2-mark objective questions, 6 very short, 6 short and 2 long answers). Only the 14 public-exam
  lessons of the NIOS syllabus bifurcation are included.
- `tools/build_hindi.py`: builds Secondary Hindi (201) from `data/hindi/src/lesson-<n>.json` (37 questions, 100 marks:
  27 objective in Section A, 10 descriptive in Section B). Lessons carry past-paper years, summaries have English
  translations, and lesson passages/explanations show as quotes. Copyrighted texts and quotes stay in `local/`.
- `tools/build_home_science.py`: builds Secondary Home Science (216) from `data/home-science/src/lesson-<n>.json` with
  `build_sci.py` (47 questions, 85 marks: 19 MCQs, twelve 2-mark objective questions of four statements or pairs, ten
  2-mark, four 3-mark and two 5-mark answers). Only the 15 public-exam lessons of the NIOS syllabus bifurcation are
  included; past-paper questions of April 2022 to April 2026 are tagged by exam.
- `tools/build_painting.py`: builds Secondary Painting (225) from `data/painting/src/lesson-<n>.json` with `build_sci.py`
  (14 questions, 30 marks: 6 MCQs, a passage with five fill-in-the-blanks, a passage with four true/false statements, four
  2-mark, one 3-mark and one 4-mark answer). Only the 6 public-exam lessons are included; `build_sci.py` now supports
  several passage sections (`case`, `case2`) and a lesson-count threshold for full papers.
- `tools/build_ich.py`: builds Secondary Indian Culture and Heritage (223) from `data/ich/src/lesson-<n>.json` with
  `build_sci.py` (50 questions, 100 marks: 20 MCQs, fifteen 2-mark objective questions, five 2-mark, five 3-mark and five
  5-mark answers). Only the 12 public-exam lessons are included. The textbook and bifurcation PDFs were downloaded from
  nios.ac.in; the past papers came from the local All folder.
- `tools/build_psychology.py`: builds Secondary Psychology (222) from `data/psychology/src/lesson-<n>.json` with
  `build_sci.py` (48 questions, 100 marks: 20 MCQs, nine 2-mark and three 4-mark objective questions, six 2-mark, six
  3-mark and four 5-mark answers). Only the 16 public-exam lessons of the bifurcation are included (TMA lessons are
  left out); past-paper questions of April 2025 to April 2026 are tagged by exam.
- `tools/build_computing.py`: builds Secondary Basic Computing (608, vocational) from
  `data/basic-computing/src/lesson-<n>.json` with `build_sci.py` (21 questions, 40 marks: eight 1-mark, eight 2-mark
  and four 3-mark questions, then one 4-mark word-processing question that asks for the steps on a given paragraph).
  All 15 lessons of the textbook are included (NIOS has no bifurcation for this course; the textbook PDF came from
  nios.ac.in). Past-paper questions of April 2024 to April 2026 are tagged by exam. `build_sci.py` now deals a
  section that only some lessons have (the steps question, only in Digital Documentation) over those lessons.
- All of these builders share `build_question` in `tools/build_ss.py`. It marks an MCQ `fixed` (options
  keep their printed order instead of being shuffled) when an option refers to the others, such as
  "all of these", "none of the above" or "both (A) and (B)".
