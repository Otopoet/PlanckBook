/*
 * PLANCK companion — client data layer (optional).
 * Injected into every station by build_site.py, alongside the "◂ PLANCK" badge.
 *
 *   • assigns a random, non-identifying visitor id (localStorage)
 *   • fires a non-blocking view beacon to api/track.php on open
 *   • renders a tiny feedback affordance (👍 / 👎 + optional note) -> api/feedback.php
 *
 * Everything here fails silently: if the API/database is absent or down, the
 * station works exactly as before. No personal data is collected.
 */
(function () {
  "use strict";

  // --- locate self + derive the API base from this script's own URL ----------
  var self = document.currentScript || document.querySelector("script[data-pk-code]");
  if (!self) return;
  var code = (self.getAttribute("data-pk-code") || "").trim();
  var apiBase = self.src.replace(/assets\/planck-companion\.js.*$/, "api/");

  // --- stable, anonymous visitor id ------------------------------------------
  var visitor;
  try {
    visitor = localStorage.getItem("pk_visitor");
    if (!visitor) {
      visitor = (crypto && crypto.randomUUID) ? crypto.randomUUID()
        : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
            var r = (Math.random() * 16) | 0;
            return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
          });
      localStorage.setItem("pk_visitor", visitor);
    }
  } catch (e) { visitor = null; } // private mode / storage blocked -> skip tracking

  var viaQr = /[?&]src=qr\b/.test(location.search) ? 1 : 0;

  function post(path, payload) {
    try {
      var body = JSON.stringify(payload);
      if (navigator.sendBeacon) {
        navigator.sendBeacon(apiBase + path, new Blob([body], { type: "application/json" }));
      } else {
        fetch(apiBase + path, { method: "POST", body: body, keepalive: true,
          headers: { "Content-Type": "application/json" } }).catch(function () {});
      }
    } catch (e) { /* ignore */ }
  }

  // --- view beacon ------------------------------------------------------------
  if (visitor) post("track.php", { code: code, type: "view", visitor: visitor, via_qr: viaQr });

  // --- minimal feedback widget -----------------------------------------------
  function buildFeedback() {
    var wrap = document.createElement("div");
    wrap.setAttribute("aria-label", "Feedback");
    wrap.style.cssText =
      "position:fixed;right:14px;bottom:14px;z-index:9999;font:13px/1.4 system-ui,sans-serif";

    var open = document.createElement("button");
    open.textContent = "Feedback";
    open.style.cssText =
      "background:var(--panel,#121833);color:var(--muted,#8a93b0);border:1px solid var(--line-2,rgba(180,190,220,.3));" +
      "border-radius:20px;padding:7px 14px;cursor:pointer;font:inherit";

    var panel = document.createElement("div");
    panel.hidden = true;
    panel.style.cssText =
      "background:var(--panel,#121833);border:1px solid var(--line-2,rgba(180,190,220,.3));border-radius:12px;" +
      "padding:14px;width:240px;color:var(--text,#e8ecf5);box-shadow:0 8px 30px rgba(0,0,0,.4)";
    panel.innerHTML =
      '<div style="margin-bottom:8px;color:var(--muted,#8a93b0)">Was this station clear?</div>' +
      '<div style="display:flex;gap:8px;margin-bottom:10px">' +
        '<button data-r="1" style="flex:1;cursor:pointer;border-radius:8px;border:1px solid var(--line-2,rgba(180,190,220,.3));background:transparent;color:inherit;padding:8px">👍</button>' +
        '<button data-r="-1" style="flex:1;cursor:pointer;border-radius:8px;border:1px solid var(--line-2,rgba(180,190,220,.3));background:transparent;color:inherit;padding:8px">👎</button>' +
      '</div>' +
      '<textarea rows="3" placeholder="Optional: a question or note…" ' +
        'style="width:100%;box-sizing:border-box;background:var(--bg,#0a0e1a);color:inherit;' +
        'border:1px solid var(--line-2,rgba(180,190,220,.3));border-radius:8px;padding:8px;resize:vertical;font:inherit"></textarea>' +
      '<button data-send style="margin-top:8px;width:100%;cursor:pointer;border:0;border-radius:8px;' +
        'background:var(--cyan,#28e0d0);color:#04201d;font-weight:600;padding:9px">Send</button>';

    var chosen = null;
    panel.addEventListener("click", function (ev) {
      var r = ev.target.getAttribute && ev.target.getAttribute("data-r");
      if (r) {
        chosen = parseInt(r, 10);
        Array.prototype.forEach.call(panel.querySelectorAll("[data-r]"), function (b) {
          b.style.borderColor = b === ev.target ? "var(--cyan,#28e0d0)" : "var(--line-2,rgba(180,190,220,.3))";
        });
      }
      if (ev.target.hasAttribute && ev.target.hasAttribute("data-send")) {
        var msg = panel.querySelector("textarea").value.trim();
        if (chosen === null && !msg) { return; }
        post("feedback.php", { code: code, visitor: visitor, rating: chosen, message: msg });
        panel.innerHTML = '<div style="color:var(--green,#5ad19a)">Thank you — noted.</div>';
        setTimeout(function () { wrap.remove(); }, 1600);
      }
    });

    open.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      open.hidden = !panel.hidden;
    });

    wrap.appendChild(open);
    wrap.appendChild(panel);
    document.body.appendChild(wrap);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildFeedback);
  } else {
    buildFeedback();
  }
})();
