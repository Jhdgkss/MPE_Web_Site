=document.addEventListener("DOMContentLoaded", function() {
    const carousel = document.querySelector('.hero-carousel');
    if (!carousel) return;
  
    const slides = carousel.querySelectorAll('.hero-slide');
    const dotsContainer = carousel.querySelector('.hero-carousel__dots');
    const prevBtn = carousel.querySelector('.hero-carousel__nav--prev');
    const nextBtn = carousel.querySelector('.hero-carousel__nav--next');
    
    let currentIndex = 0;
    let intervalId;
    const intervalTime = parseInt(carousel.dataset.interval) || 8000;
  
    // 1. Create Dots
    if (slides.length > 1) {
      slides.forEach((_, idx) => {
        const dot = document.createElement('button');
        dot.classList.add('hero-carousel__dot','hero-dot');
        if (idx === 0) dot.classList.add('is-active');
        dot.ariaLabel = `Go to slide ${idx + 1}`;
        dot.addEventListener('click', () => goToSlide(idx));
        dotsContainer.appendChild(dot);
      });
    }
  
    // 2. Main Slide Function
    function goToSlide(index) {
      // Handle wrapping
      if (index < 0) index = slides.length - 1;
      if (index >= slides.length) index = 0;
  
      // Clean up current slide (Pause videos to save CPU)
      const currentSlide = slides[currentIndex];
      currentSlide.classList.remove('is-active');
      const currentVideos = currentSlide.querySelectorAll('video');
      currentVideos.forEach(v => v.pause());
  
      // Update Index
      currentIndex = index;
  
      // Activate new slide
      const newSlide = slides[currentIndex];
      newSlide.classList.add('is-active');
      
      // Play videos in the new slide
      const newVideos = newSlide.querySelectorAll('video');
      newVideos.forEach(v => {
          v.currentTime = 0; // Optional: restart video from beginning
          v.play().catch(e => console.log("Autoplay prevented:", e));
      });
  
      // Update Dots
      const dots = dotsContainer.querySelectorAll('.hero-carousel__dot');
      if (dots.length > 0) {
        dots.forEach(d => d.classList.remove('is-active'));
        dots[currentIndex].classList.add('is-active');
      }
  
      resetTimer();
    }
  
    // 3. Timer Logic
    function startTimer() {
      if (slides.length > 1) {
        intervalId = setInterval(() => goToSlide(currentIndex + 1), intervalTime);
      }
    }
  
    function resetTimer() {
      clearInterval(intervalId);
      startTimer();
    }
  
    // 4. Event Listeners
    if (prevBtn) prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));
  
    // Initialize
    // Ensure the very first slide's video is playing
    const firstSlideVideos = slides[0].querySelectorAll('video');
    firstSlideVideos.forEach(v => v.play().catch(e => { /* ignore autoplay blocks */ }));
    
    startTimer();
  });