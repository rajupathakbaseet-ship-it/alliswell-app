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
.mast{background:#fff;border-bottom:4px solid var(--red)}.mast .w{max-width:1180px;margin:auto;padding:12px 16px;display:flex;align-items:center;gap:12px}
.mast img{width:56px;height:56px;border-radius:50%;border:3px solid var(--gold2);object-fit:cover}.mast b{font-size:24px;color:var(--red);display:block;line-height:1.1}.mast small{color:var(--muted)}
nav{background:var(--red)}nav .w{max-width:1180px;margin:auto;display:flex;overflow-x:auto}nav a{color:#fff;text-decoration:none;padding:10px 14px;font-weight:700;font-size:16px;white-space:nowrap}
main{min-width:0}.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-bottom:16px}
h1{color:var(--maroon);margin:0 0 4px;font-size:28px;line-height:1.3}h2{color:var(--red);font-size:22px;margin:14px 0 6px}.sub{color:var(--muted);font-size:15px}
.sym{font-size:46px;float:right;color:var(--gold2);line-height:1}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0}
.facts div{background:#fff3dc;border:1px solid var(--gold2);border-radius:10px;padding:8px 12px}.facts b{display:block;color:var(--deep);font-size:15px}
.st{display:grid;grid-template-columns:1fr 1fr;gap:4px 18px;font-size:16px}.st span{color:#e0a63a;letter-spacing:2px}
.rl{display:flex;flex-wrap:wrap;gap:8px}.rl a{background:#fff;border:1px solid var(--line);border-radius:20px;padding:5px 12px;text-decoration:none;font-weight:700}
.btn{display:inline-block;background:#1a6b43;color:#fff;text-decoration:none;padding:10px 18px;border-radius:10px;font-weight:800;margin:6px 6px 0 0}.btn.red{background:var(--red)}
.lay{max-width:1180px;margin:16px auto;padding:0 16px;display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:18px;align-items:start}aside{position:sticky;top:10px}
@media(max-width:980px){.lay{grid-template-columns:1fr}aside{position:static}}
.rb{background:linear-gradient(180deg,#8f1420,#b3121f);padding:8px 0 10px}.rb .w{max-width:1180px;margin:auto;display:flex;gap:6px;overflow-x:auto;padding:0 12px;scrollbar-width:none}.rb .w::-webkit-scrollbar{display:none}
.rb a{flex:1 0 64px;text-align:center;color:#fff;text-decoration:none;font-size:14px;font-weight:700;line-height:1.2}.rb a i{display:flex;align-items:center;justify-content:center;width:46px;height:46px;margin:0 auto 3px;border-radius:50%;background:#fff;color:var(--red);font-style:normal;font-size:26px;border:2px solid var(--gold)}.rb a.on i{background:var(--gold);color:var(--deep)}
.bc{font-size:14px;color:var(--muted);margin:0 0 8px}.bc a{color:var(--muted);text-decoration:none}.bc a:hover{color:var(--red)}.bc span{margin:0 6px}
.meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;color:var(--muted);font-size:15px;margin:6px 0 10px;padding:8px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.meta b{color:var(--deep)}
.shr{display:flex;gap:6px;margin-left:auto}.shr a,.shr button{width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:#fff;text-decoration:none;font-weight:800;font-size:15px;border:0;cursor:pointer;font-family:inherit}
.shr .wa{background:#25d366}.shr .fb{background:#1877f2}.shr .tw{background:#111}.shr .tg{background:#2aa1da}.shr .cp{background:#7a1e2c}
.sum{background:#fff3dc;border-left:5px solid var(--gold2);border-radius:10px;padding:10px 14px;margin:10px 0;font-weight:600}.sum b{color:var(--red)}
.svc{background:linear-gradient(160deg,#7a1e2c,#b3121f);color:#fff;border-radius:14px;padding:16px;margin-bottom:16px}.svc h3{margin:0;font-size:22px;color:var(--gold)}.svc p{margin:2px 0 10px;font-size:14px;color:#f8e3d0}
.svg{display:grid;grid-template-columns:1fr 1fr;gap:8px}.svg a{background:#fff;color:var(--deep);border-radius:12px;padding:10px 8px;text-decoration:none;text-align:center;font-weight:800;font-size:15px;line-height:1.25}.svg a i{display:block;font-style:normal;font-size:28px;margin-bottom:2px}.svg a small{display:block;color:var(--red);font-size:13px;margin-top:2px}
.svc .go{display:block;text-align:center;background:var(--gold);color:var(--deep);border-radius:22px;padding:9px;margin-top:10px;font-weight:800;text-decoration:none}
.side{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin-bottom:16px}.side h3{margin:0 0 8px;color:var(--maroon);font-size:19px}.side a.ln{display:block;padding:7px 0;border-bottom:1px dashed var(--line);text-decoration:none;font-weight:700;font-size:16px}
footer{background:var(--deep);color:#f5e6d6;margin-top:24px;padding:18px 16px;font-size:15px;text-align:center}footer a{color:var(--gold);margin:0 8px;text-decoration:none}"""


def wa(t):
    return "https://wa.me/918815605282?text=" + urllib.parse.quote(t)


SVC = {"hi": [("📜", "जन्म कुंडली रिपोर्ट", "₹2100", "नमस्ते पंडित जी, मुझे पूरी कुंडली रिपोर्ट (₹2100) बनवानी है।"),
              ("💑", "कुंडली मिलान", "गुण-दोष", "नमस्ते पंडित जी, मुझे कुंडली मिलान करवाना है।"),
              ("💍", "विवाह भविष्य", "शादी कब", "नमस्ते पंडित जी, मुझे अपने विवाह के बारे में पूछना है।"),
              ("💼", "करियर-नौकरी", "सही समय", "नमस्ते पंडित जी, मुझे करियर और नौकरी के बारे में पूछना है।"),
              ("🪐", "शनि साढ़ेसाती", "उपाय", "नमस्ते पंडित जी, मुझे शनि साढ़ेसाती के बारे में पूछना है।"),
              ("🐍", "राहु-केतु दोष", "उपाय", "नमस्ते पंडित जी, मुझे राहु-केतु दोष के बारे में पूछना है।")],
       "en": [("📜", "Full Kundli Report", "₹2100", "Namaste Pandit ji, I want a full kundli report (₹2100)."),
              ("💑", "Kundli Matching", "Guna milan", "Namaste Pandit ji, I want kundli matching."),
              ("💍", "Marriage Prediction", "When to marry", "Namaste Pandit ji, I want to ask about my marriage."),
              ("💼", "Career & Job", "Right timing", "Namaste Pandit ji, I want to ask about my career."),
              ("🪐", "Shani Sade Sati", "Remedies", "Namaste Pandit ji, I want to ask about Sade Sati."),
              ("🐍", "Rahu-Ketu Dosha", "Remedies", "Namaste Pandit ji, I want to ask about Rahu-Ketu dosha.")]}
TXT = {"hi": dict(nav=[("/", "होम"), ("/rashifal/", "आज का राशिफल"), ("/rashifal/saptahik.html", "साप्ताहिक राशिफल"), ("/rashifal/masik.html", "मासिक राशिफल"),
                       ("/rashifal/love.html", "लव राशिफल"), ("/rashifal/ank-jyotish.html", "अंक ज्योतिष"), ("/lekh/", "राशिफल 2027 और लेख"), ("/web-stories/", "वेब स्टोरी"), ("/#kundli-banayen", "मुफ़्त कुंडली"), ("/#milan", "कुंडली मिलान"), ("/#panchang", "पंचांग")],
                  svc="ज्योतिष सेवाएं", svcp="पंडित राजू पाठक से सीधे WhatsApp पर बात करें", go="WhatsApp पर पूछें →",
                  free="मुफ़्त सुविधाएँ", fl=[("/#kundli-banayen", "🔯 मुफ़्त कुंडली बनाएँ"), ("/#milan", "💑 मुफ़्त कुंडली मिलान"), ("/rashifal/", "♈ आज का राशिफल"), ("/#sadesati", "🪐 साढ़ेसाती जाँचें"), ("/#muhurat", "📅 शुभ मुहूर्त")],
                  home="होम", by="लेखक", upd="अपडेट", share="शेयर करें", tr="🔥 ट्रेंडिंग",
                  trl=[("/rashifal/", "आज का राशिफल – मेष से मीन तक"), ("/rashifal/love.html", "आज का लव राशिफल ❤️"), ("/rashifal/ank-jyotish.html", "आज का अंक राशिफल (मूलांक 1-9)"),
                       ("/rashifal/saptahik.html", "साप्ताहिक राशिफल"), ("/lekh/rahu-ketu-gochar-5-december-2026.html", "5 दिसंबर राहु-केतु गोचर: 12 राशियों पर असर"),
                       ("/lekh/shani-sadesati-dhaiya-2026-2027.html", "शनि साढ़ेसाती-ढैय्या 2026-27"), ("/lekh/", "राशिफल 2027 – सभी 12 राशियाँ")]),
       "en": dict(nav=[("/", "Home"), ("/en/lekh/", "Horoscope 2027 & Articles"), ("/rashifal/", "Daily Horoscope (Hindi)"), ("/#kundli-banayen", "Free Kundli"), ("/#milan", "Kundli Matching"), ("/#panchang", "Panchang")],
                  svc="Astrology Services", svcp="Talk to Pandit Raju Pathak directly on WhatsApp", go="Ask on WhatsApp →",
                  free="Free Tools", fl=[("/#kundli-banayen", "🔯 Free Kundli"), ("/#milan", "💑 Free Kundli Matching"), ("/#sadesati", "🪐 Check Sade Sati"), ("/#muhurat", "📅 Shubh Muhurat")],
                  home="Home", by="By", upd="Updated", share="Share", tr="🔥 Trending",
                  trl=[("/en/lekh/", "Horoscope 2027 – all 12 signs"), ("/en/lekh/mesh-rashifal-2027.html", "Aries Horoscope 2027"), ("/en/lekh/vrishchik-rashifal-2027.html", "Scorpio Horoscope 2027"), ("/web-stories/", "Web Stories")])}


def rashi_bar(cur=None, lang="hi"):
    return '<div class="rb"><div class="w">' + "".join(
        f'<a href="/rashifal/{s}.html"{" class=on" if s == cur else ""}><i>{sym}</i>{h if lang == "hi" else e}</a>' for h, s, e, ro, sym, ak in RASHIS) + "</div></div>"


def aside(lang="hi"):
    T = TXT[lang]
    g = "".join(f'<a href="{wa(m)}" target="_blank" rel="noopener"><i>{ic}</i>{n}<small>{sm}</small></a>' for ic, n, sm, m in SVC[lang])
    fl = "".join(f'<a class="ln" href="{u}">{n}</a>' for u, n in T["fl"])
    return (f'<div class="svc"><h3>🔯 {T["svc"]}</h3><p>{T["svcp"]}</p><div class="svg">{g}</div>'
            f'<a class="go" href="{wa(SVC[lang][0][3])}" target="_blank" rel="noopener">{T["go"]}</a></div>'
            f'<div class="side"><h3>{T["tr"]}</h3>' + "".join(f'<a class="ln" href="{u}">{n}</a>' for u, n in T["trl"]) + '</div>'
            f'<div class="side"><h3>{T["free"]}</h3>{fl}</div>')


def crumbs(items, lang="hi"):
    """items: [(नाम, url या None)] – होम अपने आप जुड़ता है।"""
    allc = [(TXT[lang]["home"], SITE + "/")] + list(items)
    html = '<div class="bc">' + '<span>›</span>'.join(f'<a href="{u}">{esc(n)}</a>' if u else esc(n) for n, u in allc) + "</div>"
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        dict({"@type": "ListItem", "position": k + 1, "name": n}, **({"item": u} if u else {})) for k, (n, u) in enumerate(allc)]}
    return html, ld


def share(url, title, lang="hi"):
    t = urllib.parse.quote(title + " " + url)
    u = urllib.parse.quote(url)
    return (f'<span class="shr" aria-label="{TXT[lang]["share"]}"><a class="wa" href="https://wa.me/?text={t}" target="_blank" rel="noopener" title="WhatsApp">W</a>'
            f'<a class="fb" href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener" title="Facebook">f</a>'
            f'<a class="tw" href="https://twitter.com/intent/tweet?text={t}" target="_blank" rel="noopener" title="X">X</a>'
            f'<a class="tg" href="https://t.me/share/url?url={u}" target="_blank" rel="noopener" title="Telegram">T</a>'
            f'<button class="cp" type="button" title="Copy link" onclick="navigator.clipboard&&navigator.clipboard.writeText(\'{url}\');this.textContent=\'✓\'">🔗</button></span>')


def meta(url, title, date_txt, lang="hi"):
    T = TXT[lang]
    who = "पंडित राजू पाठक" if lang == "hi" else "Pandit Raju Pathak"
    return f'<div class="meta"><span>✍️ {T["by"]}: <b>{who}</b></span><span>🗓️ {T["upd"]}: {esc(date_txt)}</span>{share(url, title, lang)}</div>'


def shell(title, desc, canon, body, ld, lang="hi", cur=None):
    T = TXT[lang]
    nav = "".join(f'<a href="{u}">{n}</a>' for u, n in T["nav"])
    return f"""<!DOCTYPE html>
<html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-20R9EGZKVE"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-20R9EGZKVE");</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5358706010218532" crossorigin="anonymous"></script>
<link rel="canonical" href="{canon}"><link rel="icon" href="../favicon.png">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{SITE}/og.jpg"><meta property="og:url" content="{canon}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;700;800&display=optional" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;700;800&display=optional"></noscript>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style><script src="/push.js" defer></script></head><body>
<div class="mast"><div class="w"><img src="../favicon.png" alt="पंडित राजू पाठक" width="56" height="56"><div><b>All Is Well Rashifal</b><small>पंडित राजू पाठक • राशिफल • गोचर • पंचांग</small></div></div></div>
<nav><div class="w">{nav}</div></nav>
{rashi_bar(cur, lang)}
<div class="lay"><main>{body}</main><aside>{aside(lang)}</aside></div>
<footer>© All Is Well Rashifal – पंडित राजू पाठक, झाँसी • 📞 8815605282<br>
<a href="../about.html">हमारे बारे में</a><a href="../privacy.html">प्राइवेसी पॉलिसी</a><a href="../disclaimer.html">अस्वीकरण</a><a href="../contact.html">संपर्क</a></footer>
</body></html>"""


HL = ' style="background:#fff3dc"'


def rashi_links(cur=None):
    return '<div class="rl">' + "".join(
        f'<a href="{s}.html"{HL if s == cur else ""}>{sym} {h}</a>' for h, s, e, ro, sym, ak in RASHIS) + "</div>"


def stars(lst):
    return '<div class="st">' + "".join(f'<div>{esc(x["name"])} <span>{"★" * int(x["value"])}{"☆" * (5 - int(x["value"]))}</span></div>' for x in lst or []) + "</div>"


def rng(a, days):
    b = a + timedelta(days=days)
    if a.month == b.month:
        return f"{a.day} से {b.day} {MONTHS[a.month - 1]} {a.year}"
    if a.year == b.year:
        return f"{a.day} {MONTHS[a.month - 1]} से {b.day} {MONTHS[b.month - 1]} {a.year}"
    return f"{a.day} {MONTHS[a.month - 1]} {a.year} से {b.day} {MONTHS[b.month - 1]} {b.year}"


RANGE = {}


def period_page(data, now, dh, p, slug, name, en_name):
    r = RANGE[p]
    url = f"{SITE}/rashifal/{slug}"
    bch, bld = crumbs([("राशिफल", f"{SITE}/rashifal/"), (name, None)])
    title = f"{name} {r} – मेष से मीन तक | {en_name} Horoscope"
    cards = "".join(
        f'<div class="card" id="{s}"><h2><a href="{s}.html" style="text-decoration:none">{sym} {h} {name}</a></h2><div class="sub">{ro} {en_name} Horoscope • {en}</div>'
        f'<p>{esc(data[s].get(p, {}).get("text"))}</p><a href="{s}.html">आज का {h} राशिफल भी पढ़ें →</a></div>'
        for h, s, en, ro, sym, ak in RASHIS if data[s].get(p, {}).get("text"))
    if not cards:
        return
    body = (f'<div class="card">{bch}<h1>{name}: {r}</h1><div class="sub">मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ, मीन • {en_name} Horoscope</div>'
            f'{meta(url, f"{name} {r}", dh)}<div class="sum"><b>संक्षेप में:</b> ग्रहों की चाल के आधार पर {r} के बीच सभी 12 राशियों का हाल – करियर, धन, प्रेम और सेहत। अपनी राशि पर क्लिक करें।</div>'
            f'{rashi_links()}</div>{cards}'
            '<div class="card"><h2>अपनी कुंडली से सटीक भविष्य</h2><p>राशिफल चंद्र राशि पर आधारित सामान्य फल है। अपनी जन्म-कुंडली के अनुसार सटीक जानकारी के लिए पंडित राजू पाठक से पूरी कुंडली रिपोर्ट (₹2100) बनवाएँ।</p>'
            '<a class="btn red" href="/#kundli-banayen">मुफ़्त कुंडली बनाएँ</a><a class="btn" href="https://wa.me/918815605282">WhatsApp पर पूछें</a></div>')
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"{name} {r}", "datePublished": now.isoformat(), "dateModified": now.isoformat(),
          "inLanguage": "hi", "author": {"@type": "Person", "name": "पंडित राजू पाठक"},
          "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
          "image": f"{SITE}/og.jpg", "mainEntityOfPage": url}
    desc = f"{name} {r}: मेष से मीन तक सभी 12 राशियों का {name} – करियर, धन, प्रेम, सेहत और उपाय। पंडित राजू पाठक, All Is Well Rashifal।"
    open(os.path.join(OUT, slug), "w", encoding="utf-8").write(shell(title, desc, url, body, [ld, bld]))


# ---------------- लव राशिफल (सर्वर के आज के गोचर-आधारित प्रेम और वैवाहिक सितारों से) ----------------
def lvl(v):
    v = int(v or 0)
    return 0 if v <= 2 else (1 if v == 3 else 2)


def star_of(a, name):
    for x in a.get("stars") or []:
        if x.get("name") == name:
            return int(x.get("value") or 0)
    return 0


LOVE = ("प्रेम संबंधों में ग़लतफ़हमी हो सकती है। साथी से बहस या पुरानी बातें छेड़ने से बचें और धैर्य से काम लें।",
        "प्रेम जीवन सामान्य रहेगा। साथी की भावनाओं को समझें और उनके लिए थोड़ा समय ज़रूर निकालें।",
        "प्रेम जीवन में मिठास बढ़ेगी। साथी के साथ यादगार समय बीतेगा, दिल की बात कहने के लिए समय अच्छा है।")
MARRIED = ("वैवाहिक जीवन में छोटी बात पर तकरार हो सकती है। जीवनसाथी की बात ध्यान से सुनें, ग़ुस्से में कोई फ़ैसला न लें।",
           "जीवनसाथी के साथ संबंध सामान्य रहेंगे। घर के कामों में एक-दूसरे का हाथ बँटाएँ, आपसी समझ बढ़ेगी।",
           "जीवनसाथी के साथ प्यार और सहयोग बढ़ेगा। साथ में बाहर जाने या घर पर ख़ास पल बिताने का योग है।")
SINGLE = ("अविवाहित लोग रिश्ते की बात जल्दबाज़ी में आगे न बढ़ाएँ।",
          "अविवाहितों के लिए रिश्ते की बात धीरे-धीरे आगे बढ़ सकती है।",
          "अविवाहितों को किसी ख़ास व्यक्ति से मुलाक़ात या रिश्ते की अच्छी ख़बर मिल सकती है।")
LUPAY = ("शुक्र मंत्र 'ॐ शुं शुक्राय नमः' का 108 बार जाप करें।",
         "माता लक्ष्मी को सफ़ेद मिठाई का भोग लगाएँ।",
         "साथी को गुलाबी रंग का कोई छोटा उपहार दें, रिश्ते में मिठास बनी रहेगी।")


def hearts(v):
    return f'<span style="color:#d6336c;letter-spacing:2px">{"♥" * v}{"♡" * (5 - v)}</span>'


def love_page(data, now, dh, de):
    url = f"{SITE}/rashifal/love.html"
    rows, best, care = [], [], []
    for h, s, en, ro, sym, ak in RASHIS:
        a = data[s]["aaj"]
        pv, mv = star_of(a, "प्रेम"), star_of(a, "वैवाहिक जीवन")
        if not pv:
            continue
        (best if pv >= 4 else care if pv <= 2 else []).append(h)
        moon = ""
        t = a.get("text") or ""
        i = t.find("चंद्रमा आपकी राशि से")
        if i >= 0:
            moon = t[i:t.find("।", i) + 1]
        rows.append(f'<div class="card" id="{s}"><h2><a href="{s}.html" style="text-decoration:none">{sym} {h} लव राशिफल</a></h2>'
                    f'<div class="sub">{ro} Love Horoscope • {en} • प्रेम {hearts(pv)} &nbsp; वैवाहिक जीवन {hearts(mv)}</div>'
                    f'<p>{esc(moon)} {LOVE[lvl(pv)]} {SINGLE[lvl(pv)]}</p><p><b>शादीशुदा लोगों के लिए:</b> {MARRIED[lvl(mv)]}</p>'
                    f'<p><b>❤️ प्रेम उपाय:</b> {LUPAY[lvl(pv)]} &nbsp; <b>शुभ रंग:</b> {esc(a.get("shubh_rang"))}</p></div>')
    if not rows:
        return
    if best:
        head = f"{', '.join(best[:3])}{' समेत ' + str(len(best)) + ' राशियों' if len(best) > 3 else ' राशि वालों'} के प्रेम जीवन में बढ़ेगी मिठास"
    else:
        head = "जानें मेष से मीन तक प्रेम और वैवाहिक जीवन का हाल"
    title = f"लव राशिफल {dh}: {head} | Aaj Ka Love Rashifal"
    bch, bld = crumbs([("राशिफल", f"{SITE}/rashifal/"), ("लव राशिफल", None)])
    summ = (f"<b>संक्षेप में:</b> आज ({DAYS[now.weekday()]}) " + (f"{', '.join(best)} राशि वालों का प्रेम जीवन अच्छा रहेगा। " if best else "") +
            (f"{', '.join(care)} राशि वाले रिश्तों में संभलकर बात करें। " if care else "") + "पूरा हाल नीचे अपनी राशि में पढ़ें।")
    body = (f'<div class="card">{bch}<h1>लव राशिफल {dh}: {head}</h1><div class="sub">Aaj Ka Love Rashifal • Love Horoscope Today {de} • प्रेम और वैवाहिक जीवन</div>'
            f'{meta(url, title, dh)}<div class="sum">{summ}</div>{rashi_links()}</div>' + "".join(rows) +
            '<div class="card"><h2>यह लव राशिफल कैसे बनता है?</h2><p>यह राशिफल चंद्र राशि से आज के ग्रह गोचर (चंद्रमा, शुक्र, मंगल, गुरु आदि) को देखकर बनाया जाता है। '
            'पंचम भाव प्रेम का और सप्तम भाव विवाह का होता है, इन पर ग्रहों का असर देखकर सितारे दिए जाते हैं। यह सामान्य फल है; अपने रिश्ते या विवाह के बारे में सटीक जानकारी के लिए अपनी कुंडली दिखाएँ।</p>'
            '<a class="btn red" href="/#milan">मुफ़्त कुंडली मिलान</a><a class="btn" href="' + wa("नमस्ते पंडित जी, मुझे विवाह/प्रेम संबंध के बारे में पूछना है।") + '">WhatsApp पर पूछें</a></div>')
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"लव राशिफल {dh}", "datePublished": now.isoformat(), "dateModified": now.isoformat(),
          "inLanguage": "hi", "author": {"@type": "Person", "name": "पंडित राजू पाठक"},
          "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
          "image": f"{SITE}/og.jpg", "mainEntityOfPage": url}
    desc = f"आज का लव राशिफल {dh}: मेष से मीन तक प्रेम जीवन, वैवाहिक जीवन, अविवाहितों के लिए रिश्ते और प्रेम उपाय – पंडित राजू पाठक।"
    open(os.path.join(OUT, "love.html"), "w", encoding="utf-8").write(shell(title, desc, url, body, [ld, bld]))


# ---------------- अंक राशिफल (मूलांक 1-9): अंक-स्वामी ग्रह और आज के अंक व वार-स्वामी की नैसर्गिक मित्रता से ----------------
NUM_LORD = {1: "सूर्य", 2: "चंद्र", 3: "गुरु", 4: "राहु", 5: "बुध", 6: "शुक्र", 7: "केतु", 8: "शनि", 9: "मंगल"}
VAAR_LORD = ["चंद्र", "मंगल", "बुध", "गुरु", "शुक्र", "शनि", "सूर्य"]  # Python weekday (सोम=0)
MAITRI = {  # (मित्र, शत्रु) – बाकी सम
    "सूर्य": ({"चंद्र", "मंगल", "गुरु"}, {"शुक्र", "शनि", "राहु", "केतु"}),
    "चंद्र": ({"सूर्य", "बुध"}, {"राहु", "केतु"}),
    "मंगल": ({"सूर्य", "चंद्र", "गुरु"}, {"बुध", "राहु"}),
    "बुध": ({"सूर्य", "शुक्र", "राहु"}, {"चंद्र"}),
    "गुरु": ({"सूर्य", "चंद्र", "मंगल", "केतु"}, {"बुध", "शुक्र"}),
    "शुक्र": ({"बुध", "शनि", "राहु"}, {"सूर्य", "चंद्र"}),
    "शनि": ({"बुध", "शुक्र", "राहु"}, {"सूर्य", "चंद्र", "मंगल"}),
    "राहु": ({"बुध", "शुक्र", "शनि"}, {"सूर्य", "चंद्र", "मंगल"}),
    "केतु": ({"मंगल", "गुरु"}, {"सूर्य", "चंद्र"}),
}
NUM_NATURE = {1: "नेतृत्व करने वाले, आत्मविश्वासी और स्वाभिमानी", 2: "भावुक, कल्पनाशील और शांत स्वभाव के", 3: "ज्ञानी, अनुशासित और सलाह देने में आगे",
              4: "मेहनती, अलग सोच रखने वाले और अचानक फ़ैसले लेने वाले", 5: "बुद्धिमान, बातचीत में कुशल और व्यापारिक सोच वाले",
              6: "कला-प्रेमी, आकर्षक और सुख-सुविधा पसंद", 7: "गहरी सोच वाले, आध्यात्मिक और रहस्यमयी स्वभाव के",
              8: "धैर्यवान, गंभीर और लंबी मेहनत से सफलता पाने वाले", 9: "साहसी, ऊर्जावान और जोशीले"}
NUM_COLOUR = {1: "केसरिया", 2: "सफ़ेद", 3: "पीला", 4: "नीला-स्लेटी", 5: "हरा", 6: "गुलाबी", 7: "हल्का भूरा", 8: "गहरा नीला", 9: "लाल"}
NUM_UPAY = {1: "सुबह सूर्य देव को जल चढ़ाएँ", 2: "शिवलिंग पर दूध-जल चढ़ाएँ", 3: "केले के पेड़ में जल और हल्दी चढ़ाएँ",
            4: "माँ दुर्गा का ध्यान करें और पक्षियों को दाना डालें", 5: "गाय को हरा चारा खिलाएँ", 6: "माता लक्ष्मी को सफ़ेद मिठाई का भोग लगाएँ",
            7: "गणेश जी को दूर्वा चढ़ाएँ", 8: "पीपल के नीचे सरसों के तेल का दीपक जलाएँ", 9: "हनुमान चालीसा का पाठ करें"}
NUM_DAY = {  # स्तर -> क्षेत्र -> 3 विकल्प
    0: {"c": ["काम में रुकावट या देरी हो सकती है, नया काम या बड़ा निवेश टालें।", "दफ़्तर में किसी से बहस न करें, अपना काम चुपचाप पूरा करें।", "जल्दबाज़ी में लिया फ़ैसला नुकसान दे सकता है, ज़रूरी काम कल पर टालें।"],
        "m": ["पैसों के लेन-देन में सावधानी रखें, उधार देने से बचें।", "अचानक ख़र्च आ सकता है, फ़िज़ूलख़र्ची पर रोक लगाएँ।", "किसी के कहने पर पैसा न लगाएँ, धोखे से बचें।"],
        "r": ["रिश्तों में छोटी बात पर मनमुटाव हो सकता है, वाणी पर संयम रखें।", "परिवार में किसी बात पर तनाव हो सकता है, शांत रहें।", "साथी की बात को दिल पर न लें, ग़लतफ़हमी जल्दी दूर होगी।"],
        "h": ["थकान और तनाव रह सकता है, पर्याप्त आराम करें।", "पेट और सिर का ध्यान रखें, बाहर का खाना कम खाएँ।", "नींद पूरी न होने से चिड़चिड़ापन रह सकता है।"]},
    1: {"c": ["काम सामान्य गति से चलेगा, मेहनत जारी रखें तो फल ज़रूर मिलेगा।", "पुराने अधूरे काम निपटाने के लिए दिन ठीक है।", "सहकर्मियों से तालमेल बनाकर चलें, काम आसानी से बनेंगे।"],
        "m": ["आमदनी और ख़र्च बराबर रहेंगे, बजट बनाकर चलें।", "छोटा लाभ हो सकता है, बड़ा निवेश सोच-समझकर करें।", "पैसों की स्थिति स्थिर रहेगी, बचत पर ध्यान दें।"],
        "r": ["परिवार और साथी के साथ संबंध सामान्य रहेंगे।", "किसी पुराने मित्र से बात हो सकती है, मन हल्का होगा।", "घर के बड़ों की सलाह आज काम आएगी।"],
        "h": ["सेहत ठीक रहेगी, खान-पान और नींद का ध्यान रखें।", "हल्का व्यायाम या टहलना फ़ायदेमंद रहेगा।", "मौसम के बदलाव से सावधान रहें, पानी ज़्यादा पिएँ।"]},
    2: {"c": ["काम में सफलता के अच्छे योग हैं, अटका काम बन सकता है।", "नई ज़िम्मेदारी या अच्छा मौका मिल सकता है, आगे बढ़कर लें।", "आपकी मेहनत की तारीफ़ होगी, बड़े लोगों का साथ मिलेगा।"],
        "m": ["धन लाभ के योग हैं, रुका पैसा मिल सकता है।", "आमदनी बढ़ने के संकेत हैं, सौदे में फ़ायदा हो सकता है।", "पैसों से जुड़ा कोई अच्छा समाचार मिल सकता है।"],
        "r": ["परिवार और साथी का पूरा साथ मिलेगा।", "किसी ख़ास से मुलाक़ात या शुभ समाचार मिल सकता है।", "रिश्तों में मिठास बढ़ेगी, घर में ख़ुशी का माहौल रहेगा।"],
        "h": ["मन प्रसन्न और शरीर ऊर्जावान रहेगा।", "सेहत अच्छी रहेगी, नई ऊर्जा महसूस करेंगे।", "पुरानी परेशानी में राहत मिलेगी।"]}}


def reduce9(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def rel(a, b):
    if a == b or b in MAITRI[a][0]:
        return 1, "मित्रता"
    if b in MAITRI[a][1]:
        return -1, "शत्रुता"
    return 0, "सम संबंध"


def ank_page(now, dh, de):
    url = f"{SITE}/rashifal/ank-jyotish.html"
    dn = reduce9(sum(int(c) for c in now.strftime("%d%m%Y")))
    dlord, vlord, vaar = NUM_LORD[dn], VAAR_LORD[now.weekday()], DAYS[now.weekday()]
    rows, best, care = [], [], []
    for n in range(1, 10):
        L = NUM_LORD[n]
        s1, r1 = rel(L, dlord)
        s2, r2 = rel(L, vlord)
        lv = 2 if s1 + s2 >= 2 else (1 if s1 + s2 >= 0 else 0)
        (best if lv == 2 else care if lv == 0 else []).append(str(n))
        dates = ", ".join(str(d) for d in range(n, 32, 9))
        lucky = ", ".join(str(k) for k in range(1, 10) if rel(L, NUM_LORD[k])[0] == 1)
        word = ("संभलकर चलने का", "मिला-जुला", "शुभ")[lv]
        c, m, r, h = (NUM_DAY[lv][k][(n + dn + q) % 3] for q, k in enumerate("cmrh"))
        rows.append(f'<div class="card" id="m{n}"><h2>मूलांक {n} <small style="color:var(--muted);font-weight:400">(जन्म तारीख {dates})</small></h2>'
                    f'<div class="sub">स्वामी ग्रह: {L} • आज का दिन: <b>{word}</b> {"★" * (lv + 2)}{"☆" * (3 - lv)}</div>'
                    f'<p>मूलांक {n} वाले {NUM_NATURE[n]} होते हैं। आपके स्वामी {L} की आज के अंक {dn} के स्वामी {dlord} से {r1} है और आज के वार ({vaar}) के स्वामी {vlord} से {r2}, इसलिए आज का दिन आपके लिए {word} रहेगा।</p>'
                    f'<p><b>💼 करियर:</b> {c} <b>💰 धन:</b> {m} <b>❤️ रिश्ते:</b> {r} <b>🩺 सेहत:</b> {h}</p>'
                    f'<p><b>शुभ अंक:</b> {lucky} &nbsp; <b>शुभ रंग:</b> {NUM_COLOUR[n]} &nbsp; <b>उपाय:</b> {NUM_UPAY[n]}।</p></div>')
    head = (f"मूलांक {', '.join(best)} वालों के लिए शुभ दिन" if best else "मूलांक 1 से 9 वालों का दिन कैसा रहेगा")
    title = f"अंक राशिफल {dh}: {head} | Aaj Ka Ank Jyotish"
    bch, bld = crumbs([("राशिफल", f"{SITE}/rashifal/"), ("अंक ज्योतिष", None)])
    summ = (f"<b>संक्षेप में:</b> आज {dh} का कुल अंक <b>{dn}</b> है (स्वामी {dlord}) और {vaar} का स्वामी {vlord} है। "
            + (f"मूलांक {', '.join(best)} वालों के लिए दिन शुभ है। " if best else "") + (f"मूलांक {', '.join(care)} वाले आज संभलकर चलें। " if care else ""))
    how = ('<div class="card"><h2>अपना मूलांक कैसे जानें?</h2><p>अपनी जन्म तारीख (सिर्फ़ दिन) के अंकों को जोड़ें, जब तक एक अंक न बचे। जैसे 14 तारीख: 1+4 = <b>5</b>, '
           '29 तारीख: 2+9 = 11, फिर 1+1 = <b>2</b>। यही आपका मूलांक है। आज का अंक पूरी तारीख (दिन+महीना+वर्ष) जोड़कर निकाला गया है।</p>'
           '<p>यह फल मूलांक के स्वामी ग्रह की आज के अंक और वार के स्वामी ग्रह से नैसर्गिक मित्रता पर आधारित सामान्य फल है।</p>'
           '<a class="btn red" href="/#kundli-banayen">मुफ़्त कुंडली बनाएँ</a><a class="btn" href="' + wa("नमस्ते पंडित जी, मुझे अंक ज्योतिष के बारे में पूछना है।") + '">WhatsApp पर पूछें</a></div>')
    body = (f'<div class="card">{bch}<h1>अंक राशिफल {dh}: {head}</h1><div class="sub">Aaj Ka Ank Jyotish • Numerology Today {de} • मूलांक 1 से 9</div>'
            f'{meta(url, title, dh)}<div class="sum">{summ}</div><div class="rl">' + "".join(f'<a href="#m{n}">मूलांक {n}</a>' for n in range(1, 10)) + '</div></div>' + "".join(rows) + how)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"अंक राशिफल {dh}", "datePublished": now.isoformat(), "dateModified": now.isoformat(),
          "inLanguage": "hi", "author": {"@type": "Person", "name": "पंडित राजू पाठक"},
          "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
          "image": f"{SITE}/og.jpg", "mainEntityOfPage": url}
    desc = f"आज का अंक राशिफल {dh}: मूलांक 1 से 9 वालों का करियर, धन, रिश्ते, सेहत, शुभ अंक, शुभ रंग और उपाय – पंडित राजू पाठक।"
    open(os.path.join(OUT, "ank-jyotish.html"), "w", encoding="utf-8").write(shell(title, desc, url, body, [ld, bld]))


def main():
    now = datetime.now(IST)
    dh = f"{now.day} {MONTHS[now.month - 1]} {now.year}"
    de = f"{now.day} {MONTHS_EN[now.month - 1]} {now.year}"
    iso = now.strftime("%Y-%m-%d")
    global RANGE
    RANGE = {"saptah": rng(now, 6), "mahina": rng(now, 29)}
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
        purl = f"{SITE}/rashifal/{s}.html"
        bch, bld = crumbs([("आज का राशिफल", f"{SITE}/rashifal/"), (f"{h} राशिफल", None)])
        body = f"""<div class="card">{bch}<span class="sym">{sym}</span><h1>{h} राशिफल आज – {dh}</h1>
<div class="sub">{DAYS[now.weekday()]} • {ro} Rashifal Today • {en} Horoscope {de} • नाम अक्षर: {ak}</div>{meta(purl, f"{h} राशिफल आज {dh}", dh)}
<h2>आज का {h} राशिफल</h2><p>{esc(a.get('text'))}</p>
<div class="facts"><div><b>💼 करियर</b>{esc(a.get('career'))}</div><div><b>💞 प्रेम</b>{esc(a.get('prem'))}</div><div><b>🩺 सेहत</b>{esc(a.get('swasthya'))}</div><div><b>💰 धन</b>{esc(a.get('dhan'))}</div>
<div><b>🔢 शुभ अंक</b>{esc(a.get('shubh_ank'))}</div><div><b>🎨 शुभ रंग</b>{esc(a.get('shubh_rang'))}</div>{f'<div><b>⏰ शुभ समय</b>{esc(a.get("best_time"))}</div>' if a.get('best_time') else ''}{f'<div><b>⚠️ सावधानी</b>{esc(a.get("caution_time"))}</div>' if a.get('caution_time') else ''}</div>
{stars(a.get('stars'))}
<h2>आज का उपाय</h2><p>{esc(a.get('upay'))}</p></div>"""
        for p, ph in PERIODS[1:]:
            t = data[s].get(p, {}).get("text")
            if t:
                body += f'<div class="card" id="{p}"><h2>{h} {ph} ({RANGE[p]})</h2><p>{esc(t)}</p></div>'
        body += f"""<div class="card"><h2>{en} Horoscope Today ({de})</h2><p>Daily {en} ({ro}) horoscope by Pandit Raju Pathak. Lucky number: {esc(a.get('shubh_ank'))}. The detailed prediction above is in Hindi.</p>
<h2>अपनी कुंडली से सटीक भविष्य</h2><p>राशिफल सामान्य होता है। अपनी जन्म-कुंडली के अनुसार सटीक जानकारी के लिए पंडित राजू पाठक से पूरी कुंडली रिपोर्ट (₹2100) बनवाएँ।</p>
<a class="btn red" href="/#kundli-banayen">मुफ़्त कुंडली बनाएँ</a><a class="btn" href="https://wa.me/918815605282">WhatsApp पर पूछें</a></div>
<div class="card"><h2>दूसरी राशियों का आज का राशिफल</h2>{rashi_links(s)}</div>"""
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"{h} राशिफल आज {dh}", "datePublished": now.isoformat(),
              "dateModified": now.isoformat(), "inLanguage": "hi", "author": {"@type": "Person", "name": "पंडित राजू पाठक"},
              "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
              "image": f"{SITE}/og.jpg", "mainEntityOfPage": f"{SITE}/rashifal/{s}.html"}
        open(os.path.join(OUT, f"{s}.html"), "w", encoding="utf-8").write(shell(title, desc, purl, body, [ld, bld], cur=s))

    cards = "".join(f'<div class="card"><h2><a href="{s}.html" style="text-decoration:none">{sym} {h} राशिफल ({en})</a></h2><p>{esc((data[s]["aaj"].get("text") or "")[:180])}… <a href="{s}.html">पूरा पढ़ें →</a></p></div>'
                    for h, s, en, ro, sym, ak in RASHIS)
    period_page(data, now, dh, "saptah", "saptahik.html", "साप्ताहिक राशिफल", "Weekly")
    period_page(data, now, dh, "mahina", "masik.html", "मासिक राशिफल", "Monthly")
    love_page(data, now, dh, de)
    ank_page(now, dh, de)
    bch, bld = crumbs([("आज का राशिफल", None)])
    body = f'<div class="card">{bch}<h1>आज का राशिफल – {dh}</h1><div class="sub">{DAYS[now.weekday()]} • Aaj Ka Rashifal • Horoscope Today {de} • पंडित राजू पाठक</div>{rashi_links()}</div>{cards}'
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"आज का राशिफल {dh}", "url": f"{SITE}/rashifal/"}, bld]
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell(f"आज का राशिफल {dh} – मेष से मीन तक | Aaj Ka Rashifal – All Is Well Rashifal",
              f"आज का राशिफल {dh}: मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ और मीन राशि का दैनिक राशिफल – पंडित राजू पाठक।",
              f"{SITE}/rashifal/", body, ld))

    urls = [("", "daily"), ("rashifal/", "daily")] + [(f"rashifal/{s}.html", "daily") for _, s, *_ in RASHIS] + [("rashifal/saptahik.html", "daily"), ("rashifal/masik.html", "daily"), ("rashifal/love.html", "daily"), ("rashifal/ank-jyotish.html", "daily")] + \
           [("lekh/", "weekly")] + [("lekh/" + f, "monthly") for f in sorted(os.listdir(os.path.join(ROOT, "docs", "lekh"))) if f.endswith(".html") and f != "index.html"] * os.path.isdir(os.path.join(ROOT, "docs", "lekh")) + \
           [(d + "/" + (f if f != "index.html" else ""), "weekly" if f == "index.html" else "monthly") for d in ("en/lekh", "web-stories") if os.path.isdir(os.path.join(ROOT, "docs", d)) for f in sorted(os.listdir(os.path.join(ROOT, "docs", d))) if f.endswith(".html")] + \
           [(u, "monthly") for u in ("about.html", "contact.html", "privacy.html", "disclaimer.html", "terms.html")]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{SITE}/{u}</loc><lastmod>{iso}</lastmod><changefreq>{c}</changefreq></url>\n" for u, c in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "docs", "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print("बन गए:", len(RASHIS), "राशि पेज", dh)


if __name__ == "__main__":
    main()
