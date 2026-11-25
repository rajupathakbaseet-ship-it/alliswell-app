/* लेखों में "संबंधित वीडियो" – All Is Well Rashifal चैनल के असली वीडियो।
   <div class="vrel" data-k="शब्द1,शब्द2" data-id="वीडियो-ID (वैकल्पिक)"></div>
   1) सर्वर (/videos) से चैनल के ताज़ा वीडियो में से विषय से मिलता वीडियो चुनता है;
   2) न मिले तो data-id वाला वीडियो; 3) वह भी न हो तो चैनल की uploads प्लेलिस्ट।
   वीडियो तभी लोड होता है जब पाठक क्लिक करे – इससे पेज हल्का रहता है। */
(function () {
  var API = "https://alliswell-server.onrender.com", CH = "UCDVq_FHNYxeeCkKBhunB0og";
  var boxes = document.querySelectorAll(".vrel");
  if (!boxes.length) return;
  var en = location.pathname.indexOf("/en/") === 0;
  var css = document.createElement("style");
  css.textContent = ".vrel{margin:18px 0}.vrel h2{margin-bottom:8px}.vrel .vp{position:relative;display:block;width:100%;aspect-ratio:16/9;background:#000 center/cover no-repeat;border:0;border-radius:12px;cursor:pointer;overflow:hidden;padding:0}" +
    ".vrel .vp:after{content:'▶';position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:72px;height:50px;line-height:50px;border-radius:12px;background:#c4161c;color:#fff;font-size:26px;text-align:center}" +
    ".vrel iframe{width:100%;aspect-ratio:16/9;border:0;border-radius:12px;display:block}.vrel .vt{display:block;margin-top:6px;font-weight:700;color:#7a1e2c}";
  document.head.appendChild(css);
  function draw(b, id, title) {
    var src = id ? "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0"
      : "https://www.youtube-nocookie.com/embed/videoseries?list=UU" + CH.slice(2) + "&autoplay=1&rel=0";
    var h = '<h2>' + (en ? "▶ Related video – Pandit Raju Pathak" : "▶ संबंधित वीडियो – पंडित राजू पाठक") + '</h2>' +
      '<button type="button" class="vp" aria-label="' + (en ? "Play video" : "वीडियो चलाएँ") + '"' +
      (id ? ' style="background-image:url(https://i.ytimg.com/vi/' + id + '/hqdefault.jpg)"' : ' style="background:linear-gradient(135deg,#4a0f19,#b3121f)"') + '></button>' +
      '<a class="vt" href="' + (id ? "https://www.youtube.com/watch?v=" + id : "https://www.youtube.com/channel/" + CH) + '" target="_blank" rel="noopener">' +
      (title ? title.replace(/[<>&"]/g, "") : (en ? "Watch on YouTube – All Is Well Rashifal" : "YouTube पर देखें – All Is Well Rashifal")) + '</a>';
    b.innerHTML = h;
    b.querySelector(".vp").onclick = function () {
      var f = document.createElement("iframe");
      f.src = src; f.allow = "autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen = true; f.title = title || "All Is Well Rashifal";
      this.replaceWith(f);
    };
  }
  function pick(list, keys) {
    for (var i = 0; i < list.length; i++) {
      var t = (list[i].title || "").toLowerCase();
      for (var k = 0; k < keys.length; k++) if (keys[k] && t.indexOf(keys[k]) >= 0) return list[i];
    }
    return null;
  }
  boxes.forEach(function (b) { draw(b, b.getAttribute("data-id"), b.getAttribute("data-t")); });
  var ctl = window.AbortController ? new AbortController() : null;
  if (ctl) setTimeout(function () { ctl.abort(); }, 9000);
  fetch(API + "/videos?limit=50", ctl ? { signal: ctl.signal } : {}).then(function (r) { return r.json(); }).then(function (d) {
    var list = (d && (d.videos || d)) || [];
    if (!list.length) return;
    boxes.forEach(function (b) {
      var keys = (b.getAttribute("data-k") || "").toLowerCase().split(",").map(function (s) { return s.trim(); });
      var v = pick(list, keys);
      if (v && v.id && v.id !== b.getAttribute("data-id")) draw(b, v.id, v.title);
    });
  }).catch(function () {});
})();
