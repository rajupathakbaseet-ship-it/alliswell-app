/* All Is Well Rashifal – हल्का Search Box (हर पेज के Header में अपने आप जुड़ता है)
   यह push.js से लोड होता है। खोज के नतीजे /khoj/ पेज पर /search.json से दिखते हैं। */
(function () {
  try {
    if (document.getElementById("aiwr-srch") || location.pathname.indexOf("/khoj/") === 0) return;
    var en = location.pathname.indexOf("/en/") === 0 ||
      (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
    try { if (location.pathname === "/" || location.pathname === "/index.html") en = localStorage.getItem("aiwr_lang") === "en"; } catch (e) {}
    var box = document.querySelector(".mast .w, .mast .wrap");
    if (!box) return;
    var css = document.createElement("style");
    css.textContent = "#aiwr-srch{display:flex;margin-left:10px;flex:0 1 230px;min-width:150px}" +
      "#aiwr-srch input{flex:1;min-width:0;border:1px solid #d9c9b4;border-right:0;border-radius:20px 0 0 20px;padding:6px 12px;font:inherit;font-size:15px;background:#fff}" +
      "#aiwr-srch button{border:0;border-radius:0 20px 20px 0;background:#7a1e2c;color:#fff;padding:0 12px;font-size:15px;cursor:pointer}" +
      "@media(max-width:860px){.mast .w,.mast .wrap{flex-wrap:wrap}#aiwr-srch{order:9;flex:1 1 100%;margin:6px 0 0}}";
    document.head.appendChild(css);
    var f = document.createElement("form");
    f.id = "aiwr-srch"; f.action = en ? "/khoj/?lang=en" : "/khoj/"; f.method = "get"; f.setAttribute("role", "search");
    f.innerHTML = '<input type="search" name="q" required aria-label="' + (en ? "Search the site" : "वेबसाइट में खोजें") +
      '" placeholder="' + (en ? "Search: Aries 2027, Ekadashi…" : "खोजें: मेष 2027, एकादशी…") + '"><button type="submit" aria-label="' +
      (en ? "Search" : "खोजें") + '">🔍</button>';
    if (en) { var h = document.createElement("input"); h.type = "hidden"; h.name = "lang"; h.value = "en"; f.appendChild(h); f.action = "/khoj/"; }
    box.appendChild(f);
  } catch (e) {}
})();
