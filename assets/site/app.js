// Reveal on scroll
const revealObs = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); revealObs.unobserve(e.target); }
  }),
  { threshold: 0.1 }
);
document.querySelectorAll('[data-reveal]').forEach(el => revealObs.observe(el));

// Dynamic year
document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

// Scroll spy for API sidebar
(function () {
  const links = document.querySelectorAll('.sidebar-link[href^="#"]');
  if (!links.length) return;

  const targets = Array.from(links)
    .map(l => document.querySelector(l.getAttribute('href')))
    .filter(Boolean);

  const activate = (id) => {
    links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + id));
  };

  const obs = new IntersectionObserver(
    (entries) => {
      entries.forEach(e => { if (e.isIntersecting) activate(e.target.id); });
    },
    { rootMargin: '-10% 0px -78% 0px' }
  );

  targets.forEach(t => obs.observe(t));
  if (targets[0]) activate(targets[0].id);
})();
