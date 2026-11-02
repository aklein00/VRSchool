const conceptDialog = document.querySelector('#environment-lightbox');
const conceptLinks = [...document.querySelectorAll('[data-environment-art]')];
if (conceptDialog && typeof conceptDialog.showModal === 'function') {
  const image = document.querySelector('#environment-lightbox-image');
  let current = 0, opener = null, previousOverflow = '';
  function showConcept(index) {
    current = (index + conceptLinks.length) % conceptLinks.length;
    const link = conceptLinks[current];
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    document.querySelector('#environment-lightbox-title').textContent = link.dataset.title;
    document.querySelector('#environment-lightbox-description').textContent = link.dataset.description;
    const count = `${current + 1} / ${conceptLinks.length} — ENVIRONMENT CONCEPTS`;
    document.querySelector('#environment-lightbox-count').textContent = count;
    document.querySelector('#environment-lightbox-status').textContent = `${link.dataset.title}, ${current + 1} of ${conceptLinks.length}`;
  }
  conceptLinks.forEach((link, index) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    opener = link;
    showConcept(index);
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    conceptDialog.showModal();
    document.querySelector('#environment-lightbox-close').focus();
  }));
  document.querySelector('#environment-lightbox-close').addEventListener('click', () => conceptDialog.close());
  document.querySelector('#environment-lightbox-prev').addEventListener('click', () => showConcept(current - 1));
  document.querySelector('#environment-lightbox-next').addEventListener('click', () => showConcept(current + 1));
  conceptDialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); showConcept(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  conceptDialog.addEventListener('click', event => { if (event.target === conceptDialog) { const r = conceptDialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) conceptDialog.close(); } });
  conceptDialog.addEventListener('close', () => { document.body.style.overflow = previousOverflow; opener?.focus({ preventScroll: true }); });
}
