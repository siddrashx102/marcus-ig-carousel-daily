# -*- coding: utf-8 -*-
"""
Pinterest carousel slide HTML generator for @marcus.stoic.calm's Pinterest
strategy (see ../01_competitor_breakdown.md through ../04_30_day_publishing_plan.md).

Same visual system as the Instagram carousel template (../../Instagram/carousel_template/
build_slides.py) for cross-platform brand consistency, resized to Pinterest's
recommended pin ratio: 1000x1500 (2:3), not Instagram's 1080x1350 (4:5).

Usage: fill/extend the PINS dict below (one entry per pin, each with its own
slide list), run this script -> writes HTML to
./html/<slug>/slide_NN.html, then render each with:

  capture-website "html/<slug>/slide_01.html" --output="slides/<slug>/slide_01.png" \
    --width=1000 --height=1500 --overwrite --launch-options='{"args":["--no-sandbox"]}'

Slide role guide (mirrors the Instagram template's proven structure):
  1. Cover/hook       -> eyebrow + headline + sub + save-cta footer
  2. Thesis/reframe    -> headline.small + statement
  3-N. Numbered list   -> number-badge + statement (one per point)
  N+1. Quote           -> quote-mark + quote-text + attribution
  N+2. Payoff          -> headline.small + sub
  N+3. Close/CTA       -> headline.small + cta-line + cta-strong
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(HERE, "html")

BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:1000px; height:1500px;
  background:#F3EEE4;
  font-family: Georgia, 'Times New Roman', serif;
  color:#2B2A26;
  position:relative;
  overflow:hidden;
}
.wrap {
  width:100%; height:100%;
  display:flex; flex-direction:column;
  justify-content:center; align-items:center;
  padding:130px 90px;
  text-align:center;
}
.eyebrow {
  font-family: Arial, 'Segoe UI', sans-serif;
  font-size:24px; letter-spacing:4px; text-transform:uppercase;
  color:#8C6E4F; margin-bottom:40px; font-weight:700;
}
.headline {
  font-size:66px; line-height:1.28; font-weight:700; color:#2B2A26;
}
.headline.small { font-size:54px; }
.sub {
  font-family: Arial, 'Segoe UI', sans-serif;
  font-size:30px; color:#5B584F; margin-top:30px; line-height:1.55;
}
.number-badge {
  width:112px; height:112px; border-radius:50%;
  background:#2B2A26; color:#F3EEE4;
  display:flex; align-items:center; justify-content:center;
  font-family: Arial, sans-serif; font-size:48px; font-weight:700;
  margin-bottom:50px;
}
.statement { font-size:52px; line-height:1.42; font-weight:700; }
.quote-mark {
  font-size:150px; color:#8C6E4F; line-height:0.5; margin-bottom:22px; font-family: Georgia, serif;
}
.quote-text { font-size:50px; line-height:1.48; font-style:italic; font-weight:600; }
.attribution {
  font-family: Arial, sans-serif; font-size:26px; color:#8C6E4F; margin-top:38px; letter-spacing:1px;
}
.cta-line { font-family: Arial, sans-serif; font-size:32px; color:#5B584F; margin-top:24px; line-height:1.6; }
.cta-strong { font-weight:700; color:#2B2A26; }
.save-cta {
  position:absolute; bottom:96px; left:0; right:0;
  text-align:center; font-family: Arial, sans-serif; font-size:26px; font-weight:700;
  letter-spacing:1px; color:#8C6E4F;
}
.watermark {
  position:absolute; bottom:48px; left:0; right:0;
  text-align:center; font-family: Arial, sans-serif; font-size:24px;
  letter-spacing:2px; color:#A79C86;
}
.pagenum {
  position:absolute; top:56px; right:60px;
  font-family: Arial, sans-serif; font-size:24px; color:#A79C86;
}
.rule { width:90px; height:4px; background:#8C6E4F; margin:36px 0; }
.badge-num-row { display:flex; align-items:center; gap:10px; }
"""

WATERMARK = "@MARCUS.STOIC.CALM"

def wrap_html(body_inner, page, total, save_cta=None):
    save_html = f'<div class="save-cta">{save_cta}</div>' if save_cta else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>
<div class="pagenum">{page}/{total}</div>
<div class="wrap">
{body_inner}
</div>
{save_html}
<div class="watermark">{WATERMARK}</div>
</body></html>"""

# --- One entry per pin. Each pin's SLIDES dict follows the same role guide
# as the Instagram template. save_cta (optional) only renders on slide 1. ---
PINS = {

    "pin_01_7_stoic_habits": {
        "save_cta": "SAVE THIS FOR YOUR MORNING ROUTINE",
        "slides": {
            1: """
<div class="eyebrow">STOIC HABITS</div>
<div class="headline">7 Stoic Habits<br>for an Unshakable Mind</div>
<div class="rule"></div>
<div class="sub">Simple daily practices, straight from Marcus Aurelius</div>
""",
            2: """
<div class="headline small">Discipline isn't a personality trait.</div>
<div class="sub">It's a set of small habits, repeated daily until they hold you steady on the hard days too.</div>
""",
            3: """
<div class="number-badge">1</div>
<div class="statement">Read one page of Stoic writing before you check your phone.</div>
""",
            4: """
<div class="number-badge">2</div>
<div class="statement">Name what's in your control today &mdash; and let the rest go.</div>
""",
            5: """
<div class="number-badge">3</div>
<div class="statement">Do the hard task first, while your discipline is freshest.</div>
""",
            6: """
<div class="number-badge">4</div>
<div class="statement">Journal one line each night on what tested you.</div>
""",
            7: """
<div class="number-badge">5</div>
<div class="statement">Sit with discomfort for 60 seconds before reacting to it.</div>
""",
            8: """
<div class="quote-mark">&ldquo;</div>
<div class="quote-text">You have power over your mind &mdash; not outside events. Realize this, and you will find strength.</div>
<div class="attribution">MARCUS AURELIUS</div>
""",
            9: """
<div class="headline small">Save this list.</div>
<div class="cta-line">Which habit are you starting with?</div>
<div class="cta-line cta-strong">Comment below &mdash; then save this pin so you can come back to it tomorrow.</div>
""",
        },
    },

    "pin_02_free_stoic_journal": {
        "save_cta": "TAP TO DOWNLOAD THE FREE JOURNAL",
        "slides": {
            1: """
<div class="eyebrow">FREE DOWNLOAD</div>
<div class="headline">The 7-Day<br>Stoic Reset Journal</div>
<div class="rule"></div>
<div class="sub">A free printable PDF &mdash; one page a day, one week to a calmer mind</div>
""",
            2: """
<div class="headline small">Stuck in a mental maze of racing thoughts?</div>
<div class="sub">This journal gives you one Stoic principle, one prompt, and one small action &mdash; every day for a week.</div>
""",
            3: """
<div class="number-badge">DAY 1&ndash;2</div>
<div class="statement">Name the pattern. See where overthinking is actually running the show.</div>
""",
            4: """
<div class="number-badge">DAY 3&ndash;5</div>
<div class="statement">Reframe it. Learn the dichotomy of control and let go of what was never yours to carry.</div>
""",
            5: """
<div class="number-badge">DAY 6&ndash;7</div>
<div class="statement">Take action. Build one real discipline habit you keep after the week ends.</div>
""",
            6: """
<div class="quote-mark">&ldquo;</div>
<div class="quote-text">He who fears death will never do anything worthy of a person who is alive.</div>
<div class="attribution">SENECA</div>
""",
            7: """
<div class="headline small">Get your free copy.</div>
<div class="cta-line">Tap the link on this pin to download the</div>
<div class="cta-line cta-strong">7-Day Stoic Reset Journal &mdash; free PDF, delivered instantly.</div>
""",
        },
    },

    "pin_03_dichotomy_of_control": {
        "save_cta": "SAVE THIS BEFORE YOUR NEXT STRESSFUL DAY",
        "slides": {
            1: """
<div class="eyebrow">STOIC PRINCIPLE</div>
<div class="headline">The Dichotomy<br>of Control</div>
<div class="rule"></div>
<div class="sub">How to stop stressing over things you can't change</div>
""",
            2: """
<div class="headline small">Every situation splits into two piles.</div>
<div class="sub">Most of your stress comes from mixing them up.</div>
""",
            3: """
<div class="number-badge">IN&nbsp;YOUR<br>CONTROL</div>
<div class="statement">Your effort, your reactions, your choices, your focus.</div>
""",
            4: """
<div class="number-badge">NOT&nbsp;IN<br>CONTROL</div>
<div class="statement">Other people's opinions, outcomes, the past, what happens next.</div>
""",
            5: """
<div class="headline small">The Stoic move:</div>
<div class="sub">Pour your energy into pile one. Release pile two &mdash; on purpose, every time you notice yourself gripping it.</div>
""",
            6: """
<div class="quote-mark">&ldquo;</div>
<div class="quote-text">Man is disturbed not by things, but by the views he takes of them.</div>
<div class="attribution">EPICTETUS</div>
""",
            7: """
<div class="headline small">Save this before your next stressful day.</div>
<div class="cta-line cta-strong">Which pile have you been mixing up lately?</div>
""",
        },
    },

}

def build():
    for slug, pin in PINS.items():
        slides = pin["slides"]
        save_cta = pin.get("save_cta")
        total = len(slides)
        out_dir = os.path.join(HTML_DIR, slug)
        os.makedirs(out_dir, exist_ok=True)
        for page in sorted(slides.keys()):
            cta = save_cta if page == 1 else None
            html = wrap_html(slides[page], page, total, save_cta=cta)
            path = os.path.join(out_dir, f"slide_{page:02d}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print("wrote", path)

if __name__ == "__main__":
    build()
