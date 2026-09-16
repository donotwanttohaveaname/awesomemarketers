#!/usr/bin/env python3
"""Build per-page OG cards (1200x630) for awesomemarketers.fi.

Concept: the community lives on Slack, so every card is a Slack moment.
A real community question, answered by what that page offers.

Design rule: Slack, LinkedIn and X shrink a link preview to roughly 200px
wide. So the card is a Slack window zoomed in, not a full screenshot: short
question, and one big focal line in the answer that still reads when tiny.
Keep `q` under ~46 characters and `big` under ~18.

Usage:  python3 _og/build_og.py            # build all
        python3 _og/build_og.py events     # build one by slug
"""
import base64, os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og")
TMP = os.path.join(ROOT, "_og", "_tmp")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MEMBERS = "1,823"

PAGES = [
 dict(slug="home", path="index.html", ch="general",
   q="wait, there are 1,823 of us in here?",
   big=MEMBERS, line="Finland's largest marketing community. Free, since 2019."),

 dict(slug="people", path="people/index.html", ch="introductions",
   q="who actually runs this place? 👀",
   big="Who we are", line="Volunteers, advisors, and the members who keep it going."),

 dict(slug="manifesto", path="manifesto/index.html", ch="general",
   q="what does this community stand for?",
   big="9 principles", line="Fair pay, ethics, diversity, zero harassment."),

 dict(slug="events", path="events/index.html", ch="events",
   q="anything worth going to this month?",
   big="What's on", line="Marketing events in Finland, community-curated."),

 dict(slug="videos", path="videos/index.html", ch="resources",
   q="did anyone record that webinar? 🙏",
   big="Talks on tap", line="Every session, free on YouTube. No sign-up."),

 dict(slug="partners", path="partners/index.html", ch="tools",
   q="what tools does everyone here use?",
   big="Tools we use", line="Picked by members, not by vendors."),

 dict(slug="resources", path="resources/index.html", ch="resources",
   q="what have you all built so far?",
   big="The lot", line="Salary data, guides, calculators, events. All free."),

 dict(slug="firstjob", path="firstjob/index.html", ch="jobs",
   q="moved to finland. how do i get hired?",
   big="First job?", line="Job boards, networking, salary data, unions."),

 dict(slug="freelance-calculator", path="freelance-calculator/index.html", ch="freelance",
   q="going freelance. what do i charge?",
   big="What to charge", line="Your day and hour rate, after YEL and holiday pay."),

 dict(slug="remote-salary-calculator", path="remote-salary-calculator/index.html", ch="freelance",
   q="remote contract from abroad. good deal?",
   big="Do the maths", line="What to ask for as self-employed in Finland."),

 dict(slug="marketing-salaries-finland", path="marketing-salaries-finland/index.html", ch="salaries",
   q="is there real data on what we earn?",
   big="Salary data", line="What marketers in Finland earn, since 2021."),

 dict(slug="marketing-salary-finland-2026", path="marketing-salary-finland-2026/index.html", ch="salaries",
   q="is €4,200 good for a mid-level marketer?",
   big="€4,658", line="Median marketing salary in Finland, 2026. 148 marketers."),

 dict(slug="marketing-salary-finland-2026-report", path="marketing-salary-finland-2026-report/index.html",
   ch="salaries", q="can i just read the whole thing?",
   big="€4,658", line="The full 2026 salary report, in plain text."),

 dict(slug="freelance-marketing-consultant-rates-finland",
   path="freelance-marketing-consultant-rates-finland/index.html", ch="freelance",
   q="what are people charging per day?",
   big="€520–650", line="What freelance marketers charge per day in Finland."),

 dict(slug="marketing-freelancer-finland", path="marketing-freelancer-finland/index.html", ch="freelance",
   q="need a freelance marketer. where do i look?",
   big="We'll match you", line=f"From {MEMBERS} marketers. Free, no fees, no cut."),

 dict(slug="awesome-meets", path="awesome-meets/index.html", ch="general",
   q="how do i meet people without another mixer? 🙃",
   big="Round one", line="Get matched with 1 or 2 marketers in Helsinki.",
   chips=["🗓 Sign up by 28 Sep", "🥗 Lunch or coffee", "📍 Helsinki"]),
]

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
 *{margin:0;padding:0;box-sizing:border-box}
 body{width:1200px;height:630px;overflow:hidden;font-family:'Inter',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
  background:
   radial-gradient(ellipse 55% 55% at 2% -6%, rgba(255,159,69,0.52), transparent 62%),
   radial-gradient(ellipse 60% 62% at 101% 104%, rgba(166,21,255,0.40), transparent 62%),
   #FFFCF9;}
 .win{position:absolute;left:44px;top:40px;right:44px;bottom:40px;background:#fff;
  border-radius:28px;box-shadow:0 26px 74px rgba(88,26,133,0.20),0 2px 8px rgba(0,0,0,.05);
  overflow:hidden;display:flex;flex-direction:column}
 .bar{height:74px;flex:none;display:flex;align-items:center;gap:13px;padding:0 34px;
  border-bottom:1px solid #EFECF4}
 .dots{display:flex;gap:8px;margin-right:5px}
 .dots i{width:13px;height:13px;border-radius:50%;display:block}
 .ch{font-family:'Space Grotesk';font-weight:700;font-size:28px;color:#141414;letter-spacing:-.02em}
 .ch b{color:#B9B4C2;font-weight:600}
 .mem{margin-left:auto;font-size:19px;font-weight:600;color:#8A8A90}
 .body{flex:1;padding:20px 36px;display:flex;flex-direction:column;justify-content:center}
 .msg{display:flex;gap:18px;align-items:flex-start}
 .av{width:60px;height:60px;border-radius:16px;flex:none;display:flex;align-items:center;
  justify-content:center;font-size:32px;background:TINT}
 .who{font-family:'Space Grotesk';font-weight:700;font-size:20px;color:#8A8A90;margin-bottom:7px}
 .q{font-family:'Space Grotesk';font-weight:600;font-size:QSIZEpx;line-height:1.24;color:#141414;
  letter-spacing:-.022em;max-width:960px}
 .ans{margin-top:18px;padding-left:78px}
 .card{border:1px solid #EDE8F2;border-left:7px solid transparent;border-radius:18px;
  padding:18px 30px 20px;background:#fff;
  background-image:linear-gradient(#fff,#fff),linear-gradient(165deg,#FF9F45,#F2588B 55%,#A615FF);
  background-origin:border-box;background-clip:padding-box,border-box;
  box-shadow:0 8px 22px rgba(88,26,133,.08)}
 .src{display:flex;align-items:center;gap:10px;margin-bottom:10px}
 .src img{width:26px;height:26px;border-radius:7px;display:block}
 .src span{font-family:'Space Grotesk';font-weight:600;font-size:19px;color:#8A8A90}
 .big{font-family:'Space Grotesk';font-weight:700;font-size:BSIZEpx;line-height:1.0;
  letter-spacing:-.045em;padding-bottom:4px;
  background:linear-gradient(112deg,#E8841B 4%,#E0439A 50%,#9B12EC 92%);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
 .line{margin-top:10px;font-family:'Space Grotesk';font-weight:600;font-size:27px;line-height:1.3;
  color:#33313A;letter-spacing:-.015em;max-width:900px}
 .chips{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}
 .chips i{font-style:normal;padding:8px 16px;border-radius:999px;background:#FAF7FD;
  border:1.5px solid #ECE5F4;font-family:'Space Grotesk';font-weight:600;font-size:19px;color:#3A3742}
 .foot{flex:none;height:66px;display:flex;align-items:center;gap:10px;padding:0 34px;
  border-top:1px solid #F4F1F8}
 .rx{display:flex;gap:9px}
 .rx i{font-style:normal;padding:6px 15px;border-radius:999px;background:#F7F4FB;
  border:1px solid #EEE9F5;font-size:20px}
 .url{margin-left:auto;display:flex;align-items:center;gap:10px}
 .url img{width:30px;height:30px;border-radius:9px;display:block}
 .url span{font-family:'Space Grotesk';font-weight:700;font-size:21px;color:#141414}
</style></head><body>
<div class="win">
 <div class="bar">
  <div class="dots"><i style="background:#FF9F45"></i><i style="background:#F2588B"></i><i style="background:#A615FF"></i></div>
  <div class="ch"><b>#</b>CHANNEL</div><div class="mem">MEMBERS members</div>
 </div>
 <div class="body">
  <div class="msg"><div class="av">EMOJI</div>
   <div style="min-width:0"><div class="who">a member</div><div class="q">QUESTION</div></div>
  </div>
  <div class="ans"><div class="card">
   <div class="src"><img src="LOGO"><span>The Awesome Marketers</span></div>
   <div class="big">BIG</div><div class="line">LINE</div>CHIPS
  </div></div>
 </div>
 <div class="foot">
  <div class="rx"><i>👀</i><i>🔥</i><i>🙌</i></div>
  <div class="url"><img src="LOGO"><span>awesomemarketers.fi</span></div>
 </div>
</div></body></html>"""

AV = [("#FFE9CB", "🙋"), ("#F4E5FF", "💬"), ("#DDE6BD", "🤔"), ("#FBD9E5", "👋"),
      ("#E3F0FB", "🧐"), ("#FFF0D6", "✍️"), ("#EFE7FD", "🙂")]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(p, i, logo_uri):
    tint, emoji = AV[i % len(AV)]
    n = len(p["big"])
    bs = 104 if n <= 6 else 90 if n <= 9 else 80 if n <= 12 else 70
    qs = 42 if len(p["q"]) <= 40 else 38
    chips = ""
    if p.get("chips"):
        chips = '<div class="chips">' + "".join(f"<i>{esc(c)}</i>" for c in p["chips"]) + "</div>"
    return (TPL.replace("CHANNEL", esc(p["ch"])).replace("MEMBERS", MEMBERS).replace("TINT", tint)
            .replace("EMOJI", emoji).replace("QSIZE", str(qs)).replace("QUESTION", esc(p["q"]))
            .replace("BSIZE", str(bs)).replace("BIG", esc(p["big"]))
            .replace("LINE", esc(p["line"])).replace("CHIPS", chips).replace("LOGO", logo_uri))


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    with open(os.path.join(ROOT, "logo.jpg"), "rb") as f:
        logo_uri = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    built = []
    for i, p in enumerate(PAGES):
        if only and p["slug"] != only:
            continue
        hp = os.path.join(TMP, p["slug"] + ".html")
        with open(hp, "w") as f:
            f.write(build(p, i, logo_uri))
        png = os.path.join(OUT, p["slug"] + ".png")
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        f"--screenshot={png}", "--window-size=1200,630",
                        "--default-background-color=FFFFFFFF",
                        "--virtual-time-budget=6000", "file://" + hp],
                       capture_output=True, timeout=90)
        built.append((p["slug"], os.path.exists(png)))
    shutil.rmtree(TMP, ignore_errors=True)
    for slug, ok in built:
        print(("OK  " if ok else "FAIL") + f" og/{slug}.png")


if __name__ == "__main__":
    main()
