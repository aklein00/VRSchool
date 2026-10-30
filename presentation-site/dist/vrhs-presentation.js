const printButton = document.querySelector('#print-guide');
printButton?.addEventListener('click', () => window.print());

const voiceGallery = document.querySelector('#voice-gallery');
if (voiceGallery) {
  const controls = document.querySelector('.voice-gallery-controls');
  const previous = document.querySelector('[data-voice-scroll="previous"]');
  const next = document.querySelector('[data-voice-scroll="next"]');
  const updateControls = () => {
    previous.disabled = voiceGallery.scrollLeft <= 1;
    next.disabled = voiceGallery.scrollLeft + voiceGallery.clientWidth >= voiceGallery.scrollWidth - 1;
  };
  controls.hidden = false;
  controls.addEventListener('click', event => {
    const direction = event.target.closest('[data-voice-scroll]')?.dataset.voiceScroll;
    if (!direction) return;
    voiceGallery.scrollBy({
      left: voiceGallery.clientWidth * 0.8 * (direction === 'previous' ? -1 : 1),
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
    });
  });
  voiceGallery.addEventListener('scroll', updateControls, { passive: true });
  window.addEventListener('resize', updateControls);
  updateControls();

  voiceGallery.addEventListener('play', event => {
    if (!(event.target instanceof HTMLAudioElement)) return;
    voiceGallery.querySelectorAll('audio').forEach(player => {
      if (player !== event.target) player.pause();
    });
  }, true);

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) voiceGallery.querySelectorAll('audio').forEach(player => player.pause());
  });
}
