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

## Layout

- `index.html`, `app.js`, `style.css`: the app (no build step)
- `data/subjects.json`: subjects and their lessons
- `data/<subject>/lesson-<n>.json`: questions and answers for one lesson (generated)
- `data/<subject>/past/lesson-<n>.json`: additions from old question papers
- `tools/convert_lesson.py`: Word → JSON converter
