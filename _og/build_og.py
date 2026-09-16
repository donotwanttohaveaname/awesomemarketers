#!/usr/bin/env python3
"""Build per-page OG cards (1200x630) for awesomemarketers.fi.

Designed to survive being shrunk: Slack, LinkedIn and X often render a link
preview thumbnail around 200px wide. So every card is one dominant focal
line plus one short supporting line, centred, on the community gradient.
Anything smaller than the supporting line is decoration only.

Usage:  python3 _og/build_og.py            # build all
        python3 _og/build_og.py events     # build one by slug
"""
import base64, os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og")
TMP = os.path.join(ROOT, "_og", "_tmp")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MEMBERS = "1,823"

# big  = the one thing readable at thumbnail size (keep it under ~18 chars)
# line = one short supporting line (keep it under ~50 chars)
# chips = decoration, never load-bearing
PAGES = [
 dict(slug="home", path="index.html", ch="general", big=MEMBERS,
   line="Finland's largest marketing community",
   chips=["Free to join", "Since 2019", "On Slack"]),

 dict(slug="people", path="people/index.html", ch="introductions", big="Who we are",
   line="Volunteers, advisors, and the members who run it"),

 dict(slug="manifesto", path="manifesto/index.html", ch="general", big="9 principles",
   line="Fair pay, ethics, diversity, zero harassment"),

 dict(slug="events", path="events/index.html", ch="events", big="What's on",
   line="Marketing events in Finland, community-curated",
   chips=["Conferences", "Meetups", "Workshops"]),

 dict(slug="videos", path="videos/index.html", ch="resources", big="Talks & webinars",
   line="Free on YouTube, no sign-up",
   chips=["SEO", "Career pivots", "Salary negotiation"]),

 dict(slug="partners", path="partners/index.html", ch="tools", big="Tools we use",
   line="Picked by members, not by vendors"),

 dict(slug="resources", path="resources/index.html", ch="resources", big="Everything we built",
   line="Salary data, guides, calculators, events. All free.",
   chips=["Salary data", "Guides", "Calculators"]),

 dict(slug="firstjob", path="firstjob/index.html", ch="jobs", big="First job?",
   line="How to land marketing work in Finland",
   chips=["Job boards", "Networking", "Salary data", "Unions"]),

 dict(slug="freelance-calculator", path="freelance-calculator/index.html", ch="freelance",
   big="What to charge", line="Your freelance day and hour rate, after YEL",
   chips=["YEL pension", "Holiday pay", "Billable days"]),

 dict(slug="remote-salary-calculator", path="remote-salary-calculator/index.html", ch="freelance",
   big="Paid from abroad?", line="What to ask for as self-employed in Finland",
   chips=["YEL", "Holidays", "Taxes"]),

 dict(slug="marketing-salaries-finland", path="marketing-salaries-finland/index.html", ch="salaries",
   big="Salary data", line="What marketers in Finland earn, since 2021",
   chips=["2026", "2023", "2021"]),

 dict(slug="marketing-salary-finland-2026", path="marketing-salary-finland-2026/index.html", ch="salaries",
   big="€4,658", line="Median marketing salary in Finland, 2026",
   chips=["148 marketers", "Pay by role", "AI skills gap"]),

 dict(slug="marketing-salary-finland-2026-report", path="marketing-salary-finland-2026-report/index.html",
   ch="salaries", big="€4,658", line="The full 2026 salary report, in plain text",
   chips=["148 marketers", "74% hit by cuts", "Every number"]),

 dict(slug="freelance-marketing-consultant-rates-finland",
   path="freelance-marketing-consultant-rates-finland/index.html", ch="freelance",
   big="€520–650", line="What freelance marketers charge per day",
   chips=["€70–115 / hour", "16 specialisations"]),

 dict(slug="marketing-freelancer-finland", path="marketing-freelancer-finland/index.html", ch="freelance",
   big="Need a freelancer?", line=f"We match you from {MEMBERS} marketers",
   chips=["Free", "No fees", "No cut"]),

 dict(slug="awesome-meets", path="awesome-meets/index.html", ch="general", big="Round one",
   line="Get matched with 1 or 2 marketers in Helsinki",
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
   radial-gradient(ellipse 58% 60% at 2% -8%, rgba(255,180,82,0.55), transparent 60%),
   radial-gradient(ellipse 62% 65% at 102% 106%, rgba(166,21,255,0.42), transparent 60%),
   #FFFDFB;}
 .edge{position:absolute;top:0;left:0;right:0;height:12px;
  background:linear-gradient(90deg,#FFB452,#E8628F,#A615FF)}
 .wrap{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;padding:60px 70px 54px}
 .top{display:flex;align-items:center;gap:13px}
 .top img{width:40px;height:40px;border-radius:11px;display:block}
 .top b{font-family:'Space Grotesk';font-weight:700;font-size:23px;color:#171717;letter-spacing:-0.01em}
 .top i{font-style:normal;font-family:'Space Grotesk';font-weight:600;font-size:20px;
  color:#8B5CF6;background:rgba(166,21,255,0.10);padding:6px 15px;border-radius:999px;margin-left:5px}
 .mid{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-align:center;width:100%}
 .big{font-family:'Space Grotesk';font-weight:700;font-size:BIGSIZEpx;line-height:1.0;
  letter-spacing:-0.042em;
  background:linear-gradient(118deg,#E8841B 8%,#E0439A 52%,#9B12EC 92%);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  padding-bottom:6px}
 .line{margin-top:20px;font-family:'Space Grotesk';font-weight:600;font-size:LINESIZEpx;
  line-height:1.26;color:#1A1A1A;letter-spacing:-0.018em;max-width:960px}
 .chips{display:flex;gap:11px;flex-wrap:wrap;justify-content:center;min-height:46px;align-items:center}
 .chip{padding:10px 21px;border-radius:999px;background:rgba(255,255,255,0.86);
  border:1.5px solid rgba(23,23,23,0.10);font-family:'Space Grotesk';font-weight:600;
  font-size:21px;color:#2C2C2C}
</style></head><body>
<div class="edge"></div>
<div class="wrap">
 <div class="top"><img src="LOGO"><b>awesomemarketers.fi</b><i>#CHANNEL</i></div>
 <div class="mid"><div class="big">BIG</div><div class="line">LINE</div></div>
 <div class="chips">CHIPS</div>
</div></body></html>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def big_size(s):
    n = len(s)
    return 168 if n <= 6 else 146 if n <= 9 else 128 if n <= 12 else 112 if n <= 15 else 98 if n <= 18 else 86


def build(p, logo_uri):
    line = p.get("line", "")
    chips = "".join(f'<div class="chip">{esc(c)}</div>' for c in p.get("chips", []))
    return (TPL.replace("BIGSIZE", str(big_size(p["big"])))
            .replace("LINESIZE", "46" if len(line) <= 46 else "41")
            .replace("BIG", esc(p["big"])).replace("LINE", esc(line))
            .replace("CHIPS", chips).replace("CHANNEL", esc(p["ch"]))
            .replace("LOGO", logo_uri))


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    with open(os.path.join(ROOT, "logo.jpg"), "rb") as f:
        logo_uri = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    built = []
    for p in PAGES:
        if only and p["slug"] != only:
            continue
        hp = os.path.join(TMP, p["slug"] + ".html")
        with open(hp, "w") as f:
            f.write(build(p, logo_uri))
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
