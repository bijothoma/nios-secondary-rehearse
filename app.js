const app = document.getElementById('app');
const scoreEl = document.getElementById('score');
const LETTERS = 'ABCDEFGH';

let subjects = [];
let score = { right: 0, done: 0, total: 0 };

// ---------- helpers ----------

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c != null && c !== false) node.append(c);
  }
  return node;
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function loadJSON(path) {
  const res = await fetch(path, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Could not load ${path}`);
  return res.json();
}

function updateScore() {
  scoreEl.hidden = score.total === 0;
  scoreEl.textContent = `✔ ${score.right} / ${score.total}`;
}

// Marks per question, e.g. "10 × 2 = 20" → 2
function marksEach(section) {
  const m = section.marks.match(/[×x]\s*(\d+)/);
  return m ? Number(m[1]) : 1;
}

// ---------- pages ----------

function renderHome() {
  scoreEl.hidden = true;
  app.replaceChildren(
    el('h1', {}, 'Choose a subject'),
    el('div', { class: 'tiles' },
      subjects.map(s => el('a', { class: 'tile', href: `#/${s.id}` },
        el('strong', {}, s.label || s.name),
        el('span', {}, s.label ? s.name + ' · ' : '', lessonCount(s))
      ))
    )
  );
}

function lessonCount(s) {
  const n = s.lessons.length;
  return n === 0 ? 'Coming soon' : `${n} lesson${n > 1 ? 's' : ''}`;
}

function renderSubject(subject) {
  scoreEl.hidden = true;
  app.replaceChildren(
    el('div', { class: 'crumbs' }, el('a', { href: '#/' }, '← Subjects')),
    el('h1', {}, subject.label || subject.name),
    subject.lessons.length === 0
      ? el('p', { class: 'muted' }, 'No lessons added yet.')
      : el('div', { class: 'tiles' },
          subject.lessons.map(l => el('a', { class: 'tile', href: `#/${subject.id}/${l.no}` },
            el('span', {}, `Lesson ${l.no}`),
            el('strong', {}, l.title)
          ))
        )
  );
}

async function renderPaper(subject, lessonMeta) {
  const paper = await loadJSON(lessonMeta.file);
  score = { right: 0, done: 0, total: 0 };

  const head = el('div', { class: 'paper-head' },
    el('div', { class: 'crumbs' }, el('a', { href: `#/${subject.id}` }, `← ${subject.label || subject.name}`)),
    el('div', { class: 'muted' }, `Lesson ${paper.lesson}`),
    el('h1', {}, paper.title),
    paper.author && el('div', {}, paper.author),
    paper.meta && el('div', { class: 'muted' }, paper.meta),
    paper.instructions?.length && el('ul', {}, paper.instructions.map(t => el('li', {}, t))),
    el('div', { class: 'actions' },
      el('button', { class: 'btn', onclick: () => renderPaper(subject, lessonMeta) }, '↻ Shuffle & start again')
    )
  );

  const sections = paper.sections.map(sec => renderSection(sec, paper));
  const summary = el('div', { class: 'summary' },
    el('p', { id: 'summary-text' }),
    el('button', {
      class: 'btn primary',
      onclick: () => { renderPaper(subject, lessonMeta); window.scrollTo(0, 0); }
    }, '↻ Try again with a new shuffle')
  );

  app.replaceChildren(head, ...sections, summary);
  updateScore();
  updateSummary();
}

function updateSummary() {
  const t = document.getElementById('summary-text');
  if (!t) return;
  t.textContent = score.total
    ? `Choice questions: ${score.right} of ${score.total} right on the first try (${score.done} answered).`
    : '';
}

function renderSection(sec, paper) {
  const qs = shuffle(sec.questions);
  // Options for a "match" section are all the right-hand items of that section.
  const matchPool = sec.questions.filter(q => q.type === 'match').map(q => q.right);
  const each = marksEach(sec);

  return el('section', { class: 'section' },
    el('h2', {}, el('span', {}, `${sec.no}. ${sec.title}`), el('span', { class: 'marks' }, sec.marks)),
    sec.note && el('p', { class: 'note' }, sec.note),
    qs.map((q, i) => {
      const num = `${sec.no}.${i + 1}`;
      if (q.type === 'mcq') {
        const correct = q.options[LETTERS.indexOf(q.answer)];
        return renderChoice(num, q.q, q.year, q.options, correct, q.note);
      }
      if (q.type === 'match') {
        return renderChoice(num, `${q.left} — ?`, q.year, matchPool, q.right);
      }
      return renderOpen(num, q, each > 1 ? paper.answerNote : null);
    })
  );
}

function questionText(num, text, year) {
  return el('p', { class: 'q-text' },
    el('span', { class: 'q-num' }, num),
    text,
    year && el('span', { class: 'year', title: 'Asked in this exam' }, year)
  );
}

function renderChoice(num, text, year, options, correct, note) {
  score.total++;
  let firstTry = true;
  let finished = false;

  const feedback = el('p', { class: 'feedback' });
  const showBtn = el('button', { class: 'btn', onclick: reveal }, 'Show answer');
  showBtn.hidden = true;
  const noteEl = note ? el('p', { class: 'note' }, note) : null;
  if (noteEl) noteEl.hidden = true;

  const buttons = shuffle(options).map((opt, i) =>
    el('button', { class: 'opt', onclick: () => choose(i) },
      el('span', { class: 'letter' }, `(${LETTERS[i]})`),
      el('span', {}, opt)
    )
  );
  const shown = buttons.map(b => b.lastChild.textContent);

  function finish() {
    finished = true;
    buttons.forEach(b => (b.disabled = true));
    showBtn.hidden = true;
    if (noteEl) noteEl.hidden = false;
    score.done++;
    updateScore();
    updateSummary();
  }

  function choose(i) {
    if (finished) return;
    if (shown[i] === correct) {
      buttons[i].classList.add('correct');
      if (firstTry) score.right++;
      feedback.className = 'feedback good';
      feedback.textContent = firstTry ? 'Correct! 🎉' : 'Correct!';
      finish();
    } else {
      firstTry = false;
      buttons[i].classList.add('wrong');
      buttons[i].disabled = true;
      feedback.className = 'feedback bad';
      feedback.textContent = 'Not quite — try again, or see the answer.';
      showBtn.hidden = false;
    }
  }

  function reveal() {
    buttons[shown.indexOf(correct)].classList.add('correct');
    feedback.className = 'feedback good';
    feedback.textContent = 'The correct answer is highlighted.';
    finish();
  }

  return el('div', { class: 'q' },
    questionText(num, text, year),
    el('div', { class: 'options' }, buttons),
    feedback,
    noteEl,
    showBtn
  );
}

function renderOpen(num, q, note) {
  const answer = el('div', { class: 'answer' },
    q.answer.split('\n').map(p => el('p', {}, p)),
    q.note && el('p', { class: 'note' }, q.note),
    note && el('p', { class: 'note' }, note)
  );
  answer.hidden = true;

  const btn = el('button', {
    class: 'btn',
    onclick: () => {
      answer.hidden = !answer.hidden;
      btn.textContent = answer.hidden ? 'Show answer' : 'Hide answer';
    }
  }, 'Show answer');

  return el('div', { class: 'q' }, questionText(num, q.q, q.year), btn, answer);
}

// ---------- routing ----------

async function route() {
  const [subjectId, lessonNo] = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  const subject = subjects.find(s => s.id === subjectId);
  try {
    if (!subject) renderHome();
    else if (!lessonNo) renderSubject(subject);
    else {
      const lesson = subject.lessons.find(l => String(l.no) === lessonNo);
      if (lesson) await renderPaper(subject, lesson);
      else renderSubject(subject);
    }
  } catch (err) {
    app.replaceChildren(el('p', { class: 'feedback bad' }, err.message));
  }
  window.scrollTo(0, 0);
}

(async function init() {
  try {
    subjects = (await loadJSON('data/subjects.json')).subjects;
  } catch {
    app.replaceChildren(el('p', { class: 'feedback bad' },
      'Could not load the question data. Open the app with start.bat (it needs a local web server).'));
    return;
  }
  window.addEventListener('hashchange', route);
  route();
})();
