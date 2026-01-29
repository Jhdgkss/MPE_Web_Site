document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".hero-carousel");
  if (!carousel) return;

  const slides = carousel.querySelectorAll(".hero-slide");

  // Dots container: support either existing container or create one
  let dotsContainer = carousel.querySelector(".hero-carousel__dots");
  if (!dotsContainer) {
    dotsContainer = document.createElement("div");
    dotsContainer.className = "hero-carousel__dots";
    carousel.appendChild(dotsContainer);
  }

  // Support multiple possible button class names (in case template changed)
  const prevBtn =
    carousel.querySelector(".hero-carousel__nav--prev") ||
    carousel.querySelector(".hero-carousel__prev") ||
    carousel.querySelector('[data-hero-prev]');

  const nextBtn =
    carousel.querySelector(".hero-carousel__nav--next") ||
    carousel.querySelector(".hero-carousel__next") ||
    carousel.querySelector('[data-hero-next]');

  let currentIndex = 0;
  let intervalId = null;
  const intervalTime = parseInt(carousel.dataset.interval, 10) || 8000;

  // Only build dots if we actually have multiple slides
  if (slides.length > 1) {
    // Clear any existing dots (avoid duplicates if JS runs twice)
    dotsContainer.innerHTML = "";

    slides.forEach((_, idx) => {
      const dot = document.createElement("button");

      // IMPORTANT: add both classes so either CSS naming works
      dot.classList.add("hero-carousel__dot", "hero-dot");
      if (idx === 0) dot.classList.add("is-active");

      dot.type = "button";
      dot.setAttribute("aria-label", `Go to slide ${idx + 1}`);
      dot.addEventListener("click", () => goToSlide(idx));

      dotsContainer.appendChild(dot);
    });
  }

  function goToSlide(index) {
    if (slides.length === 0) return;

    // Wrap index
    if (index < 0) index = slides.length - 1;
    if (index >= slides.length) index = 0;

    // Deactivate current slide
    const currentSlide = slides[currentIndex];
    if (currentSlide) {
      currentSlide.classList.remove("is-active");
      currentSlide.querySelectorAll("video").forEach((v) => v.pause());
    }

    // Activate new slide
    currentIndex = index;
    const newSlide = slides[currentIndex];
    if (newSlide) {
      newSlide.classList.add("is-active");

      // Try to play video if present (ignore autoplay restrictions)
      newSlide.querySelectorAll("video").forEach((v) => {
        try {
          v.currentTime = 0;
        } catch (e) {}
        v.play().catch(() => {});
      });
    }

    // Update dots
    const dots = dotsContainer ? dotsContainer.querySelectorAll(".hero-carousel__dot, .hero-dot") : [];
    if (dots.length) {
      dots.forEach((d) => d.classList.remove("is-active"));
      if (dots[currentIndex]) dots[currentIndex].classList.add("is-active");
    }

    resetTimer();
  }

  function startTimer() {
    if (slides.length > 1) {
      intervalId = setInterval(() => goToSlide(currentIndex + 1), intervalTime);
    }
  }

  function resetTimer() {
    if (intervalId) clearInterval(intervalId);
    startTimer();
  }

  // Wire up arrows
  if (prevBtn) prevBtn.addEventListener("click", () => goToSlide(currentIndex - 1));
  if (nextBtn) nextBtn.addEventListener("click", () => goToSlide(currentIndex + 1));

  // Init
  if (slides.length) {
    slides.forEach((s, i) => s.classList.toggle("is-active", i === 0));
    // Try play first slide video
    slides[0].querySelectorAll("video").forEach((v) => v.play().catch(() => {}));
  }

  startTimer();
});
