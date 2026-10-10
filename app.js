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

// Marks per question, e.g. "10 × 2 = 20" → 2
function marksEach(section) {
  var m = section.marks.match(/[×x]\s*(\d+)/);
  return m ? Number(m[1]) : 1;
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
              el('span', {}, 'Lesson ' + l.no),
              el('strong', {}, l.title)
            );
          })
        )
  );
}

function renderPaper(subject, lessonMeta) {
  loadJSON(lessonMeta.file, function (paper) {
    score = { right: 0, done: 0, total: 0 };
    var restart = function () { renderPaper(subject, lessonMeta); };

    var head = el('div', { 'class': 'paper-head' },
      el('div', { 'class': 'crumbs' }, el('a', { href: '#/' + subject.id }, '« ' + (subject.label || subject.name))),
      el('div', { 'class': 'muted' }, 'Lesson ' + paper.lesson),
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

    var sections = paper.sections.map(function (sec) { return renderSection(sec, paper); });
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

function renderSection(sec, paper) {
  var qs = shuffle(sec.questions);
  // Options for a "match" section are all the right-hand items of that section.
  var matchPool = sec.questions
    .filter(function (q) { return q.type === 'match'; })
    .map(function (q) { return q.right; });
  var each = marksEach(sec);

  return el('div', { 'class': 'section' },
    el('h2', {}, el('span', {}, sec.no + '. ' + sec.title), el('span', { 'class': 'marks' }, sec.marks)),
    sec.note ? el('p', { 'class': 'note' }, sec.note) : null,
    qs.map(function (q, i) {
      var num = sec.no + '.' + (i + 1);
      if (q.type === 'mcq') {
        var correct = q.options[LETTERS.indexOf(q.answer)];
        return renderChoice(num, q.q, q.year, q.options, correct, q.note);
      }
      if (q.type === 'match') {
        return renderChoice(num, q.left + ' — ?', q.year, matchPool, q.right);
      }
      return renderOpen(num, q, each > 1 ? paper.answerNote : null);
    })
  );
}

function questionText(num, text, year) {
  return el('p', { 'class': 'q-text' },
    el('span', { 'class': 'q-num' }, num),
    text,
    year ? el('span', { 'class': 'year', title: 'Asked in this exam' }, year) : null
  );
}

// Marks an option as right or wrong with a symbol as well as a style, so it reads
// on greyscale (e-ink) screens where green and red look the same.
function markOption(button, kind) {
  addClass(button, kind);
  button.appendChild(el('span', { 'class': 'mark' }, kind === 'correct' ? '✓' : '✗'));
}

function renderChoice(num, text, year, options, correct, note) {
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
    questionText(num, text, year),
    el('div', { 'class': 'options' }, buttons),
    feedback,
    noteEl,
    showBtn
  );
}

function renderOpen(num, q, note) {
  var answer = el('div', { 'class': 'answer' },
    q.answer.split('\n').map(function (p) { return el('p', {}, p); }),
    q.note ? el('p', { 'class': 'note' }, q.note) : null,
    note ? el('p', { 'class': 'note' }, note) : null
  );
  setHidden(answer, true);

  var btn = el('button', {
    'class': 'btn',
    onclick: function () {
      setHidden(answer, !isHidden(answer));
      btn.textContent = isHidden(answer) ? 'Show answer' : 'Hide answer';
    }
  }, 'Show answer');

  return el('div', { 'class': 'q' }, questionText(num, q.q, q.year), btn, answer);
}

// ---------- routing ----------

function route() {
  var parts = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  var subject = find(subjects, function (s) { return s.id === parts[0]; });
  var lesson = subject && parts[1]
    ? find(subject.lessons, function (l) { return String(l.no) === parts[1]; })
    : null;
  if (!subject) renderHome();
  else if (lesson) return renderPaper(subject, lesson); // scrolls once loaded
  else renderSubject(subject);
  window.scrollTo(0, 0);
}

loadJSON('data/subjects.json', function (data) {
  subjects = data.subjects;
  window.addEventListener('hashchange', route, false);
  route();
}, function () {
  showError(new Error('Could not load the question data. Open the app with start.bat (it needs a local web server).'));
});
