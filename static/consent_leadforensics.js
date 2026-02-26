/* MPE Cookie Consent + Lead Forensics loader + click/event tracking
   - UK compliant: tracking loads ONLY after explicit consent.
   - Tracks page views (Lead Forensics default) + key events (clicks/submits) as pseudo-page views.
*/

(function () {
  "use strict";

  const CFG = (window.MPE_TRACKING || {});
  const CONSENT_COOKIE = CFG.consentCookieName || "mpe_cookie_consent";
  const CONSENT_ACCEPTED = "accepted";
  const CONSENT_REJECTED = "rejected";

  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }

  function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/; SameSite=Lax`;
  }

  function slugify(str) {
    return (str || "")
      .toString()
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9\-]/g, "")
      .replace(/\-\-+/g, "-")
      .slice(0, 60);
  }

  function safeText(el) {
    if (!el) return "";
    return (el.getAttribute("data-lf-label") || el.getAttribute("aria-label") || el.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 80);
  }

  // --- Lead Forensics loader (after consent) ---
  let lfLoaded = false;

  function injectScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.async = true;
      s.src = src;
      s.onload = () => resolve(true);
      s.onerror = () => reject(new Error("Failed to load script: " + src));
      document.head.appendChild(s);
    });
  }

  function ensureLeadForensics() {
    if (lfLoaded) return Promise.resolve(true);
    lfLoaded = true;

    // Main tracking script
    const src = CFG.leadForensicsScriptSrc;
    if (!src) return Promise.resolve(false);

    return injectScript(src).then(() => {
      // Add noscript pixel equivalent for cases where LF uses it (we keep it as an image request).
      try {
        const img = new Image();
        img.alt = "";
        img.style.display = "none";
        img.src = CFG.leadForensicsPixelSrc || "";
      } catch (e) {
        // ignore
      }

      // Custom event tracking function (pseudo-page views)
      // Lead Forensics guidance uses track_load(page_URL, page_title)
      if (!window.track_load) {
        window.track_load = function track_load(docloc, doctit) {
          try {
            const trk_sw = encodeURIComponent(String(screen.width).substring(0, 6));
            const trk_sh = encodeURIComponent(String(screen.height).substring(0, 6));
            const trk_ref = encodeURIComponent(String(document.referrer || "").substring(0, 1100));
            const trk_loc = encodeURIComponent(String(docloc || window.location.href).substring(0, 1100));
            let trk_tit = String(doctit || document.title || "").substring(0, 200);
            trk_tit = trk_tit.replace(/[\u00a0]/g, " ");
            trk_tit = trk_tit.replace(/[\u2122]/g, "");
            trk_tit = trk_tit.replace(/[\u00ae]/g, "");
            trk_tit = encodeURIComponent(trk_tit);
            const trk_agn = encodeURIComponent(String(navigator.appName || "").substring(0, 100));
            const trk_dom = encodeURIComponent(String(document.domain || "").substring(0, 200));
            const trk_user = encodeURIComponent(String(CFG.leadForensicsAccountId || "102273"));

            const endpoint = CFG.leadForensicsCaptureEndpoint || "https://secure.leadforensics.com/Track/Capture.aspx";
            const url = `${endpoint}?trk_user=${trk_user}&trk_sw=${trk_sw}&trk_sh=${trk_sh}&trk_ref=${trk_ref}&trk_tit=${trk_tit}&trk_loc=${trk_loc}&trk_agn=${trk_agn}&trk_dom=${trk_dom}`;

            const i = new Image(1, 1);
            i.src = url;
          } catch (e) {
            // ignore
          }
        };
      }

      return true;
    }).catch(() => false);
  }

  function hasConsent() {
    return getCookie(CONSENT_COOKIE) === CONSENT_ACCEPTED;
  }

  // --- Cookie banner ---
  function showBannerIfNeeded() {
    const banner = document.getElementById("cookie-banner");
    if (!banner) return;

    const existing = getCookie(CONSENT_COOKIE);
    if (existing === CONSENT_ACCEPTED || existing === CONSENT_REJECTED) {
      banner.hidden = true;
      return;
    }
    banner.hidden = false;
  }

  function wireBannerButtons() {
    const accept = document.getElementById("cookie-accept");
    const reject = document.getElementById("cookie-reject");
    const banner = document.getElementById("cookie-banner");

    if (accept) {
      accept.addEventListener("click", () => {
        setCookie(CONSENT_COOKIE, CONSENT_ACCEPTED, 180);
        if (banner) banner.hidden = true;
        ensureLeadForensics();
      });
    }

    if (reject) {
      reject.addEventListener("click", () => {
        setCookie(CONSENT_COOKIE, CONSENT_REJECTED, 180);
        if (banner) banner.hidden = true;
        // Do not load tracking
      });
    }
  }

  // --- Event tracking ---
  function lfTrack(label, url) {
    if (!hasConsent()) return;
    // Make sure LF is loaded (best-effort) then send event.
    ensureLeadForensics().finally(() => {
      if (typeof window.track_load === "function") {
        window.track_load(url, label);
      }
    });
  }

  function shouldTrackElement(el) {
    if (!el) return false;
    if (el.hasAttribute("data-lf-ignore")) return false;

    // Explicit opt-in
    if (el.hasAttribute("data-lf-track")) return true;

    // Reasonable defaults: buttons / prominent CTAs
    const tag = (el.tagName || "").toLowerCase();
    if (tag === "button") return true;
    if (tag === "a") {
      const cls = (el.className || "").toString();
      if (cls.includes("btn")) return true;
      if (el.closest("nav")) return true; // nav clicks are useful
    }
    if (tag === "input" && (el.type || "").toLowerCase() === "submit") return true;

    return false;
  }

  function buildEventUrl(el, label) {
    try {
      if (el && el.tagName && el.tagName.toLowerCase() === "a") {
        const href = el.getAttribute("href") || "";
        if (href && !href.startsWith("#") && !href.startsWith("javascript:")) {
          // Convert relative URL to absolute for LF
          const u = new URL(href, window.location.origin);
          return u.toString();
        }
      }
    } catch (e) {
      // ignore
    }

    const hash = slugify(label || "event");
    return window.location.href.split("#")[0] + "#" + hash;
  }

  function bindGlobalClickTracking() {
    document.addEventListener("click", (ev) => {
      const target = ev.target;
      if (!target) return;

      const el = target.closest("a, button, input[type=submit]");
      if (!el) return;

      if (!shouldTrackElement(el)) return;

      const label = safeText(el) || "Click";
      const url = buildEventUrl(el, label);
      lfTrack(label, url);
    }, { capture: true });
  }

  function bindFormTracking() {
    document.addEventListener("submit", (ev) => {
      const form = ev.target;
      if (!form || !form.tagName || form.tagName.toLowerCase() !== "form") return;

      // Don't include any field values; just track the page + form purpose.
      const label = (form.getAttribute("data-lf-label") || form.getAttribute("name") || form.getAttribute("id") || "Form Submit")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 80);

      const url = window.location.href.split("#")[0] + "#" + slugify(label);
      lfTrack(label, url);
    }, { capture: true });
  }

  function init() {
    showBannerIfNeeded();
    wireBannerButtons();

    // If user already consented, load immediately
    if (hasConsent()) {
      ensureLeadForensics();
    }

    bindGlobalClickTracking();
    bindFormTracking();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
