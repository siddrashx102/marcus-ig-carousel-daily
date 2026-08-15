# -*- coding: utf-8 -*-
"""
Reusable carousel slide HTML generator for @marcus.stoic.calm.
Ported from the proven post_08082026 (Mara) method, watermark fixed to Marcus.

Usage each run: fill SLIDES below with that day's content (8-10 slides,
Instagram's carousel cap is 10 images), then run this script to write
HTML files to ./html/slide_NN.html, then render each with:

  capture-website "html/slide_01.html" --output="slides/slide_01.png" --width=1080 --height=1350 --overwrite

Slide role guide (proven structure, from workflow_instagram_posting.md):
  1. Cover/hook      -> eyebrow + headline + sub
  2. Thesis/reframe   -> headline.small + statement
  3-N. Numbered list  -> number-badge + statement (one per point)
  N+1. Quote          -> quote-mark + quote-text + attribution (Marcus Aurelius / Epictetus / Seneca)
  N+2. Payoff         -> headline.small + sub
  N+3. Close/CTA      -> headline.small + cta-line + cta-strong (engagement question + save-CTA)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(HERE, "html")

BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:1080px; height:1350px;
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
  padding:110px 100px;
  text-align:center;
}
.eyebrow {
  font-family: Arial, 'Segoe UI', sans-serif;
  font-size:24px; letter-spacing:4px; text-transform:uppercase;
  color:#8C6E4F; margin-bottom:36px; font-weight:700;
}
.headline {
  font-size:64px; line-height:1.28; font-weight:700; color:#2B2A26;
}
.headline.small { font-size:52px; }
.sub {
  font-family: Arial, 'Segoe UI', sans-serif;
  font-size:30px; color:#5B584F; margin-top:28px; line-height:1.5;
}
.number-badge {
  width:110px; height:110px; border-radius:50%;
  background:#2B2A26; color:#F3EEE4;
  display:flex; align-items:center; justify-content:center;
  font-family: Arial, sans-serif; font-size:48px; font-weight:700;
  margin-bottom:48px;
}
.statement { font-size:52px; line-height:1.4; font-weight:700; }
.quote-mark {
  font-size:140px; color:#8C6E4F; line-height:0.5; margin-bottom:20px; font-family: Georgia, serif;
}
.quote-text { font-size:50px; line-height:1.45; font-style:italic; font-weight:600; }
.attribution {
  font-family: Arial, sans-serif; font-size:26px; color:#8C6E4F; margin-top:36px; letter-spacing:1px;
}
.cta-line { font-family: Arial, sans-serif; font-size:32px; color:#5B584F; margin-top:22px; line-height:1.6; }
.cta-strong { font-weight:700; color:#2B2A26; }
.watermark {
  position:absolute; bottom:48px; left:0; right:0;
  text-align:center; font-family: Arial, sans-serif; font-size:24px;
  letter-spacing:2px; color:#A79C86;
}
.pagenum {
  position:absolute; top:48px; right:56px;
  font-family: Arial, sans-serif; font-size:24px; color:#A79C86;
}
.rule { width:90px; height:4px; background:#8C6E4F; margin:34px 0; }
"""

WATERMARK = "@MARCUS.STOIC.CALM"

def wrap_html(body_inner, page, total):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>
<div class="pagenum">{page}/{total}</div>
<div class="wrap">
{body_inner}
</div>
<div class="watermark">{WATERMARK}</div>
</body></html>"""

# --- Fill this per run with that day's content (8-10 slides). Example shape below. ---
SLIDES = {
    1: """
<div class="eyebrow">EYEBROW LABEL</div>
<div class="headline">Hook headline<br>goes here</div>
<div class="rule"></div>
<div class="sub">Supporting sub-line</div>
""",
    # 2: thesis/reframe -> headline small + statement
    # 3..N: numbered list -> number-badge + statement, one per slide
    # N+1: quote -> quote-mark + quote-text + attribution
    # N+2: payoff -> headline small + sub
    # N+3: close -> headline small + cta-line + cta-strong
}

def build():
    total = len(SLIDES)
    os.makedirs(HTML_DIR, exist_ok=True)
    for page in sorted(SLIDES.keys()):
        html = wrap_html(SLIDES[page], page, total)
        path = os.path.join(HTML_DIR, f"slide_{page:02d}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

if __name__ == "__main__":
    build()
