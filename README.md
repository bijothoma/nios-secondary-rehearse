# NIOS Secondary Rehearse

Practice app for NIOS 10th (Secondary) model question papers, one paper per lesson.
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
- All of these builders share `build_question` in `tools/build_ss.py`. It marks an MCQ `fixed` (options
  keep their printed order instead of being shuffled) when an option refers to the others, such as
  "all of these", "none of the above" or "both (A) and (B)".
