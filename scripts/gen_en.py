"""English versions of the daily pages: docs/en/rashifal/*.html
Runs right after gen_rashi.py every night. Uses the same server data and turns the
automatic Hindi rashifal into English sentence by sentence (same gochar rules).
Also adds the Hindi/English button and hreflang links to the Hindi daily pages."""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_rashi as G  # noqa: E402
from datetime import datetime  # noqa: E402

SITE, RASHIS = G.SITE, G.RASHIS
HI_DIR = os.path.join(G.ROOT, "docs", "rashifal")
EN_DIR = os.path.join(G.ROOT, "docs", "en", "rashifal")
esc = G.esc
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PL = {"सूर्य": "the Sun", "चंद्र": "the Moon", "चंद्रमा": "the Moon", "मंगल": "Mars", "बुध": "Mercury", "गुरु": "Jupiter",
      "शुक्र": "Venus", "शनि": "Saturn", "राहु": "Rahu", "केतु": "Ketu"}
PL_CAP = {k: v[0].upper() + v[1:] for k, v in PL.items()}
NAK = dict(zip(["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी",
                "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण",
                "धनिष्ठा", "शतभिषा", "पूर्वा भाद्रपद", "उत्तरा भाद्रपद", "रेवती"],
               ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
                "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
                "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]))
HOUSE = {  # house: (Hindi good, Hindi bad, English good, English bad) – same table as the server
    1: ("मन प्रसन्न रहेगा, आत्मविश्वास बढ़ेगा और रुके काम आगे बढ़ेंगे", "मन थोड़ा बेचैन रह सकता है, जल्दबाज़ी में फैसला न लें",
        "your mind will be cheerful, confidence will grow and pending work will move ahead", "your mind may stay a little restless, so avoid hasty decisions"),
    2: ("धन आने के योग हैं, परिवार का साथ मिलेगा और वाणी से काम बनेंगे", "खर्च बढ़ सकता है, बोलचाल में संयम रखें, परिवार में बहस से बचें",
        "money is likely to come in, your family will support you and your words will get things done", "expenses may rise, so watch your words and avoid arguments in the family"),
    3: ("हिम्मत और मेहनत का पूरा फल मिलेगा, भाई-बहनों और मित्रों से सहयोग मिलेगा", "आलस से काम अटक सकते हैं, छोटी यात्रा में सावधानी रखें",
        "your courage and hard work will pay off fully, and siblings and friends will help you", "laziness may hold up work, so be careful on short trips"),
    4: ("घर-परिवार में सुख रहेगा, वाहन या घर से जुड़ा काम बन सकता है", "घर में किसी बात को लेकर तनाव हो सकता है, माता की सेहत का ध्यान रखें",
        "there will be happiness at home, and work related to a vehicle or house may get done", "there may be tension at home, so take care of your mother's health"),
    5: ("बुद्धि तेज़ चलेगी, संतान और प्रेम संबंधों से खुशी मिलेगी", "प्रेम और संतान को लेकर चिंता हो सकती है, सट्टे या जोखिम से दूर रहें",
        "your mind will be sharp, and children and love life will bring joy", "there may be worry about love or children, so stay away from speculation and risk"),
    6: ("शत्रु और विरोधी कमज़ोर पड़ेंगे, पुराने रोग और कर्ज़ से राहत मिलेगी", "सेहत और विरोधियों से सावधान रहें, उधार देने से बचें",
        "enemies and rivals will weaken, and you will get relief from old illness and debt", "be careful about health and opponents, and avoid lending money"),
    7: ("जीवनसाथी और साझेदारी से लाभ होगा, नए संबंध बन सकते हैं", "जीवनसाथी या साझेदार से अनबन हो सकती है, धैर्य से बात करें",
        "you will gain from your spouse and partnerships, and new relationships may form", "there may be friction with your spouse or partner, so talk patiently"),
    8: ("अचानक लाभ या रुका पैसा मिलने के योग हैं, गुप्त बातों में सफलता", "अचानक रुकावट या चोट का डर है, वाहन धीरे चलाएँ और सेहत पर ध्यान दें",
        "there are chances of a sudden gain or of getting stuck money back, with success in confidential matters", "there is a risk of sudden obstacles or injury, so drive slowly and watch your health"),
    9: ("भाग्य साथ देगा, धर्म-कर्म और बड़ों के आशीर्वाद से काम बनेंगे", "भाग्य थोड़ा धीमा रहेगा, पिता या गुरु से मतभेद से बचें",
        "luck will be on your side, and work will get done through good deeds and the blessings of elders", "luck will be a little slow, so avoid disagreements with your father or teacher"),
    10: ("नौकरी-व्यापार में तरक्की, मान-सम्मान और नई ज़िम्मेदारी मिल सकती है", "कार्यक्षेत्र में दबाव रहेगा, अधिकारियों से बहस न करें",
         "you may get progress in your job or business, respect and new responsibilities", "there will be pressure at work, so don't argue with your seniors"),
    11: ("आमदनी बढ़ेगी, इच्छाएँ पूरी होंगी और बड़े लोगों से लाभ मिलेगा", "लाभ में देरी हो सकती है, मित्रों पर आँख मूँदकर भरोसा न करें",
         "income will rise, wishes will be fulfilled and you will gain from influential people", "gains may be delayed, so don't trust friends blindly"),
    12: ("दान-पुण्य और यात्रा से मन को शांति मिलेगी", "खर्च और भागदौड़ बढ़ेगी, नींद पूरी न होने से थकान रह सकती है",
         "charity and travel will bring peace of mind", "expenses and running around will increase, and lack of sleep may leave you tired"),
}
HI2EN = {}
for _h, (a, b, c, d) in HOUSE.items():
    HI2EN[a], HI2EN[b] = c, d
AREA = {  # star name: (Hindi name, English name, (low, mid, high) English sentences)
    "व्यवसाय": ("Career", ("Work may face obstacles, so postpone new investments or big decisions for now.",
                           "Job and business will run normally; keep working and results will come gradually.",
                           "Your hard work will be appreciated at work, and a new task or deal may bring gains.")),
    "धन-सम्पत्ति": ("Money", ("Be careful with money and avoid wasteful spending and lending.",
                              "Income and expenses will stay balanced, so focus on saving.",
                              "There are good chances of financial gain, and money that was stuck may come back.")),
    "प्रेम": ("Love", ("There may be misunderstandings in love, so avoid harsh words.",
                       "Love life will be normal; try to understand your partner's feelings.",
                       "Love life will grow sweeter, and you will spend memorable time with your partner.")),
    "परिवार": ("Family", ("There may be a disagreement at home, so talk calmly.",
                          "The family atmosphere will be normal, and elders' advice will help.",
                          "You will spend good time with family, and the mood at home will be happy.")),
    "स्वास्थ्य": ("Health", ("Take care of your health; tiredness, stomach trouble or headache are possible.",
                             "Health will be normal; mind your diet and sleep.",
                             "Health will be good, with energy and freshness all day.")),
    "वैवाहिक जीवन": ("Married life", ("Small arguments with your spouse are possible, so be patient.",
                                      "Married life will be normal; give each other time.",
                                      "Love and cooperation will grow in married life.")),
}
SHORT = {"व्यवसाय": ("Pressure, stay patient", "Normal, keep working", "Chances of progress"),
         "प्रेम": ("Avoid misunderstandings", "Normal", "Sweetness in relationships"),
         "स्वास्थ्य": ("Watch tiredness and stomach", "Normal, keep a good routine", "Good health"),
         "धन-सम्पत्ति": ("Control expenses", "Income and expenses balanced", "Chances of financial gain")}
COLOUR = {"केसरिया": "Saffron", "सफ़ेद": "White", "सफेद": "White", "लाल": "Red", "हरा": "Green", "पीला": "Yellow", "गुलाबी": "Pink",
          "नीला": "Blue", "नीला-स्लेटी": "Blue-grey", "हल्का भूरा": "Light brown", "गहरा नीला": "Dark blue"}
UPAY = {"सुबह सूर्य देव को जल चढ़ाएँ": "Offer water to the Sun God in the morning",
        "शिवलिंग पर दूध-जल चढ़ाएँ": "Offer milk mixed with water on a Shivling",
        "हनुमान चालीसा का पाठ करें": "Recite the Hanuman Chalisa",
        "गाय को हरा चारा खिलाएँ": "Feed green fodder to a cow",
        "केले के पेड़ में जल और हल्दी चढ़ाएँ": "Offer water and turmeric to a banana tree",
        "माता लक्ष्मी को सफ़ेद मिठाई का भोग लगाएँ": "Offer white sweets to Goddess Lakshmi",
        "शनिवार को पीपल के नीचे सरसों के तेल का दीपक जलाएँ": "On Saturday, light a mustard-oil lamp under a peepal tree",
        "पीपल के नीचे सरसों के तेल का दीपक जलाएँ": "Light a mustard-oil lamp under a peepal tree",
        "माँ दुर्गा का ध्यान करें, पक्षियों को दाना डालें": "Pray to Goddess Durga and feed grains to birds",
        "माँ दुर्गा का ध्यान करें और पक्षियों को दाना डालें": "Pray to Goddess Durga and feed grains to birds",
        "गणेश जी को दूर्वा चढ़ाएँ": "Offer durva grass to Lord Ganesha"}
ORD = {"पहले": 1, "दूसरे": 2, "तीसरे": 3, "चौथे": 4, "छठे": 6}
PLR = "सूर्य|चंद्रमा|चंद्र|मंगल|बुध|गुरु|शुक्र|शनि|राहु|केतु"


def ordn(w):
    if w in ORD:
        return ORD[w]
    m = re.match(r"(\d+)वें", w)
    return int(m.group(1)) if m else None


def eng_ord(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def lvl(v):
    return 0 if v <= 2 else (1 if v == 3 else 2)


def stars_of(a):
    return {x.get("name"): int(x.get("value") or 0) for x in a.get("stars") or []}


def planet_lines(text):
    """Turn the planet-house sentences of the automatic Hindi text into English."""
    out = []
    for s in [x.strip() for x in (text or "").split("।") if x.strip()]:
        m = re.match(r"^चंद्रमा आपकी राशि से (\S+) भाव में \((.+?) नक्षत्र\) हैं, इसलिए (.+)$", s)
        if m and ordn(m.group(1)) and m.group(3) in HI2EN:
            nak = NAK.get(m.group(2), "")
            out.append(f"The Moon is in the {eng_ord(ordn(m.group(1)))} house from your sign{f' ({nak} nakshatra)' if nak else ''}, so {HI2EN[m.group(3)]}.")
            continue
        m = re.match(rf"^({PLR}) आपकी राशि से (\S+) भाव में हैं, इसलिए (.+)$", s)
        if m and ordn(m.group(2)) and m.group(3) in HI2EN:
            out.append(f"{PL_CAP[m.group(1)]} is in the {eng_ord(ordn(m.group(2)))} house from your sign, so {HI2EN[m.group(3)]}.")
            continue
        m = re.match(rf"^({PLR}) के (\S+) भाव में होने से (.+)$", s)
        if m and ordn(m.group(2)) and m.group(3) in HI2EN:
            out.append(f"With {PL[m.group(1)]} in your {eng_ord(ordn(m.group(2)))} house, {HI2EN[m.group(3)]}.")
    return out


def moon_line(text):
    for s in planet_lines(text):
        if s.startswith("The Moon"):
            return s
    return ""


def remedy(a):
    u = (a.get("upay") or "").strip().rstrip("।")
    return UPAY.get(u, "Chant 'Om Namah Shivaya' 108 times")


def to_en(a, period):
    """English rashifal for one rashi and one period from the server data."""
    st = stars_of(a)
    if not st:
        return None
    avg = sum(st.values()) / len(st)
    lead = {"aaj": "Today", "saptah": "This week", "mahina": "This month"}[period]
    mood = (f"{lead} is in your favour, and the planets are supporting you." if avg >= 3.7 else
            f"{lead} calls for some caution, so avoid haste." if avg <= 2.5 else
            f"{lead} will be mixed, so think before you act.")
    parts = [mood] + planet_lines(a.get("text"))
    for k in ("व्यवसाय", "धन-सम्पत्ति", "प्रेम", "परिवार", "स्वास्थ्य"):
        if k in st:
            parts.append(AREA[k][1][lvl(st[k])])
    rem = remedy(a)
    parts.append(f"Remedy: {rem}.")
    short = {k: SHORT[k][lvl(st.get(k, 3))] for k in SHORT}
    return {"text": " ".join(parts), "career": short["व्यवसाय"], "love": short["प्रेम"], "health": short["स्वास्थ्य"], "money": short["धन-सम्पत्ति"],
            "stars": [(AREA[k][0], v) for k, v in st.items() if k in AREA], "num": a.get("shubh_ank") or "",
            "colour": COLOUR.get((a.get("shubh_rang") or "").strip(), a.get("shubh_rang") or ""), "remedy": rem,
            "best": (a.get("best_time") or "").replace(" से ", " to "),
            "caution": (a.get("caution_time") or "").replace(" से ", " to ").replace("राहुकाल", "Rahu Kaal")}


# ---------------- page parts ----------------
NAV = [("/", "Home"), ("/en/rashifal/", "Daily Horoscope"), ("/en/rashifal/saptahik.html", "Weekly"), ("/en/rashifal/masik.html", "Monthly"),
       ("/en/rashifal/love.html", "Love Horoscope"), ("/en/rashifal/ank-jyotish.html", "Numerology"), ("/en/lekh/", "Horoscope 2027"),
       ("/web-stories/", "Web Stories"), ("/#kundli-banayen", "Free Kundli"), ("/#milan", "Kundli Matching")]
TREND = [("/en/rashifal/", "Today's horoscope – all 12 signs"), ("/en/rashifal/love.html", "Today's love horoscope ❤️"),
         ("/en/rashifal/ank-jyotish.html", "Today's numerology (1-9)"), ("/en/rashifal/saptahik.html", "Weekly horoscope"),
         ("/en/lekh/", "Horoscope 2027 – all 12 signs")]
LBTN_CSS = ".lbtn{margin-left:auto;background:var(--red);color:#fff!important;text-decoration:none;font-weight:800;font-size:15px;padding:6px 14px;border-radius:20px;white-space:nowrap}"


def rashi_bar(cur=None):
    return '<div class="rb"><div class="w">' + "".join(
        f'<a href="/en/rashifal/{s}.html"{" class=on" if s == cur else ""}><i>{sym}</i>{e}</a>' for h, s, e, ro, sym, ak in RASHIS) + "</div></div>"


def rashi_links(cur=None):
    return '<div class="rl">' + "".join(
        f'<a href="{s}.html"{G.HL if s == cur else ""}>{sym} {e}</a>' for h, s, e, ro, sym, ak in RASHIS) + "</div>"


def aside():
    g = "".join(f'<a href="{G.wa(m)}" target="_blank" rel="noopener"><i>{ic}</i>{n}<small>{sm}</small></a>' for ic, n, sm, m in G.SVC["en"])
    return (f'<div class="svc"><h3>🔯 Astrology Services</h3><p>Talk to Pandit Raju Pathak directly on WhatsApp</p><div class="svg">{g}</div>'
            f'<a class="go" href="{G.wa(G.SVC["en"][0][3])}" target="_blank" rel="noopener">Ask on WhatsApp →</a></div>'
            '<div class="side"><h3>🔥 Trending</h3>' + "".join(f'<a class="ln" href="{u}">{n}</a>' for u, n in TREND) + '</div>'
            '<div class="side"><h3>Free Tools</h3><a class="ln" href="/#kundli-banayen">🔯 Free Kundli</a><a class="ln" href="/#milan">💑 Free Kundli Matching</a>'
            '<a class="ln" href="/#sadesati">🪐 Check Sade Sati</a><a class="ln" href="/#muhurat">📅 Shubh Muhurat</a></div>')


def crumbs(items):
    allc = [("Home", SITE + "/")] + list(items)
    html = '<div class="bc">' + '<span>›</span>'.join(f'<a href="{u}">{esc(n)}</a>' if u else esc(n) for n, u in allc) + "</div>"
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        dict({"@type": "ListItem", "position": k + 1, "name": n}, **({"item": u} if u else {})) for k, (n, u) in enumerate(allc)]}
    return html, ld


def meta(url, title, date_txt):
    return f'<div class="meta"><span>✍️ By: <b><a href="/author/">Pandit Raju Pathak</a></b></span><span>🗓️ Updated: {esc(date_txt)}</span>{G.share(url, title, "en")}</div>'


def article_ld(head, now, url):
    return {"@context": "https://schema.org", "@type": "Article", "headline": head, "datePublished": now.isoformat(), "dateModified": now.isoformat(),
            "inLanguage": "en", "author": {"@type": "Person", "name": "Pandit Raju Pathak"},
            "publisher": {"@type": "Organization", "name": "All Is Well Rashifal", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
            "image": f"{SITE}/og.jpg", "mainEntityOfPage": url}


def shell(title, desc, slug, body, ld, cur=None):
    s2 = "" if slug == "index.html" else slug
    en_url, hi_url = f"{SITE}/en/rashifal/{s2}", f"{SITE}/rashifal/{s2}"
    nav = "".join(f'<a href="{u}">{n}</a>' for u, n in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<script>try{{localStorage.setItem("aiwr_lang","en")}}catch(e){{}}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-20R9EGZKVE"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-20R9EGZKVE");</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5358706010218532" crossorigin="anonymous"></script>
<link rel="canonical" href="{en_url}"><link rel="icon" href="/favicon.png">
<link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="hi" href="{hi_url}"><link rel="alternate" hreflang="x-default" href="{hi_url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{SITE}/og.jpg"><meta property="og:url" content="{en_url}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;700;800&display=optional" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{G.CSS}{LBTN_CSS}</style><script src="/push.js" defer></script></head><body>
<div class="mast"><div class="w"><img src="/favicon.png" alt="Pandit Raju Pathak" width="56" height="56"><div><b>All Is Well Rashifal</b><small>Pandit Raju Pathak • Horoscope • Transits • Panchang</small></div><a class="lbtn" href="{hi_url}" onclick="try{{localStorage.setItem('aiwr_lang','hi')}}catch(e){{}}">हिंदी</a></div></div>
<nav><div class="w">{nav}</div></nav>
{rashi_bar(cur)}
<div class="lay"><main>{body}</main><aside>{aside()}</aside></div>
<footer>© All Is Well Rashifal – Pandit Raju Pathak, Jhansi, India • 📞 +91 8815605282<br>
<a href="/about.html">About</a><a href="/privacy.html">Privacy Policy</a><a href="/disclaimer.html">Disclaimer</a><a href="/contact.html">Contact</a></footer>
</body></html>"""


def write(slug, html):
    open(os.path.join(EN_DIR, slug), "w", encoding="utf-8").write(html)


def stars_html(lst):
    return '<div class="st">' + "".join(f'<div>{esc(n)} <span>{"★" * v}{"☆" * (5 - v)}</span></div>' for n, v in lst) + "</div>"


def rng_en(a, days):
    b = a + G.timedelta(days=days)
    M = G.MONTHS_EN
    if a.month == b.month:
        return f"{a.day} to {b.day} {M[a.month - 1]} {a.year}"
    if a.year == b.year:
        return f"{a.day} {M[a.month - 1]} to {b.day} {M[b.month - 1]} {a.year}"
    return f"{a.day} {M[a.month - 1]} {a.year} to {b.day} {M[b.month - 1]} {b.year}"


KUNDLI_CARD = ('<div class="card"><h2>Accurate predictions from your own kundli</h2><p>A horoscope based on the Moon sign is a general prediction. '
               'For accurate guidance based on your birth chart, get a full kundli report (₹2100) from Pandit Raju Pathak.</p>'
               '<a class="btn red" href="/#kundli-banayen">Make a free kundli</a><a class="btn" href="https://wa.me/918815605282">Ask on WhatsApp</a></div>')


def rashi_pages(en, now, de):
    for h, s, e, ro, sym, ak in RASHIS:
        a = en[s].get("aaj")
        if not a:
            continue
        url = f"{SITE}/en/rashifal/{s}.html"
        title = f"{e} Horoscope Today {de} | {ro} Rashifal – Daily {e} Horoscope"
        desc = f"{e} ({ro}) horoscope for today, {DAYS_EN[now.weekday()]} {de}: career, love, health, money, lucky number, lucky colour and remedy – Pandit Raju Pathak."
        bch, bld = crumbs([("Daily Horoscope", f"{SITE}/en/rashifal/"), (f"{e} Horoscope", None)])
        body = f"""<div class="card">{bch}<span class="sym">{sym}</span><h1>{e} Horoscope Today – {de}</h1>
<div class="sub">{DAYS_EN[now.weekday()]} • {ro} Rashifal • {h} • Name letters: {ak}</div>{meta(url, f"{e} Horoscope Today {de}", de)}
<h2>Today's {e} Horoscope</h2><p>{esc(a["text"])}</p>
<div class="facts"><div><b>💼 Career</b>{esc(a["career"])}</div><div><b>💞 Love</b>{esc(a["love"])}</div><div><b>🩺 Health</b>{esc(a["health"])}</div><div><b>💰 Money</b>{esc(a["money"])}</div>
<div><b>🔢 Lucky number</b>{esc(a["num"])}</div><div><b>🎨 Lucky colour</b>{esc(a["colour"])}</div>{f'<div><b>⏰ Best time</b>{esc(a["best"])}</div>' if a["best"] else ''}{f'<div><b>⚠️ Caution</b>{esc(a["caution"])}</div>' if a["caution"] else ''}</div>
{stars_html(a["stars"])}
<h2>Today's remedy</h2><p>{esc(a["remedy"])}.</p></div>"""
        for p, ph in (("saptah", "Weekly Horoscope"), ("mahina", "Monthly Horoscope")):
            t = (en[s].get(p) or {}).get("text")
            if t:
                body += f'<div class="card" id="{p}"><h2>{e} {ph} ({RANGE[p]})</h2><p>{esc(t)}</p></div>'
        body += KUNDLI_CARD + f'<div class="card"><h2>Today\'s horoscope for other signs</h2>{rashi_links(s)}</div>'
        write(f"{s}.html", shell(title, desc, f"{s}.html", body, [article_ld(f"{e} Horoscope Today {de}", now, url), bld], cur=s))


def period_page(en, now, de, p, slug, name):
    r = RANGE[p]
    url = f"{SITE}/en/rashifal/{slug}"
    cards = "".join(
        f'<div class="card" id="{s}"><h2><a href="{s}.html" style="text-decoration:none">{sym} {e} {name}</a></h2><div class="sub">{ro} Rashifal • {h}</div>'
        f'<p>{esc(en[s][p]["text"])}</p><a href="{s}.html">Read today\'s {e} horoscope too →</a></div>'
        for h, s, e, ro, sym, ak in RASHIS if en[s].get(p))
    if not cards:
        return
    bch, bld = crumbs([("Daily Horoscope", f"{SITE}/en/rashifal/"), (name, None)])
    title = f"{name} {r} – Aries to Pisces | All Is Well Rashifal"
    body = (f'<div class="card">{bch}<h1>{name}: {r}</h1><div class="sub">Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces</div>'
            f'{meta(url, f"{name} {r}", de)}<div class="sum"><b>In short:</b> Based on the planetary transits, here is how {r} looks for all 12 signs – career, money, love and health. Click your sign.</div>'
            f'{rashi_links()}</div>{cards}{KUNDLI_CARD}')
    desc = f"{name} {r}: predictions for all 12 signs from Aries to Pisces – career, money, love, health and remedies. Pandit Raju Pathak, All Is Well Rashifal."
    write(slug, shell(title, desc, slug, body, [article_ld(f"{name} {r}", now, url), bld]))


LOVE = ("There may be misunderstandings in love. Avoid arguments or digging up old issues with your partner, and be patient.",
        "Love life will be normal. Understand your partner's feelings and make some time for them.",
        "Love life will grow sweeter. You will spend memorable time with your partner, and it is a good time to say what is in your heart.")
MARRIED = ("Small arguments may arise in married life. Listen carefully to your spouse and don't decide anything in anger.",
           "Relations with your spouse will be normal. Share the household work and your understanding will grow.",
           "Love and cooperation with your spouse will grow. There is a chance of going out together or spending special moments at home.")
SINGLE = ("Singles should not rush a relationship.", "For singles, talk of a relationship may move ahead slowly.",
          "Singles may meet someone special or get good news about a relationship.")
LUPAY = ("Chant the Venus mantra 'Om Shum Shukraya Namah' 108 times.", "Offer white sweets to Goddess Lakshmi.",
         "Give your partner a small pink gift to keep the sweetness in your relationship.")


def hearts(v):
    return f'<span style="color:#d6336c;letter-spacing:2px">{"♥" * v}{"♡" * (5 - v)}</span>'


def love_page(raw, now, de):
    url = f"{SITE}/en/rashifal/love.html"
    rows, best, care = [], [], []
    for h, s, e, ro, sym, ak in RASHIS:
        a = raw[s].get("aaj") or {}
        st = stars_of(a)
        pv, mv = st.get("प्रेम", 0), st.get("वैवाहिक जीवन", 0)
        if not pv:
            continue
        (best if pv >= 4 else care if pv <= 2 else []).append(e)
        rows.append(f'<div class="card" id="{s}"><h2><a href="{s}.html" style="text-decoration:none">{sym} {e} Love Horoscope</a></h2>'
                    f'<div class="sub">{ro} Love Rashifal • Love {hearts(pv)} &nbsp; Married life {hearts(mv)}</div>'
                    f'<p>{esc(moon_line(a.get("text")))} {LOVE[lvl(pv)]} {SINGLE[lvl(pv)]}</p><p><b>For married couples:</b> {MARRIED[lvl(mv)]}</p>'
                    f'<p><b>❤️ Love remedy:</b> {LUPAY[lvl(pv)]} &nbsp; <b>Lucky colour:</b> {esc(COLOUR.get(a.get("shubh_rang") or "", a.get("shubh_rang") or ""))}</p></div>')
    if not rows:
        return
    head = (f"{', '.join(best[:3])}{' and ' + str(len(best) - 3) + ' more signs' if len(best) > 3 else ''} will see more sweetness in love" if best
            else "Love and married life for all 12 signs")
    title = f"Love Horoscope Today {de}: {head}"
    bch, bld = crumbs([("Daily Horoscope", f"{SITE}/en/rashifal/"), ("Love Horoscope", None)])
    summ = (f"<b>In short:</b> Today ({DAYS_EN[now.weekday()]}) " + (f"love life looks good for {', '.join(best)}. " if best else "") +
            (f"{', '.join(care)} should speak carefully in relationships. " if care else "") + "Read your sign below.")
    body = (f'<div class="card">{bch}<h1>{title}</h1><div class="sub">Aaj Ka Love Rashifal • Love and married life</div>'
            f'{meta(url, title, de)}<div class="sum">{summ}</div>{rashi_links()}</div>' + "".join(rows) +
            '<div class="card"><h2>How is this love horoscope made?</h2><p>It is based on today\'s planetary transits (Moon, Venus, Mars, Jupiter and others) counted from your Moon sign. '
            'The 5th house rules love and the 7th house rules marriage; the stars show how the planets affect them. This is a general prediction – for your own relationship or marriage, show your kundli.</p>'
            '<a class="btn red" href="/#milan">Free kundli matching</a><a class="btn" href="' + G.wa("Namaste Pandit ji, I want to ask about love/marriage.") + '">Ask on WhatsApp</a></div>')
    desc = f"Today's love horoscope {de}: love life, married life and relationship news for singles, with love remedies for all 12 signs – Pandit Raju Pathak."
    write("love.html", shell(title, desc, "love.html", body, [article_ld(title, now, url), bld]))


NATURE = {1: "natural leaders, confident and self-respecting", 2: "emotional, imaginative and calm", 3: "wise, disciplined and good at giving advice",
          4: "hard-working, original thinkers who take sudden decisions", 5: "intelligent, good talkers with a business mind",
          6: "art-loving, attractive and fond of comfort", 7: "deep thinkers, spiritual and a little mysterious",
          8: "patient, serious and successful through long effort", 9: "brave, energetic and enthusiastic"}
NCOL = {1: "Saffron", 2: "White", 3: "Yellow", 4: "Blue-grey", 5: "Green", 6: "Pink", 7: "Light brown", 8: "Dark blue", 9: "Red"}
NUPAY = {1: "Offer water to the Sun God in the morning", 2: "Offer milk mixed with water on a Shivling", 3: "Offer water and turmeric to a banana tree",
         4: "Pray to Goddess Durga and feed grains to birds", 5: "Feed green fodder to a cow", 6: "Offer white sweets to Goddess Lakshmi",
         7: "Offer durva grass to Lord Ganesha", 8: "Light a mustard-oil lamp under a peepal tree", 9: "Recite the Hanuman Chalisa"}
NDAY = {0: {"c": ["Work may face delays; postpone new work or big investments.", "Avoid arguments at the office and quietly finish your work.", "A hasty decision may cause loss; push important work to tomorrow."],
            "m": ["Be careful with money matters and avoid lending.", "Sudden expenses may come up, so cut wasteful spending.", "Don't invest on someone else's word; beware of fraud."],
            "r": ["Small things may cause friction in relationships, so mind your words.", "There may be tension in the family; stay calm.", "Don't take your partner's words to heart; the misunderstanding will clear soon."],
            "h": ["You may feel tired and stressed, so rest well.", "Take care of your stomach and head, and eat less outside food.", "Lack of sleep may make you irritable."]},
        1: {"c": ["Work will move at a normal pace; keep going and results will come.", "A good day to finish old pending work.", "Stay in tune with colleagues and work will get done easily."],
            "m": ["Income and expenses will be balanced, so stick to a budget.", "A small gain is possible; think carefully before a big investment.", "Your money situation will be stable; focus on saving."],
            "r": ["Relations with family and partner will be normal.", "You may hear from an old friend, which will lift your mood.", "Advice from elders at home will be useful today."],
            "h": ["Health will be fine; mind your diet and sleep.", "Light exercise or a walk will do you good.", "Be careful with the change in weather and drink more water."]},
        2: {"c": ["Good chances of success at work; stuck work may get done.", "You may get a new responsibility or a good opportunity, so step forward.", "Your hard work will be praised and seniors will support you."],
            "m": ["Chances of financial gain; money that was stuck may come back.", "Signs of rising income; a deal may bring profit.", "You may get good news related to money."],
            "r": ["Family and partner will fully support you.", "You may meet someone special or get good news.", "Relationships will grow sweeter and the mood at home will be happy."],
            "h": ["Your mind will be happy and your body full of energy.", "Health will be good and you will feel fresh energy.", "You will get relief from an old problem."]}}


def ank_page(now, de):
    url = f"{SITE}/en/rashifal/ank-jyotish.html"
    dn = G.reduce9(sum(int(c) for c in now.strftime("%d%m%Y")))
    dlord, vlord = G.NUM_LORD[dn], G.VAAR_LORD[now.weekday()]
    REL = {"मित्रता": "friendly", "शत्रुता": "unfriendly", "सम संबंध": "neutral"}
    rows, best, care = [], [], []
    for n in range(1, 10):
        L = G.NUM_LORD[n]
        s1, r1 = G.rel(L, dlord)
        s2, r2 = G.rel(L, vlord)
        lv = 2 if s1 + s2 >= 2 else (1 if s1 + s2 >= 0 else 0)
        (best if lv == 2 else care if lv == 0 else []).append(str(n))
        dates = ", ".join(str(d) for d in range(n, 32, 9))
        lucky = ", ".join(str(k) for k in range(1, 10) if G.rel(L, G.NUM_LORD[k])[0] == 1)
        word = ("a day to be careful", "a mixed day", "an auspicious day")[lv]
        c, m, r, h = (NDAY[lv][k][(n + dn + q) % 3] for q, k in enumerate("cmrh"))
        rows.append(f'<div class="card" id="m{n}"><h2>Number {n} <small style="color:var(--muted);font-weight:400">(born on {dates})</small></h2>'
                    f'<div class="sub">Ruling planet: {PL_CAP[L]} • Today: <b>{word}</b> {"★" * (lv + 2)}{"☆" * (3 - lv)}</div>'
                    f'<p>People with number {n} are {NATURE[n]}. Your ruler {PL[L]} is {REL[r1]} with {PL[dlord]}, the ruler of today\'s number {dn}, and {REL[r2]} with {PL[vlord]}, the lord of {DAYS_EN[now.weekday()]}, so today is {word} for you.</p>'
                    f'<p><b>💼 Career:</b> {c} <b>💰 Money:</b> {m} <b>❤️ Relationships:</b> {r} <b>🩺 Health:</b> {h}</p>'
                    f'<p><b>Lucky numbers:</b> {lucky} &nbsp; <b>Lucky colour:</b> {NCOL[n]} &nbsp; <b>Remedy:</b> {NUPAY[n]}.</p></div>')
    head = f"A lucky day for numbers {', '.join(best)}" if best else "How the day looks for numbers 1 to 9"
    title = f"Numerology Today {de}: {head}"
    bch, bld = crumbs([("Daily Horoscope", f"{SITE}/en/rashifal/"), ("Numerology", None)])
    summ = (f"<b>In short:</b> The total number of today, {de}, is <b>{dn}</b> (ruled by {PL[dlord]}), and {DAYS_EN[now.weekday()]} is ruled by {PL[vlord]}. "
            + (f"The day is auspicious for numbers {', '.join(best)}. " if best else "") + (f"Numbers {', '.join(care)} should be careful today. " if care else ""))
    how = ('<div class="card"><h2>How to find your number (mulank)</h2><p>Add the digits of your date of birth (only the day) until one digit is left. For example, the 14th: 1+4 = <b>5</b>; '
           'the 29th: 2+9 = 11, then 1+1 = <b>2</b>. That is your number. Today\'s number is found by adding the full date (day + month + year).</p>'
           '<p>This is a general prediction based on the natural friendship of your number\'s ruling planet with the rulers of today\'s number and weekday.</p>'
           '<a class="btn red" href="/#kundli-banayen">Make a free kundli</a><a class="btn" href="' + G.wa("Namaste Pandit ji, I want to ask about numerology.") + '">Ask on WhatsApp</a></div>')
    body = (f'<div class="card">{bch}<h1>{title}</h1><div class="sub">Aaj Ka Ank Jyotish • Numbers 1 to 9</div>'
            f'{meta(url, title, de)}<div class="sum">{summ}</div><div class="rl">' + "".join(f'<a href="#m{n}">Number {n}</a>' for n in range(1, 10)) + '</div></div>' + "".join(rows) + how)
    desc = f"Today's numerology {de}: career, money, relationships, health, lucky numbers, lucky colour and remedy for numbers 1 to 9 – Pandit Raju Pathak."
    write("ank-jyotish.html", shell(title, desc, "ank-jyotish.html", body, [article_ld(title, now, url), bld]))


def index_page(en, now, de):
    url = f"{SITE}/en/rashifal/"
    cards = "".join(f'<div class="card"><h2><a href="{s}.html" style="text-decoration:none">{sym} {e} Horoscope ({ro})</a></h2><p>{esc((en[s]["aaj"]["text"])[:180])}… <a href="{s}.html">Read more →</a></p></div>'
                    for h, s, e, ro, sym, ak in RASHIS if en[s].get("aaj"))
    bch, bld = crumbs([("Daily Horoscope", None)])
    body = f'<div class="card">{bch}<h1>Today\'s Horoscope – {de}</h1><div class="sub">{DAYS_EN[now.weekday()]} • Daily Horoscope • Aaj Ka Rashifal • Pandit Raju Pathak</div>{rashi_links()}</div>{cards}'
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Today's Horoscope {de}", "url": url}, bld]
    write("index.html", shell(f"Today's Horoscope {de} – Aries to Pisces | Daily Horoscope – All Is Well Rashifal",
                              f"Daily horoscope for {de}: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius and Pisces – Pandit Raju Pathak.",
                              "index.html", body, ld))


# ---------------- Hindi daily pages: add the English button, hreflang and the saved-language redirect ----------------
def link_hindi_pages():
    for f in sorted(os.listdir(HI_DIR)):
        if not f.endswith(".html") or not os.path.exists(os.path.join(EN_DIR, f)):
            continue
        p = os.path.join(HI_DIR, f)
        t = open(p, encoding="utf-8").read()
        if 'class="lbtn"' in t:
            continue
        slug = "" if f == "index.html" else f
        hi_url, en_url = f"{SITE}/rashifal/{slug}", f"{SITE}/en/rashifal/{slug}"
        head = (f'<link rel="alternate" hreflang="hi" href="{hi_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{hi_url}">'
                f'<script>try{{if(localStorage.getItem("aiwr_lang")==="en")location.replace("{en_url}")}}catch(e){{}}</script><style>{LBTN_CSS}</style>')
        btn = f'<a class="lbtn" href="{en_url}" onclick="try{{localStorage.setItem(\'aiwr_lang\',\'en\')}}catch(e){{}}">English</a>'
        t = t.replace("</head>", head + "</head>", 1)
        t = t.replace("राशिफल • गोचर • पंचांग</small></div>", "राशिफल • गोचर • पंचांग</small></div>" + btn, 1)
        t = t.replace("<b>पंडित राजू पाठक</b></span>", '<b><a href="/author/">पंडित राजू पाठक</a></b></span>', 1)
        open(p, "w", encoding="utf-8").write(t)


def sitemap(iso):
    p = os.path.join(G.ROOT, "docs", "sitemap.xml")
    t = open(p, encoding="utf-8").read()
    add = "".join(f"  <url><loc>{SITE}/en/rashifal/{'' if f == 'index.html' else f}</loc><lastmod>{iso}</lastmod><changefreq>daily</changefreq></url>\n"
                  for f in sorted(os.listdir(EN_DIR)) if f.endswith(".html") and f"/en/rashifal/{'' if f == 'index.html' else f}<" not in t)
    if f"{SITE}/author/<" not in t:
        add += f"  <url><loc>{SITE}/author/</loc><lastmod>{iso}</lastmod><changefreq>monthly</changefreq></url>\n"
    open(p, "w", encoding="utf-8").write(t.replace("</urlset>", add + "</urlset>"))


RANGE = {}


def main():
    now = datetime.now(G.IST)
    de = f"{now.day} {G.MONTHS_EN[now.month - 1]} {now.year}"
    RANGE.update({"saptah": rng_en(now, 6), "mahina": rng_en(now, 29)})
    os.makedirs(EN_DIR, exist_ok=True)
    raw, en = {}, {}
    for h, s, *_ in RASHIS:
        raw[s], en[s] = {}, {}
        for p, _ in G.PERIODS:
            r = G.get(f"/rashifal/{G.urllib.parse.quote(h)}?period={p}") or {}
            raw[s][p] = r
            if r.get("text"):
                en[s][p] = to_en(r, p)
        if not en[s].get("aaj"):
            print("No data from the server, keeping the old English pages:", h)
            sys.exit(0)
    rashi_pages(en, now, de)
    period_page(en, now, de, "saptah", "saptahik.html", "Weekly Horoscope")
    period_page(en, now, de, "mahina", "masik.html", "Monthly Horoscope")
    love_page(raw, now, de)
    ank_page(now, de)
    index_page(en, now, de)
    link_hindi_pages()
    sitemap(now.strftime("%Y-%m-%d"))
    print("English pages done:", de)


if __name__ == "__main__":
    main()
