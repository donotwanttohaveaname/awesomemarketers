#!/usr/bin/env python3
"""Build per-page OG cards (1200x630) for awesomemarketers.fi.

Concept: the community lives on Slack, so every card is a Slack moment.
A real community question, answered by the thing that page offers.

Usage:  python3 _og/build_og.py            # build all
        python3 _og/build_og.py events     # build one by slug
"""
import base64, os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og")
TMP = os.path.join(ROOT, "_og", "_tmp")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# slug, channel, the question a member asks, then the answer card
PAGES = [
 dict(slug="home", path="index.html", ch="general",
   q="wait, 1,787 marketers in one slack? how did i not know about this",
   title="The Awesome Marketers", big="1,787",
   meta="Finland's largest English-speaking marketing community. Since 2019, free, and volunteer run."),

 dict(slug="people", path="people/index.html", ch="introductions",
   q="who actually runs this place? 👀",
   title="The people behind it",
   meta="Volunteers, advisors, and the members who keep the community running."),

 dict(slug="manifesto", path="manifesto/index.html", ch="general",
   q="what does this community actually stand for?",
   title="Our manifesto", big="9",
   meta="Nine principles. Ethical marketing, fair pay, diversity, zero tolerance for harassment."),

 dict(slug="events", path="events/index.html", ch="events",
   q="anything worth going to in helsinki this month?",
   title="Marketing events in Finland",
   meta="Conferences, meetups, and workshops. Community-curated and updated regularly."),

 dict(slug="videos", path="videos/index.html", ch="resources",
   q="did anyone record that webinar? 🙏",
   title="Talks and webinars",
   meta="Free on YouTube. SEO, career pivots, salary negotiation, personal branding."),

 dict(slug="partners", path="partners/index.html", ch="tools",
   q="what tools do people here actually pay for?",
   title="Tools we use and recommend",
   meta="Picked by members, not by vendors. Some links keep the community free."),

 dict(slug="resources", path="resources/index.html", ch="resources",
   q="is there a list of everything you've built?",
   title="Everything we've built",
   meta="Salary data, career guides, calculators, and events. All free."),

 dict(slug="firstjob", path="firstjob/index.html", ch="jobs",
   q="moved to finland, zero luck landing a marketing job. help?",
   title="First marketing job guide",
   meta="Job boards, networking, salary data, unions, and advice from 1,787+ marketers."),

 dict(slug="freelance-calculator", path="freelance-calculator/index.html", ch="freelance",
   q="going freelance next month. what do i even charge?",
   title="Freelance rate calculator",
   meta="Your day and hour rate, with YEL, holiday pay, and the days you will not bill."),

 dict(slug="remote-salary-calculator", path="remote-salary-calculator/index.html", ch="freelance",
   q="a us company offered me a remote contract. is it actually a good deal?",
   title="Remote salary calculator",
   meta="What to ask for from Finland as self-employed, with YEL, holidays, and taxes covered."),

 dict(slug="marketing-salaries-finland", path="marketing-salaries-finland/index.html", ch="salaries",
   q="is there actual data on what marketers earn here, or just vibes?",
   title="Marketing salary reports",
   meta="Community survey data from 2021, 2023, and 2026. What marketers in Finland really earn."),

 dict(slug="marketing-salary-finland-2026", path="marketing-salary-finland-2026/index.html", ch="salaries",
   q="is €4,200 good for a mid-level marketer in helsinki? asking for me",
   title="Salary Report 2026", big="€4,658",
   meta="Median gross per month across 148 marketers. Pay by role, seniority, and the AI skills gap."),

 dict(slug="marketing-salary-finland-2026-report", path="marketing-salary-finland-2026-report/index.html", ch="salaries",
   q="can i just read the whole thing instead of clicking through charts?",
   title="The written report", big="148",
   meta="Every number from the 2026 survey in plain text. Median €4,658, pay by role, AI, remote work."),

 dict(slug="freelance-marketing-consultant-rates-finland", path="freelance-marketing-consultant-rates-finland/index.html", ch="freelance",
   q="what are people actually charging per day here? be honest",
   title="Freelance rates 2026", big="€520–650",
   meta="Per day for the median profile, €70 to €115 per hour ad-hoc. Calculated from real salary data."),

 dict(slug="marketing-freelancer-finland", path="marketing-freelancer-finland/index.html", ch="freelance",
   q="need a freelance marketer for a launch. where do i even look?",
   title="Hire a marketing freelancer",
   meta="Tell us the brief, we match you with the right person from the community. No fees, no cut."),

 dict(slug="awesome-meets", path="awesome-meets/index.html", ch="general",
   q="how do i meet marketers here without another mixer? 🙃",
   title="Awesome Autumn Meets", big="Round one",
   meta="Brand new format. Sign up by 28 Sep, get matched with 1 or 2 marketers by 2 Oct.",
   chips=["🥗 Lunch or after-work coffee", "📍 Helsinki", "🗓 Meet 12 to 30 Oct"]),
]

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
 *{margin:0;padding:0;box-sizing:border-box}
 body{width:1200px;height:630px;overflow:hidden;font-family:'Inter',system-ui,sans-serif;
   -webkit-font-smoothing:antialiased;
   background:
     radial-gradient(ellipse 55% 50% at 4% 0%, rgba(255,180,82,0.38), transparent 60%),
     radial-gradient(ellipse 60% 55% at 100% 100%, rgba(166,21,255,0.34), transparent 62%),
     #F7F5FA;}
 .win{position:absolute;left:52px;top:46px;right:52px;bottom:46px;background:#fff;
   border-radius:26px;box-shadow:0 24px 70px rgba(70,20,110,0.18),0 2px 8px rgba(0,0,0,0.05);
   overflow:hidden;display:flex;flex-direction:column}
 .bar{height:64px;flex:none;display:flex;align-items:center;gap:12px;padding:0 30px;
   border-bottom:1px solid #ECE9F1}
 .dots{display:flex;gap:7px;margin-right:6px}
 .dots i{width:11px;height:11px;border-radius:50%;display:block}
 .ch{font-family:'Space Grotesk';font-weight:700;font-size:23px;color:#171717;letter-spacing:-0.01em}
 .ch b{color:#A3A3A3;font-weight:600;margin-right:1px}
 .mem{margin-left:auto;font-size:16px;font-weight:600;color:#737373}
 .body{flex:1;padding:26px 34px;display:flex;flex-direction:column;justify-content:center}
 .msg{display:flex;gap:16px}
 .av{width:52px;height:52px;border-radius:14px;flex:none;display:flex;align-items:center;
   justify-content:center;font-size:27px;background:TINT}
 .who{font-family:'Space Grotesk';font-weight:700;font-size:18px;color:#171717;margin-bottom:5px}
 .who em{font-style:normal;font-weight:500;color:#A3A3A3;font-size:15px;margin-left:9px}
 .q{font-size:29px;line-height:1.34;color:#1F1F1F;font-weight:400;max-width:930px}
 .ans{margin-top:26px;display:flex;gap:16px}
 .card{flex:1;min-width:0;border:1px solid #EAE6EF;border-left:6px solid transparent;
   border-radius:14px;padding:20px 26px 22px;background:#fff;
   background-image:linear-gradient(#fff,#fff),linear-gradient(160deg,#FFB452,#A615FF);
   background-origin:border-box;background-clip:padding-box,border-box;
   box-shadow:0 6px 18px rgba(70,20,110,0.07)}
 .src{display:flex;align-items:center;gap:9px;margin-bottom:9px}
 .src img{width:25px;height:25px;border-radius:7px;display:block}
 .src span{font-family:'Space Grotesk';font-weight:600;font-size:16px;color:#6B6B6B;letter-spacing:0.01em}
 .t{font-family:'Space Grotesk';font-weight:700;font-size:TSIZEpx;line-height:1.1;
   letter-spacing:-0.028em;color:#171717;margin-bottom:BGAPpx}
 .big{font-family:'Space Grotesk';font-weight:700;font-size:62px;line-height:1;letter-spacing:-0.035em;
   background:linear-gradient(135deg,#F0912B,#A615FF);-webkit-background-clip:text;
   background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
 .m{font-size:19px;line-height:1.45;color:#404040;max-width:880px}
 .chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
 .chip{padding:5px 14px;border-radius:999px;background:#F6F3FA;border:1px solid #EDE8F3;
   font-size:16px;font-weight:600;color:#262626}
 .foot{flex:none;height:66px;display:flex;align-items:center;gap:10px;padding:0 34px;
   border-top:1px solid #F2EFF6}
 .rx{display:flex;gap:8px}
 .rx i{font-style:normal;padding:5px 13px;border-radius:999px;background:#F6F3FA;
   border:1px solid #EDE8F3;font-size:17px}
 .url{margin-left:auto;display:flex;align-items:center;gap:9px}
 .url img{width:27px;height:27px;border-radius:8px;display:block}
 .url span{font-family:'Space Grotesk';font-weight:600;font-size:18px;color:#171717}
</style></head><body>
<div class="win">
 <div class="bar">
  <div class="dots"><i style="background:#FFB452"></i><i style="background:#E86A9A"></i><i style="background:#A615FF"></i></div>
  <div class="ch"><b>#</b>CHANNEL</div>
  <div class="mem">1,787 members</div>
 </div>
 <div class="body">
  <div class="msg">
   <div class="av">EMOJI</div>
   <div style="min-width:0">
    <div class="who">a member<em>TIME</em></div>
    <div class="q">QUESTION</div>
   </div>
  </div>
  <div class="ans">
   <div style="width:52px;flex:none"></div>
   <div class="card">
    <div class="src"><img src="LOGO"><span>The Awesome Marketers</span></div>
    BIG<div class="t">TITLE</div>
    <div class="m">META</div>CHIPS
   </div>
  </div>
 </div>
 <div class="foot">
  <div class="rx"><i>👀</i><i>🔥</i><i>🙌</i></div>
  <div class="url"><img src="LOGO"><span>awesomemarketers.fi</span></div>
 </div>
</div></body></html>"""

AV = [("#FFE9CB", "🙋"), ("#F4E5FF", "💬"), ("#DDE6BD", "🤔"), ("#FBD9E5", "👋"),
      ("#E3F0FB", "🧐"), ("#FFF0D6", "✍️"), ("#EFE7FD", "🙂")]
TIMES = ["9:14", "10:02", "11:37", "13:20", "14:45", "16:08", "17:31"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(p, i, logo_uri):
    tint, emoji = AV[i % len(AV)]
    big = ""
    tsize, bgap = 34, 10
    if p.get("big"):
        big = f'<div class="big">{esc(p["big"])}</div>'
        tsize, bgap = 27, 8
    chips = ""
    if p.get("chips"):
        chips = '<div class="chips">' + "".join(f'<span class="chip">{esc(c)}</span>' for c in p["chips"]) + "</div>"
    return (TPL.replace("CHIPS", chips).replace("CHANNEL", esc(p["ch"])).replace("TINT", tint)
            .replace("EMOJI", emoji).replace("TIME", TIMES[i % len(TIMES)])
            .replace("QUESTION", esc(p["q"])).replace("BIG", big)
            .replace("TSIZE", str(tsize)).replace("BGAP", str(bgap))
            .replace("TITLE", esc(p["title"])).replace("META", esc(p["meta"]))
            .replace("LOGO", logo_uri))


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
