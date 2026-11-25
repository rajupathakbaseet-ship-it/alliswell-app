"""लेखों की सूची (/lekh/ और /en/lekh/) विषय के अनुसार अपने आप बनाता है।
नया लेख docs/lekh/ या docs/en/lekh/ में डालते ही अगली रात की अपडेट में सूची में सही विषय के नीचे आ जाता है।
पेज का ऊपरी हिस्सा, साइडबार और फ़ुटर जैसे हैं वैसे ही रहते हैं – सिर्फ़ <main> के अंदर की सूची बदलती है।"""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDER = ["mesh", "vrishabh", "mithun", "kark", "singh", "kanya", "tula", "vrishchik", "dhanu", "makar", "kumbh", "meen"]
CATS = {
    "hi": [("rashifal", "♈ राशिफल 2027 – मेष से मीन", "12 राशियों और मूलांक 1-9 का पूरा साल"),
           ("vrat27", "🪔 व्रत-त्योहार 2027", "एकादशी, पूर्णिमा, अमावस्या और साल भर के पर्वों की तारीख़ें"),
           ("muhurat", "📅 शुभ मुहूर्त", "विवाह, गृह प्रवेश, मुंडन, नामकरण और वाहन ख़रीद के मुहूर्त"),
           ("gochar", "🪐 ग्रह गोचर और साढ़ेसाती", "ग्रहों का राशि परिवर्तन और 12 राशियों पर असर"),
           ("vrat26", "🕉️ व्रत-त्योहार 2026", "इस साल के बड़े पर्व – तारीख़, पूजा विधि और उपाय")],
    "en": [("rashifal", "♈ Horoscope 2027 – Aries to Pisces", "Full-year predictions for all 12 signs and numbers 1-9"),
           ("vrat27", "🪔 Hindu Festivals & Vrat 2027", "Ekadashi, Purnima, Amavasya and festival dates of the year"),
           ("muhurat", "📅 Shubh Muhurat", "Marriage, griha pravesh, mundan, naming and vehicle muhurat"),
           ("gochar", "🪐 Planetary Transits & Sade Sati", "Planet sign changes and their effect on 12 signs"),
           ("vrat26", "🕉️ Festivals 2026", "This year's major festivals – date, puja vidhi and remedies")]}


def cat(slug):
    if slug.endswith("-rashifal-2027") or slug.startswith("mulank-rashifal"):
        return "rashifal"
    if "muhurat" in slug:
        return "muhurat"
    if any(k in slug for k in ("gochar", "sadesati", "yuti", "grahan")) and "2027-list" not in slug:
        return "gochar" if "grahan" not in slug else "vrat27"
    if "2027" in slug:
        return "vrat27"
    return "vrat26"


def info(path):
    t = open(path, encoding="utf-8").read()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else re.search(r"<title>(.*?)</title>", t, re.S).group(1)
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    pub = re.search(r'"datePublished":\s*"([^"]+)"', t)
    return html.unescape(title), html.unescape(d.group(1) if d else ""), (pub.group(1) if pub else "")


def build(lang):
    d = os.path.join(ROOT, "docs", "lekh" if lang == "hi" else "en/lekh")
    idx = os.path.join(d, "index.html")
    if not os.path.exists(idx):
        return
    page = open(idx, encoding="utf-8").read()
    a, b = page.find("<main>"), page.find("</main>")
    if a < 0 or b < 0:
        return
    head = re.search(r'<main><div class="card">.*?</div></div>', page[a:b], re.S)
    top = head.group(0)[len("<main>"):] if head else ""
    groups = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html") or f == "index.html":
            continue
        slug = f[:-5]
        title, desc, pub = info(os.path.join(d, f))
        groups.setdefault(cat(slug), []).append((slug, f, title, desc, pub))
    more = "पूरा लेख पढ़ें →" if lang == "hi" else "Read full article →"
    jump = '<div class="card"><div class="rl">' + "".join(
        f'<a href="#{k}">{n}</a>' for k, n, _ in CATS[lang] if groups.get(k)) + "</div></div>"
    out = []
    for k, name, sub in CATS[lang]:
        items = groups.get(k)
        if not items:
            continue
        if k == "rashifal":
            items.sort(key=lambda x: (ORDER.index(x[0].split("-")[0]) if x[0].split("-")[0] in ORDER else 99))
        else:
            items.sort(key=lambda x: x[4], reverse=(k != "vrat27"))
        out.append(f'<div class="card" id="{k}"><h2 style="margin:0">{name}</h2><div class="sub">{sub}</div></div>')
        for slug, f, title, desc, pub in items:
            r = slug.split("-")[0]
            img = (f'<img class="hero" src="../{"../" if lang == "en" else ""}img/{r}-2027-sm.jpg" alt="{html.escape(title.split(":")[0])}" loading="lazy" width="640" height="360">'
                   if k == "rashifal" and r in ORDER else "")
            out.append(f'<div class="card"><a class="lk" href="{f}">{img}<h2>{html.escape(title)}</h2><p>{html.escape(desc)}</p>'
                       f'<b style="color:var(--red)">{more}</b></a></div>')
    new = "<main>" + top + jump + "".join(out)
    open(idx, "w", encoding="utf-8").write(page[:a] + new + page[b:])


def main():
    for lang in ("hi", "en"):
        try:
            build(lang)
        except Exception as e:  # सूची न बने तो भी बाकी अपडेट न रुके
            print("lekh index:", lang, e)


if __name__ == "__main__":
    main()
