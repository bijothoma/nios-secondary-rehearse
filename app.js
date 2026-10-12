// Written in plain ES5 (var, function, XMLHttpRequest) so it also runs in older
// browsers such as the Kindle's.
var app = document.getElementById('app');
var scoreEl = document.getElementById('score');
var LETTERS = 'ABCDEFGH';

var subjects = [];
var score = { right: 0, done: 0, total: 0 };

// ---------- helpers ----------

function appendAll(node, items) {
  for (var i = 0; i < items.length; i++) {
    var c = items[i];
    if (c == null || c === false || c === '') continue;
    if (Object.prototype.toString.call(c) === '[object Array]') appendAll(node, c);
    else if (typeof c === 'object') node.appendChild(c);
    else node.appendChild(document.createTextNode(String(c)));
  }
}

function el(tag, attrs) {
  var node = document.createElement(tag);
  attrs = attrs || {};
  for (var k in attrs) {
    if (!attrs.hasOwnProperty(k)) continue;
    var v = attrs[k];
    if (k === 'class') node.className = v;
    else if (k.indexOf('on') === 0) node.addEventListener(k.slice(2), v, false);
    else node.setAttribute(k, v);
  }
  appendAll(node, Array.prototype.slice.call(arguments, 2));
  return node;
}

function setChildren(parent) {
  parent.innerHTML = '';
  appendAll(parent, Array.prototype.slice.call(arguments, 1));
}

function setHidden(node, hidden) {
  node.style.display = hidden ? 'none' : '';
}

function isHidden(node) {
  return node.style.display === 'none';
}

function addClass(node, name) {
  if ((' ' + node.className + ' ').indexOf(' ' + name + ' ') < 0) node.className += ' ' + name;
}

function find(arr, test) {
  for (var i = 0; i < arr.length; i++) if (test(arr[i])) return arr[i];
  return null;
}

function shuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function loadJSON(path, done, fail) {
  var xhr = new XMLHttpRequest();
  // The timestamp stops the browser from showing an old copy after an update.
  xhr.open('GET', path + '?t=' + new Date().getTime(), true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState !== 4) return;
    if (xhr.status !== 200 && !(xhr.status === 0 && xhr.responseText)) {
      fail(new Error('Could not load ' + path));
      return;
    }
    var data;
    try {
      data = JSON.parse(xhr.responseText);
    } catch (e) {
      fail(new Error('Could not read ' + path));
      return;
    }
    done(data);
  };
  xhr.send();
}

function showError(err) {
  setChildren(app, el('p', { 'class': 'feedback bad' }, err.message));
}

function updateScore() {
  setHidden(scoreEl, score.total === 0);
  scoreEl.textContent = 'Score: ' + score.right + ' / ' + score.total;
}

// ---------- pages ----------

function renderHome() {
  setHidden(scoreEl, true);
  setChildren(app,
    el('h1', {}, 'Choose a subject'),
    el('div', { 'class': 'tiles' },
      subjects.map(function (s) {
        return el('a', { 'class': 'tile', href: '#/' + s.id },
          el('strong', {}, s.label || s.name),
          el('span', {}, s.label ? s.name + ' · ' : '', lessonCount(s))
        );
      })
    )
  );
}

function lessonCount(s) {
  var n = s.lessons.length;
  return n === 0 ? 'Coming soon' : n + ' lesson' + (n > 1 ? 's' : '');
}

function renderSubject(subject) {
  setHidden(scoreEl, true);
  setChildren(app,
    el('div', { 'class': 'crumbs' }, el('a', { href: '#/' }, '« Subjects')),
    el('h1', {}, subject.label || subject.name),
    subject.lessons.length === 0
      ? el('p', { 'class': 'muted' }, 'No lessons added yet.')
      : el('div', { 'class': 'tiles' },
          subject.lessons.map(function (l) {
            return el('a', { 'class': 'tile', href: '#/' + subject.id + '/' + l.no },
              el('span', {}, lessonLabel(l)),
              el('strong', {}, l.button || l.title)
            );
          })
        )
  );
}

// Full model papers carry a tag instead of a lesson number.
function lessonLabel(l) {
  return l.tag || 'Lesson ' + l.no;
}

function lessonHash(subject, lessonMeta) {
  return '#/' + subject.id + '/' + lessonMeta.no;
}

function renderLessonMenu(subject, lessonMeta) {
  setHidden(scoreEl, true);
  var base = lessonHash(subject, lessonMeta);
  setChildren(app,
    el('div', { 'class': 'crumbs' }, el('a', { href: '#/' + subject.id }, '« ' + (subject.label || subject.name))),
    el('div', { 'class': 'muted' }, lessonLabel(lessonMeta)),
    el('h1', {}, lessonMeta.title),
    el('div', { 'class': 'tiles' },
      lessonMeta.text ? el('a', { 'class': 'tile', href: base + '/text' },
        el('span', {}, 'Read'), el('strong', {}, 'Lesson')) : null,
      lessonMeta.text ? el('a', { 'class': 'tile', href: base + '/translation' },
        el('span', {}, 'Read with English'), el('strong', {}, 'Lesson with translation')) : null,
      lessonMeta.summary ? el('a', { 'class': 'tile', href: base + '/summary' },
        el('span', {}, 'Revise'), el('strong', {}, 'Summary')) : null,
      el('a', { 'class': 'tile', href: base + '/paper' },
        el('span', {}, 'Practise'), el('strong', {}, 'Model question paper'))
    )
  );
}

// kind is 'text' (the lesson) or 'summary'; both files use the same block format.
function renderText(subject, lessonMeta, kind, withEnglish) {
  setHidden(scoreEl, true);
  var views = kind === 'summary' ? ['/summary', '/summary-en'] : ['/text', '/translation'];
  loadJSON(lessonMeta[kind], function (doc) {
    var blocks = [];
    var hasEnglish = false;
    doc.blocks.forEach(function (b) {
      b.parts.forEach(function (p) { if (p[0] === 'en') hasEnglish = true; });
      var parts = [];
      b.parts.forEach(function (p) {
        if (!withEnglish && p[0] === 'en') return;
        var last = parts[parts.length - 1];
        // Without English, sentences rejoin into one paragraph; poem lines keep their breaks.
        if (!withEnglish && last) {
          var poem = last[1].indexOf('\n') >= 0 || p[1].indexOf('\n') >= 0;
          parts[parts.length - 1] = ['ml', last[1] + (poem ? '\n' : ' ') + p[1]];
        } else {
          parts.push(p);
        }
      });
      if (!parts.length) return;
      var tag = b.type === 'title' ? 'h1' : b.type === 'heading' ? 'h2' : 'p';
      blocks.push(el(tag, { 'class': 'text-' + b.type },
        parts.map(function (p) { return el('span', { 'class': p[0] }, p[1]); })));
    });
    setChildren(app,
      el('div', { 'class': 'crumbs' }, el('a', { href: lessonHash(subject, lessonMeta) }, '« Lesson ' + lessonMeta.no)),
      el('div', { 'class': 'lesson-text' + (withEnglish ? ' with-en' : '') }, blocks),
      el('div', { 'class': 'actions' },
        hasEnglish ? el('a', { 'class': 'btn', href: lessonHash(subject, lessonMeta) + views[withEnglish ? 0 : 1] },
          withEnglish ? 'Hide English' : 'Show English') : null,
        ' ',
        el('a', { 'class': 'btn primary', href: lessonHash(subject, lessonMeta) + '/paper' }, 'Model question paper'))
    );
    window.scrollTo(0, 0);
  }, showError);
}

function renderPaper(subject, lessonMeta) {
  loadJSON(lessonMeta.file, function (paper) {
    score = { right: 0, done: 0, total: 0 };
    var restart = function () { renderPaper(subject, lessonMeta); };

    var head = el('div', { 'class': 'paper-head' },
      el('div', { 'class': 'crumbs' }, lessonMeta.text || lessonMeta.summary
        ? el('a', { href: lessonHash(subject, lessonMeta) }, '« Lesson ' + lessonMeta.no)
        : el('a', { href: '#/' + subject.id }, '« ' + (subject.label || subject.name))),
      el('div', { 'class': 'muted' }, lessonLabel(lessonMeta)),
      el('h1', {}, paper.title),
      paper.author ? el('div', {}, paper.author) : null,
      paper.meta ? el('div', { 'class': 'muted' }, paper.meta) : null,
      paper.instructions && paper.instructions.length
        ? el('ul', {}, paper.instructions.map(function (t) { return el('li', {}, t); }))
        : null,
      el('div', { 'class': 'actions' },
        el('button', { 'class': 'btn', onclick: restart }, 'Shuffle & start again')
      )
    );

    var sections = paper.sections.map(renderSection);
    var summary = el('div', { 'class': 'summary' },
      el('p', { id: 'summary-text' }),
      el('button', { 'class': 'btn primary', onclick: restart }, 'Try again with a new shuffle')
    );

    setChildren(app, head, sections, summary);
    updateScore();
    updateSummary();
    window.scrollTo(0, 0);
  }, showError);
}

function updateSummary() {
  var t = document.getElementById('summary-text');
  if (!t) return;
  t.textContent = score.total
    ? 'Choice questions: ' + score.right + ' of ' + score.total +
      ' right on the first try (' + score.done + ' answered).'
    : '';
}

function renderSection(sec) {
  var qs = shuffle(sec.questions);
  // Options for a "match" section are all the right-hand items of that section.
  var matchPool = sec.questions
    .filter(function (q) { return q.type === 'match'; })
    .map(function (q) { return q.right; });

  return el('div', { 'class': 'section' },
    el('h2', {}, el('span', {}, sec.no + '. ' + sec.title), el('span', { 'class': 'marks' }, sec.marks)),
    sec.note ? el('p', { 'class': 'note' }, sec.note) : null,
    qs.map(function (q, i) {
      var num = sec.no + '.' + (i + 1);
      if (q.type === 'mcq') {
        var correct = q.options[LETTERS.indexOf(q.answer)];
        return renderChoice(num, q.q, q.years, q.options, correct, q.note, q.image);
      }
      if (q.type === 'match') {
        return renderChoice(num, q.left + ' — ?', q.years, matchPool, q.right);
      }
      return renderOpen(num, q);
    })
  );
}

// years: the exams this question was asked in, e.g. ["April 2025", "October 2019"]
// image: an optional picture (e.g. a map) shown under the question.
function questionText(num, text, years, image) {
  var p = el('p', { 'class': 'q-text' },
    el('span', { 'class': 'q-num' }, num),
    text,
    (years || []).map(function (y) {
      return el('span', { 'class': 'year', title: 'Asked in this exam' }, y);
    })
  );
  return image ? [p, el('img', { 'class': 'q-img', src: image, alt: 'Map for question ' + num })] : p;
}

// Marks an option as right or wrong with a symbol as well as a style, so it reads
// on greyscale (e-ink) screens where green and red look the same.
function markOption(button, kind) {
  addClass(button, kind);
  button.appendChild(el('span', { 'class': 'mark' }, kind === 'correct' ? '✓' : '✗'));
}

function renderChoice(num, text, years, options, correct, note, image) {
  score.total++;
  var firstTry = true;
  var finished = false;

  var feedback = el('p', { 'class': 'feedback' });
  var showBtn = el('button', { 'class': 'btn', onclick: reveal }, 'Show answer');
  setHidden(showBtn, true);
  var noteEl = note ? el('p', { 'class': 'note' }, note) : null;
  if (noteEl) setHidden(noteEl, true);

  var shown = shuffle(options);
  var buttons = shown.map(function (opt, i) {
    return el('button', { 'class': 'opt', onclick: function () { choose(i); } },
      el('span', { 'class': 'letter' }, '(' + LETTERS.charAt(i) + ')'),
      el('span', { 'class': 'opt-text' }, opt)
    );
  });

  function finish() {
    finished = true;
    buttons.forEach(function (b) { b.disabled = true; });
    setHidden(showBtn, true);
    if (noteEl) setHidden(noteEl, false);
    score.done++;
    updateScore();
    updateSummary();
  }

  function choose(i) {
    if (finished) return;
    if (shown[i] === correct) {
      markOption(buttons[i], 'correct');
      if (firstTry) score.right++;
      feedback.className = 'feedback good';
      feedback.textContent = '✓ Correct!';
      finish();
    } else {
      firstTry = false;
      markOption(buttons[i], 'wrong');
      buttons[i].disabled = true;
      feedback.className = 'feedback bad';
      feedback.textContent = '✗ Not quite — try again, or see the answer.';
      setHidden(showBtn, false);
    }
  }

  function reveal() {
    markOption(buttons[shown.indexOf(correct)], 'correct');
    feedback.className = 'feedback good';
    feedback.textContent = 'The correct answer is marked ✓.';
    finish();
  }

  return el('div', { 'class': 'q' },
    questionText(num, text, years, image),
    el('div', { 'class': 'options' }, buttons),
    feedback,
    noteEl,
    showBtn
  );
}

function answerParas(text) {
  return text.split('\n').map(function (p) { return el('p', {}, p); });
}

// q.or is an internal choice: { q, answer } asked as an alternative to the main question.
function renderOpen(num, q) {
  var answer = el('div', { 'class': 'answer' },
    answerParas(q.answer),
    q.or ? [el('p', { 'class': 'or' }, 'OR'), answerParas(q.or.answer)] : null,
    q.note ? el('p', { 'class': 'note' }, q.note) : null
  );
  setHidden(answer, true);

  var btn = el('button', {
    'class': 'btn',
    onclick: function () {
      setHidden(answer, !isHidden(answer));
      btn.textContent = isHidden(answer) ? 'Show answer' : 'Hide answer';
    }
  }, 'Show answer');

  return el('div', { 'class': 'q' },
    questionText(num, q.q, q.years, q.image),
    q.or ? [el('p', { 'class': 'or' }, 'OR'), el('p', { 'class': 'q-text' }, q.or.q)] : null,
    btn, answer);
}

// ---------- routing ----------

function route() {
  var parts = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  var subject = find(subjects, function (s) { return s.id === parts[0]; });
  var lesson = subject && parts[1]
    ? find(subject.lessons, function (l) { return String(l.no) === parts[1]; })
    : null;
  var view = parts[2];
  if (!subject) renderHome();
  else if (!lesson) renderSubject(subject);
  // Lessons with a text file get a menu; the views scroll once loaded.
  else if (lesson.text && view === 'text') return renderText(subject, lesson, 'text', false);
  else if (lesson.text && view === 'translation') return renderText(subject, lesson, 'text', true);
  else if (lesson.summary && view === 'summary') return renderText(subject, lesson, 'summary', false);
  else if (lesson.summary && view === 'summary-en') return renderText(subject, lesson, 'summary', true);
  else if ((lesson.text || lesson.summary) && view !== 'paper') renderLessonMenu(subject, lesson);
  else return renderPaper(subject, lesson);
  window.scrollTo(0, 0);
}

// Lesson texts kept only on this computer (local/ is not in git) are listed in local/texts.json.
function addLocalTexts(local) {
  subjects.forEach(function (s) {
    var texts = local[s.id] || {};
    s.lessons.forEach(function (l) {
      if (!l.text && texts[l.no]) l.text = texts[l.no];
    });
  });
}

loadJSON('data/subjects.json', function (data) {
  subjects = data.subjects;
  var start = function () {
    window.addEventListener('hashchange', route, false);
    route();
  };
  loadJSON('local/texts.json', function (local) { addLocalTexts(local); start(); }, start);
}, function () {
  showError(new Error('Could not load the question data. Open the app with start.bat (it needs a local web server).'));
});
