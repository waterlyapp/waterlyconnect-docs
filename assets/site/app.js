const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.14 }
);

document.querySelectorAll("[data-reveal]").forEach((element) => {
  revealObserver.observe(element);
});

document.querySelectorAll("[data-year]").forEach((element) => {
  element.textContent = new Date().getFullYear();
});

const driftElements = Array.from(document.querySelectorAll("[data-drift]"));

if (driftElements.length > 0 && window.matchMedia("(pointer: fine)").matches) {
  const resetTransforms = () => {
    driftElements.forEach((element) => {
      element.style.transform = "";
    });
  };

  window.addEventListener("mousemove", (event) => {
    const { innerWidth, innerHeight } = window;
    const x = event.clientX / innerWidth - 0.5;
    const y = event.clientY / innerHeight - 0.5;

    driftElements.forEach((element) => {
      const speed = Number(element.dataset.drift || 18);
      element.style.transform =
        `translate3d(${x * speed}px, ${y * speed}px, 0)`;
    });
  });

  window.addEventListener("mouseleave", resetTransforms);
}
