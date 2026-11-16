"""रोज़ 12 राशियों के अलग पेज बनाता है: docs/rashifal/<rashi>.html
GitHub Action इसे हर रात 12:15 बजे (भारत समय) चलाता है। सर्वर से जवाब न आए तो पुराने पेज वैसे ही रहते हैं।"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://alliswell-server.onrender.com"
SITE = "https://alliswellrashfal.com"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "rashifal")
IST = timezone(timedelta(hours=5, minutes=30))
MONTHS = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]

RASHIS = [  # (हिंदी, slug, English, Roman, symbol, नाम अक्षर)
    ("मेष", "mesh", "Aries", "Mesh", "♈", "चू, चे, चो, ला, ली, लू, ले, लो, अ"),
    ("वृषभ", "vrishabh", "Taurus", "Vrishabh", "♉", "इ, उ, ए, ओ, वा, वी, वू, वे, वो"),
    ("मिथुन", "mithun", "Gemini", "Mithun", "♊", "का, की, कू, घ, ङ, छ, के, को, ह"),
    ("कर्क", "kark", "Cancer", "Kark", "♋", "ही, हू, हे, हो, डा, डी, डू, डे, डो"),
    ("सिंह", "singh", "Leo", "Singh", "♌", "मा, मी, मू, मे, मो, टा, टी, टू, टे"),
    ("कन्या", "kanya", "Virgo", "Kanya", "♍", "टो, पा, पी, पू, ष, ण, ठ, पे, पो"),
    ("तुला", "tula", "Libra", "Tula", "♎", "रा, री, रू, रे, रो, ता, ती, तू, ते"),
    ("वृश्चिक", "vrishchik", "Scorpio", "Vrishchik", "♏", "तो, ना, नी, नू, ने, नो, या, यी, यू"),
    ("धनु", "dhanu", "Sagittarius", "Dhanu", "♐", "ये, यो, भा, भी, भू, धा, फा, ढा, भे"),
    ("मकर", "makar", "Capricorn", "Makar", "♑", "भो, जा, जी, खी, खू, खे, खो, गा, गी"),
    ("कुंभ", "kumbh", "Aquarius", "Kumbh", "♒", "गू, गे, गो, सा, सी, सू, से, सो, दा"),
    ("मीन", "meen", "Pisces", "Meen", "♓", "दी, दू, थ, झ, ञ, दे, दो, चा, ची"),
]
PERIODS = [("aaj", "आज का राशिफल"), ("saptah", "साप्ताहिक राशिफल"), ("mahina", "मासिक राशिफल")]


def get(path, tries=6):
    url = API + path
    if os.environ.get("MOCK"):
        return json.load(open(os.environ["MOCK"], encoding="utf-8"))
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "aiwr-pages"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            print("दोबारा कोशिश:", path, e)
            time.sleep(20)
    return None


def esc(s):
    return (str(s or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


CSS = """:root{--red:#b3121f;--maroon:#7a1e2c;--deep:#4a0f19;--gold:#f3c97a;--gold2:#e0a63a;--cream:#fffaf2;--ink:#231713;--muted:#6b5a4e;--line:#eadfcf}
*{box-sizing:border-box}body{margin:0;font-family:'Mukta','Noto Sans Devanagari',system-ui,sans-serif;background:var(--cream);color:var(--ink);font-size:18px;line-height:1.7}a{color:var(--red)}
.mast{background:#fff;border-bottom:4px solid var(--red)}.mast .w{max-width:900px;margin:auto;padding:12px 16px;display:flex;align-items:center;gap:12px}
.mast img{width:56px;height:56px;border-radius:50%;border:3px solid var(--gold2);object-fit:cover}.mast b{font-size:24px;color:var(--red);display:block;line-height:1.1}.mast small{color:var(--muted)}
nav{background:var(--red)}nav .w{max-width:900px;margin:auto;display:flex;overflow-x:auto}nav a{color:#fff;text-decoration:none;padding:10px 14px;font-weight:700;font-size:16px;white-space:nowrap}
main{max-width:900px;margin:20px auto;padding:0 16px}.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-bottom:16px}
h1{color:var(--maroon);margin:0 0 4px;font-size:28px;line-height:1.3}h2{color:var(--red);font-size:22px;margin:14px 0 6px}.sub{color:var(--muted);font-size:15px}
.sym{font-size:46px;float:right;color:var(--gold2);line-height:1}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0}
.facts div{background:#fff3dc;border:1px solid var(--gold2);border-radius:10px;padding:8px 12px}.facts b{display:block;color:var(--deep);font-size:15px}
.st{display:grid;grid-template-columns:1fr 1fr;gap:4px 18px;font-size:16px}.st span{color:#e0a63a;letter-spacing:2px}
.rl{display:flex;flex-wrap:wrap;gap:8px}.rl a{background:#fff;border:1px solid var(--line);border-radius:20px;padding:5px 12px;text-decoration:none;font-weight:700}
.btn{display:inline-block;background:#1a6b43;color:#fff;text-decoration:none;padding:10px 18px;border-radius:10px;font-weight:800;margin:6px 6px 0 0}.btn.red{background:var(--red)}
footer{background:var(--deep);color:#f5e6d6;margin-top:24px;padding:18px 16px;font-size:15px;text-align:center}footer a{color:var(--gold);margin:0 8px;text-decoration:none}"""


def shell(title, desc, canon, body, ld):
    return f"""<!DOCTYPE html>
<html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-20R9EGZKVE"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-20R9EGZKVE");</script>
<link rel="canonical" href="{canon}"><link rel="icon" href="../favicon.png">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{SITE}/og.jpg"><meta property="og:url" content="{canon}">
<link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style></head><body>
<div class="mast"><div class="w"><img src="../favicon.png" alt="पंडित राजू पाठक"><div><b>All Is Well Rashifal</b><small>पंडित राजू पाठक • राशिफल • गोचर • पंचांग</small></div></div></div>
<nav><div class="w"><a href="/">होम</a><a href="index.html">सभी राशियाँ</a><a href="/#kundli-banayen">मुफ़्त कुंडली</a><a href="/#milan">कुंडली मिलान</a><a href="/#gochar">ग्रह गोचर</a><a href="/#panchang">पंचांग</a></div></nav>
<main>{body}</main>
<footer>© All Is Well Rashifal – पंडित राजू पाठक, झाँसी • 📞 8815605282<br>
<a href="../about.html">हमारे बारे में</a><a href="../privacy.html">प्राइवेसी पॉलिसी</a><a href="../disclaimer.html">अस्वीकरण</a><a href="../contact.html">संपर्क</a></footer>
</body></html>"""


HL = ' style="background:#fff3dc"'


def rashi_links(cur=None):
    return '<div class="rl">' + "".join(
        f'<a href="{s}.html"{HL if s == cur else ""}>{sym} {h}</a>' for h, s, e, ro, sym, ak in RASHIS) + "</div>"


def stars(lst):
    return '<div class="st">' + "".join(f'<div>{esc(x["name"])} <span>{"★" * int(x["value"])}{"☆" * (5 - int(x["value"]))}</span></div>' for x in lst or []) + "</div>"


def main():
    now = datetime.now(IST)
    dh = f"{now.day} {MONTHS[now.month - 1]} {now.year}"
    de = f"{now.day} {MONTHS_EN[now.month - 1]} {now.year}"
    iso = now.strftime("%Y-%m-%d")
    data = {}
    for h, s, *_ in RASHIS:
        data[s] = {}
        for p, _ in PERIODS:
            r = get(f"/rashifal/{urllib.parse.quote(h)}?period={p}")
            if not r or not r.get("text"):
                if p == "aaj":
                    print("सर्वर से राशिफल नहीं मिला, पुराने पेज रहने दिए:", h)
                    sys.exit(0)
            data[s][p] = r or {}
    os.makedirs(OUT, exist_ok=True)

    for h, s, en, ro, sym, ak in RASHIS:
        a = data[s]["aaj"]
        title = f"{h} राशिफल आज {dh} | Aaj Ka {ro} Rashifal – {en} Horoscope Today"
        desc = f"आज का {h} राशिफल {dh} ({DAYS[now.weekday()]}): करियर, प्रेम, सेहत, धन, शुभ अंक, शुभ रंग और उपाय – पंडित राजू पाठक, All Is Well Rashifal।"
        body = f"""<div class="card"><span class="sym">{sym}</span><h1>{h} राशिफल आज – {dh}</h1>
<div class="sub">{DAYS[now.weekday()]} • {ro} Rashifal Today • {en} Horoscope {de} • नाम अक्षर: {ak}</div>
<h2>आज का {h} राशिफल</h2><p>{esc(a.get('text'))}</p>
<div class="facts"><div><b>💼 करियर</b>{esc(a.get('career'))}</div><div><b>💞 प्रेम</b>{esc(a.get('prem'))}</div><div><b>🩺 सेहत</b>{esc(a.get('swasthya'))}</div><div><b>💰 धन</b>{esc(a.get('dhan'))}</div>
<div><b>🔢 शुभ अंक</b>{esc(a.get('shubh_ank'))}</div><div><b>🎨 शुभ रंग</b>{esc(a.get('shubh_rang'))}</div>{f'<div><b>⏰ शुभ समय</b>{esc(a.get("best_time"))}</div>' if a.get('best_time') else ''}{f'<div><b>⚠️ सावधानी</b>{esc(a.get("caution_time"))}</div>' if a.get('caution_time') else ''}</div>
{stars(a.get('stars'))}
<h2>आज का उपाय</h2><p>{esc(a.get('upay'))}</p></div>"""
        for p, ph in PERIODS[1:]:
            t = data[s].get(p, {}).get("text")
            if t:
                body += f'<div class="card"><h2>{h} {ph}</h2><p>{esc(t)}</p></div>'
        body += f"""<div class="card"><h2>{en} Horoscope Today ({de})</h2><p>Daily {en} ({ro}) horoscope by Pandit Raju Pathak. Lucky number: {esc(a.get('shubh_ank'))}. The detailed prediction above is in Hindi.</p>
<h2>अपनी कुंडली से सटीक भविष्य</h2><p>राशिफल सामान्य होता है। अपनी जन्म-कुंडली के अनुसार सटीक जानकारी के लिए पंडित राजू पाठक से पूरी कुंडली रिपोर्ट (₹2100) बनवाएँ।</p>
<a class="btn red" href="/#kundli-banayen">मुफ़्त कुंडली बनाएँ</a><a class="btn" href="https://wa.me/918815605282">WhatsApp पर पूछें</a></div>
<div class="card"><h2>दूसरी राशियों का आज का राशिफल</h2>{rashi_links(s)}</div>"""
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"{h} राशिफल आज {dh}", "datePublished": now.isoformat(),
              "dateModified": now.isoformat(), "inLanguage": "hi", "author": {"@type": "Person", "name": "पंडित राजू पाठक"},
              "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
              "image": f"{SITE}/og.jpg", "mainEntityOfPage": f"{SITE}/rashifal/{s}.html"}
        open(os.path.join(OUT, f"{s}.html"), "w", encoding="utf-8").write(shell(title, desc, f"{SITE}/rashifal/{s}.html", body, ld))

    cards = "".join(f'<div class="card"><h2><a href="{s}.html" style="text-decoration:none">{sym} {h} राशिफल ({en})</a></h2><p>{esc((data[s]["aaj"].get("text") or "")[:180])}… <a href="{s}.html">पूरा पढ़ें →</a></p></div>'
                    for h, s, en, ro, sym, ak in RASHIS)
    body = f'<div class="card"><h1>आज का राशिफल – {dh}</h1><div class="sub">{DAYS[now.weekday()]} • Aaj Ka Rashifal • Horoscope Today {de} • पंडित राजू पाठक</div>{rashi_links()}</div>{cards}'
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"आज का राशिफल {dh}", "url": f"{SITE}/rashifal/"}
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell(f"आज का राशिफल {dh} – मेष से मीन तक | Aaj Ka Rashifal – All Is Well Rashifal",
              f"आज का राशिफल {dh}: मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ और मीन राशि का दैनिक राशिफल – पंडित राजू पाठक।",
              f"{SITE}/rashifal/", body, ld))

    urls = [("", "daily"), ("rashifal/", "daily")] + [(f"rashifal/{s}.html", "daily") for _, s, *_ in RASHIS] + \
           [("lekh/", "weekly")] + [("lekh/" + f, "monthly") for f in sorted(os.listdir(os.path.join(ROOT, "docs", "lekh"))) if f.endswith(".html") and f != "index.html"] * os.path.isdir(os.path.join(ROOT, "docs", "lekh")) + \
           [(u, "monthly") for u in ("about.html", "contact.html", "privacy.html", "disclaimer.html", "terms.html")]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{SITE}/{u}</loc><lastmod>{iso}</lastmod><changefreq>{c}</changefreq></url>\n" for u, c in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "docs", "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print("बन गए:", len(RASHIS), "राशि पेज", dh)


if __name__ == "__main__":
    main()
