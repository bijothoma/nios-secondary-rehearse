"""Build the printable Malayalam model question paper 4 (PDF) in the layout of the April 2026 paper.

Usage:
  python tools/build_ml_pdf.py

Papers 1-3 are regenerated with the same seed as build_ml_papers.py so that paper 4 uses only questions they did not
use. Questions that refer to 'this lesson' are skipped (a printed paper has no lesson label). The answers (with the
keywords of the 3- and 5-mark answers) follow on separate pages. The HTML is printed to PDF with Microsoft Edge
(headless), which shapes Malayalam correctly. Output: downloads/malayalam-model-paper-4.pdf
"""
import html
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ml_papers as bp  # noqa: E402

APP = bp.APP_DIR
OUT = APP / 'downloads' / 'malayalam-model-paper-4.pdf'
EDGE = Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
CODE = 'MODEL/S/232/4/MM'
LETTERS = 'ABCD'

GENERAL = [
    'എല്ലാ ചോദ്യങ്ങൾക്കുമുള്ള ഉത്തരങ്ങൾ നിങ്ങൾക്ക് നൽകിയിരിക്കുന്ന ആൻസർ ബുക്കിൽ നൽകണം.',
    'ഈ ചോദ്യപേപ്പർ വായിക്കുന്നതിന് 15 മിനിറ്റ് സമയം അനുവദിച്ചിട്ടുണ്ട്. ഉച്ചക്ക് 02.15 ന് ചോദ്യപേപ്പർ നൽകും; '
    '02.15 മുതൽ 02.30 വരെ വിദ്യാർഥികൾ ചോദ്യപേപ്പർ വായിക്കുക മാത്രം ചെയ്യുക. ഈ സമയം ആൻസർ ബുക്കിൽ ഒരു '
    'ഉത്തരവും എഴുതാൻ പാടുള്ളതല്ല.',
    'പരീക്ഷാർഥികൾ അവരവരുടെ റോൾ നമ്പർ ചോദ്യപേപ്പറിന്റെ ആദ്യ പേജിൽ എഴുതേണ്ടതാണ്.',
    'ആദ്യ പേജിൽ പ്രിന്റ് ചെയ്തിരിക്കുന്ന വിവരങ്ങൾ അനുസരിച്ച് പേജുകളും ചോദ്യങ്ങളും ചോദ്യപേപ്പറിൽ '
    'അടങ്ങിയിട്ടുണ്ടോ എന്ന് പരിശോധിച്ച് ഉറപ്പ് വരുത്തേണ്ടതാണ്. കൂടാതെ ചോദ്യങ്ങൾ ക്രമമായി പ്രിന്റ് ചെയ്തിട്ടുണ്ടോ '
    'എന്നും ഉറപ്പ് വരുത്തേണ്ടതാണ്.',
    'ഒറ്റവാക്കിൽ ഉത്തരമെഴുതേണ്ട ചോദ്യങ്ങൾ (A), (B), (C), (D) എന്ന ക്രമത്തിൽ കൊടുത്തിട്ടുള്ള ഉത്തരങ്ങളിൽ '
    'നിന്നും ശരിയായ ഉത്തരം തെരഞ്ഞെടുത്ത് ഉത്തരപുസ്തകത്തിൽ എഴുതേണ്ടതാണ്.',
    'ഒറ്റവാക്കിൽ ഉത്തരമെഴുതേണ്ടതിൽ ഉൾപ്പെടെ എല്ലാ ചോദ്യങ്ങളുടെയും ഉത്തരം അനുവദിച്ചിരിക്കുന്ന സമയത്തിനുള്ളിൽ '
    'തന്നെ എഴുതേണ്ടതാണ്.',
    'ഉത്തരപുസ്തകത്തിൽ ഏതെങ്കിലും അടയാളങ്ങൾ ഇടുകയോ, നിശ്ചയിച്ചിരിക്കുന്ന സ്ഥാനത്തൊഴികെ ഉത്തരപുസ്തകത്തിന്റെ '
    'ഏതെങ്കിലും ഭാഗത്ത് റോൾ നമ്പർ എഴുതുകയോ ചെയ്യുന്നത് പരീക്ഷാർഥികളുടെ അയോഗ്യതയായി പരിഗണിക്കുന്നതാണ്.',
    'ഉത്തരപുസ്തകത്തിന്റെ പുറത്ത് ചോദ്യപേപ്പറിന്റെ കോഡ് നമ്പർ ' + CODE + ' എഴുതേണ്ടതാണ്.',
]

PAPER_INSTR = [
    ('(i)', 'എല്ലാ ചോദ്യങ്ങൾക്കും ഉത്തരം എഴുതണം.'),
    ('(ii)', 'ഒന്നു മുതൽ പതിനൊന്നുവരെയുള്ള ചോദ്യങ്ങൾക്ക് A, B, C, D എന്ന ക്രമത്തിൽ കൊടുത്തിരിക്കുന്നതിൽ നിന്നും '
             'ശരിയായത് എടുത്തെഴുതണം.'),
]

CSS = """
@page { size: A4; margin: 15mm 17mm 18mm 17mm;
  @bottom-left { content: 'CODEHERE'; font: 10pt 'Nirmala UI'; }
  @bottom-center { content: counter(page); font: 10pt 'Nirmala UI'; }
  @bottom-right { content: 'Model Paper 4'; font: 10pt 'Nirmala UI'; } }
body { font-family: 'Nirmala UI', 'Kartika', serif; font-size: 11.5pt; line-height: 1.35; color: #000; }
h1 { text-align: center; font-size: 20pt; margin: 4px 0; letter-spacing: 1px; }
.c { text-align: center; } .b { font-weight: bold; }
.row { display: flex; justify-content: space-between; border-top: 1.5px solid #000; border-bottom: 1.5px solid #000;
  padding: 4px 0; margin: 14px 0 10px; font-weight: bold; }
.sec { margin: 16px 0 6px; font-weight: bold; display: flex; justify-content: space-between; gap: 12px; break-after: avoid; }
.q { margin: 5px 0 5px 30px; text-indent: -30px; break-inside: avoid; }
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 20px; margin: 3px 0 0 18px; text-indent: 0; }
.opts.one { grid-template-columns: 1fr; }
.or { text-align: center; margin: 4px 0; }
.pb { break-before: page; }
.box { display: inline-block; width: 22px; height: 22px; border: 1px solid #000; vertical-align: middle; }
.cover td { padding: 3px 6px; } ol.gen { padding-left: 24px; font-size: 10.5pt; }
.ans { margin: 5px 0 5px 36px; text-indent: -36px; break-inside: avoid; }
.ans .k { margin-top: 3px; text-indent: 0; font-size: 10.5pt; border-left: 3px solid #555; padding-left: 6px; }
.ans p { margin: 3px 0 0 0; text-indent: 0; }
""".replace('CODEHERE', CODE)


def e(t):
    return html.escape(str(t))


def paper4():
    lessons = sorted((json.loads(p.read_text(encoding='utf-8')) for p in bp.DATA.glob('lesson-*.json')),
                     key=lambda l: l['lesson'])
    rng = random.Random(bp.SEED)
    used = set()
    for n in range(1, bp.PAPERS + 1):
        bp.build_paper(rng, lessons, used, n)
    # Paper 4: skip questions that need a lesson label to make sense.
    plain = bp.usable
    def usable4(no, q):
        if not plain(no, q):
            return False
        if no in (1, 3) and set(q.get('options', ())) == bp.TRUE_FALSE:
            return False  # true/false items belong to section 4 only
        return no == 3 or not bp.CONTEXT.search(q.get('q', ''))

    bp.usable = usable4
    secs = []
    for no, title, marks, count in bp.SECTIONS:
        if no == 10:
            mains = bp.pick(rng, lessons, 10, count, used)
            alts = bp.pick(rng, lessons, 10, count, used, avoid={l['lesson'] for l, _ in mains})
            qs = [dict(q, **{'or': a}) for (_, q), (_, a) in zip(mains, alts)]
        else:
            qs = [q for _, q in bp.pick(rng, lessons, no, count, used)]
        secs.append((no, title, marks, qs))
    return secs


def question_html(sec_no, i, q):
    num = f'{sec_no}.{i}'
    if sec_no == 4:
        return f'<div class="q">{num}. {e(q["q"])}</div>'
    if sec_no == 3:
        return (f'<div class="q">{num}. {e(q["q"])}'
                f'<div class="opts one">({e(", ".join(q["options"]))})</div></div>')
    if sec_no == 1:
        opts = ''.join(f'<div>({LETTERS[k]}) {e(o)}</div>' for k, o in enumerate(q['options']))
        long = any(len(o) > 28 for o in q['options'])
        return f'<div class="q">{num}. {e(q["q"])}<div class="opts{" one" if long else ""}">{opts}</div></div>'
    text = f'<div class="q">{num}. {e(q["q"])}</div>'
    if q.get('or'):
        text += ('<div class="or">അല്ലെങ്കിൽ</div><div class="q" style="margin-left:30px;text-indent:0">'
                 + e(q['or']['q']) + '</div>')
    return text


def paras(text):
    return ''.join(f'<p>{e(t)}</p>' for t in text.split('\n'))


def build_html(secs):
    out = [f'<html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head><body>']
    gen = ''.join(f'<li>{e(t)}</li>' for t in GENERAL)
    boxes = ''.join('<span class="box"></span>' for _ in range(9))
    instr = ''.join(f'<div style="margin-bottom:4px"><span style="display:inline-block;width:34px">{a}</span>{e(b)}</div>'
                    for a, b in PAPER_INSTR)
    out.append(f"""
<div style="text-align:right">This Question Paper consists of 10 questions.<br>
<span class="b">Code No. {CODE}</span></div>
<table class="cover"><tr><td class="b">Roll No.<br><span style="font-size:9pt">റോൾ നമ്പർ</span></td>
<td>{boxes}</td></tr></table>
<h1 style="margin-top:34px">MALAYALAM</h1><div class="c b" style="font-size:15pt">മലയാളം</div>
<div class="c b" style="font-size:20pt;margin:8px 0 30px">(232)</div>
<div class="b">Day and Date of Examination<br>(പരീക്ഷാ ദിവസവും തീയതിയും) ______________________________________</div>
<div class="b" style="margin-top:14px">Signature of Invigilators &nbsp; 1. ______________________________<br>
<span style="margin-left:150px">2. ______________________________</span></div>
<div class="b" style="border-top:1.5px solid #000;margin-top:14px;padding-top:6px">പൊതുവായ നിർദ്ദേശങ്ങൾ :</div>
<ol class="gen">{gen}</ol>
<div class="pb"></div>
<h1>MALAYALAM</h1><div class="c b" style="font-size:15pt">മലയാളം</div><div class="c b" style="font-size:20pt">(232)</div>
<div class="row"><span>സമയം : 3 മണിക്കൂർ]</span><span>[മാർക്ക് : 100</span></div>
<table><tr><td class="b" style="vertical-align:top;padding-right:16px;white-space:nowrap">നിർദ്ദേശങ്ങൾ :</td><td>{instr}</td></tr></table>""")
    for no, title, marks, qs in secs:
        out.append(f'<div class="sec"><span>{no}.&nbsp; {e(title)}</span>'
                   f'<span style="white-space:nowrap">[{e(marks)}]</span></div>')
        if no == 5:
            out.append('<table style="margin-left:24px">')
            for i, q in enumerate(qs, 1):
                out.append(f'<tr><td style="padding-right:26px">5.{i}. {e(q["left"])}</td><td>- {e(q["right"])}</td></tr>')
            out.append('</table>')
            continue
        for i, q in enumerate(qs, 1):
            out.append(question_html(no, i, q))
    out[-1] = '<div style="break-inside:avoid">' + out[-1] + '<div class="c" style="margin-top:14px">* * *</div></div>'
    out.append('<div class="pb"></div><h1>ഉത്തരസൂചിക</h1>'
               '<div class="c b">Answer Key — Model Paper 4 (Malayalam, 232)</div>')
    for no, title, marks, qs in secs:
        out.append(f'<div class="sec"><span>{no}.&nbsp; {e(title)}</span>'
                   f'<span style="white-space:nowrap">[{e(marks)}]</span></div>')
        for i, q in enumerate(qs, 1):
            num = f'{no}.{i}'
            if no in (1, 3, 4):
                ans = e(q['options'][LETTERS.index(q['answer'])])
                prefix = f'({q["answer"]}) ' if no == 1 else ''
                out.append(f'<div class="ans">{num}. {prefix}{ans}</div>')
            elif no == 5:
                out.append(f'<div class="ans">{num}. {e(q["left"])} - {e(q["right"])}</div>')
            elif no in (2, 6, 7):
                out.append(f'<div class="ans">{num}. {e(q["answer"].replace(chr(10), " "))}</div>')
            else:
                kw = (f'<div class="k"><b>Keywords:</b> {e(", ".join(q["keywords"]))}</div>'
                      if q.get('keywords') else '')
                out.append(f'<div class="ans">{num}. {paras(q["answer"])}{kw}</div>')
                if q.get('or'):
                    kw2 = (f'<div class="k"><b>Keywords:</b> {e(", ".join(q["or"]["keywords"]))}</div>'
                           if q['or'].get('keywords') else '')
                    out.append(f'<div class="or">അല്ലെങ്കിൽ</div>'
                               f'<div class="ans" style="margin-left:36px">{paras(q["or"]["answer"])}{kw2}</div>')
    out.append('</body></html>')
    return '\n'.join(out)


def main():
    secs = paper4()
    kw = {}
    for p in bp.DATA.glob('lesson-*.json'):
        for s in json.loads(p.read_text(encoding='utf-8'))['sections']:
            for q in s['questions']:
                if q.get('keywords'):
                    kw[q['answer']] = q['keywords']
    for _, _, _, qs in secs:
        for q in qs:
            if q['answer'] in kw:
                q['keywords'] = kw[q['answer']]
            if q.get('or') and q['or']['answer'] in kw:
                q['or']['keywords'] = kw[q['or']['answer']]
    OUT.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / 'paper.html'
        page.write_text(build_html(secs), encoding='utf-8')
        subprocess.run([str(EDGE), '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={OUT}', page.as_uri()], check=True, timeout=180)
    print('Wrote', OUT)


if __name__ == '__main__':
    main()
