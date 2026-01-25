/**
 * Lightweight hero carousel (no dependencies).
 * - Auto-rotates
 * - Prev/Next
 * - Dots
 */
(function () {
  const carousel = document.querySelector(".hero-carousel");
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll(".hero-slide"));
  const dotsWrap = carousel.querySelector(".hero-carousel__dots");
  const prevBtn = carousel.querySelector(".hero-carousel__nav--prev");
  const nextBtn = carousel.querySelector(".hero-carousel__nav--next");

  if (!slides.length) return;

  const intervalMs = parseInt(carousel.getAttribute("data-interval") || "7000", 10);
  let idx = 0;
  let timer = null;

  function setActive(newIdx) {
    idx = (newIdx + slides.length) % slides.length;
    slides.forEach((s, i) => s.classList.toggle("is-active", i === idx));

    if (dotsWrap) {
      dotsWrap.querySelectorAll(".hero-dot").forEach((d, i) => d.classList.toggle("is-active", i === idx));
    }
  }

  function buildDots() {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = "";
    slides.forEach((_, i) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "hero-dot" + (i === 0 ? " is-active" : "");
      dot.setAttribute("aria-label", `Go to slide ${i + 1}`);
      dot.addEventListener("click", () => {
        setActive(i);
        restart();
      });
      dotsWrap.appendChild(dot);
    });
  }

  function next() { setActive(idx + 1); }
  function prev() { setActive(idx - 1); }

  function start() {
    if (timer) return;
    timer = window.setInterval(next, intervalMs);
  }

  function stop() {
    if (!timer) return;
    window.clearInterval(timer);
    timer = null;
  }

  function restart() {
    stop();
    start();
  }

  buildDots();
  setActive(0);
  start();

  if (prevBtn) prevBtn.addEventListener("click", () => { prev(); restart(); });
  if (nextBtn) nextBtn.addEventListener("click", () => { next(); restart(); });

  // Pause on hover (desktop)
  carousel.addEventListener("mouseenter", stop);
  carousel.addEventListener("mouseleave", start);

  // Basic keyboard support
  carousel.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") { prev(); restart(); }
    if (e.key === "ArrowRight") { next(); restart(); }
  });
})();