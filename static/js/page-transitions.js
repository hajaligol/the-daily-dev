/*
 * Page fade transitions.
 *
 * The Daily Dev is a classic multi-page Django site (every navigation is a
 * full page load). Rather than delaying navigation to wait for an exit
 * animation, this script lets the click navigate immediately (no lag) and
 * just leaves a flag in sessionStorage. A tiny inline snippet in <head>
 * (see the templates) reads that flag before the stylesheet is applied, so
 * the next page starts fading in the instant it paints.
 */
(function () {
  "use strict";

  function prefersReducedMotion() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function isPlainLeftClick(event) {
    return (
      event.button === 0 &&
      !event.metaKey &&
      !event.ctrlKey &&
      !event.shiftKey &&
      !event.altKey
    );
  }

  // Find a same-page, same-origin navigation link worth animating.
  function findNavLink(target) {
    var link = target && target.closest ? target.closest("a[href]") : null;
    if (!link) return null;

    var targetAttr = (link.getAttribute("target") || "").toLowerCase();
    if (targetAttr && targetAttr !== "_self") return null;
    if (link.hasAttribute("download")) return null;

    var href = link.getAttribute("href") || "";
    if (!href || href.charAt(0) === "#") return null;
    if (/^(mailto:|tel:|javascript:)/i.test(href)) return null;

    if (link.origin !== window.location.origin) return null;
    if (
      link.pathname === window.location.pathname &&
      link.search === window.location.search
    ) {
      return null;
    }

    return link;
  }

  document.addEventListener(
    "click",
    function (event) {
      if (event.defaultPrevented || !isPlainLeftClick(event)) return;

      var link = findNavLink(event.target);
      if (!link) return;

      var sheet = document.querySelector(".newspaper");
      if (!sheet || prefersReducedMotion()) return; // let the browser navigate normally

      // No preventDefault, no waiting — the browser navigates right away.
      // We just leave a flag for the next page to pick up on load.
      try {
        sessionStorage.setItem("fadeIn", "1");
      } catch (err) {
        /* sessionStorage unavailable (private mode, etc.) — harmless, just no fade-in */
      }

      sheet.classList.add("fade-out");
    },
    true
  );

  // If this page is restored from the back/forward cache (e.g. after
  // clicking the browser Back button), it comes back exactly as it was
  // left — including a lingering "fade-out" class whose animation ended
  // at opacity: 0. Nothing else fires in that case (it's not a fresh
  // load), so without this the page would just sit there invisible.
  window.addEventListener("pageshow", function (event) {
    var sheet = document.querySelector(".newspaper");
    if (!sheet) return;

    if (event.persisted || sheet.classList.contains("fade-out")) {
      sheet.classList.remove("fade-out");
    }
  });
})();