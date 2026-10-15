/**
 * PawConnect - Master Client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const menuToggle = document.getElementById('menuToggle');
  const navMenu = document.getElementById('navMenu');
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('show');
      const isExpanded = navMenu.classList.contains('show');
      menuToggle.setAttribute('aria-expanded', isExpanded);
      menuToggle.innerHTML = isExpanded ? '✕' : '☰';
    });
  }

  // 2. Auto-dismiss Flash Alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // 3. Fallback for pet images that fail to load
  const petImages = document.querySelectorAll('.pet-card-media img, .pet-gallery-main img');
  const fallbackSvg = "data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300' fill='%23F4EFE6'%3E%3Crect width='400' height='300' fill='%23FAF6F0'/%3E%3Ccircle cx='200' cy='140' r='50' fill='%23E07A5F' opacity='0.2'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='38' fill='%23E07A5F'%3E🐾%3C/text%3E%3Ctext x='50%25' y='70%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='14' font-weight='bold' fill='%233D2B1F'%3EPawConnect Pet%3C/text%3E%3C/svg%3E";

  petImages.forEach(img => {
    img.addEventListener('error', () => {
      img.src = fallbackSvg;
    });
  });

  // 4. Client-side Live Filter (if pet cards are present on page)
  const liveSearchInput = document.getElementById('liveSearchInput');
  const petCards = document.querySelectorAll('.pet-card');
  const noPetsMsg = document.getElementById('noPetsLiveMatch');
  const visibleCountSpan = document.getElementById('visiblePetCount');

  if (liveSearchInput && petCards.length > 0) {
    liveSearchInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      let matchCount = 0;

      petCards.forEach(card => {
        const name = card.getAttribute('data-name')?.toLowerCase() || '';
        const breed = card.getAttribute('data-breed')?.toLowerCase() || '';
        const city = card.getAttribute('data-city')?.toLowerCase() || '';
        const species = card.getAttribute('data-species')?.toLowerCase() || '';

        const isMatch = name.includes(term) || breed.includes(term) || city.includes(term) || species.includes(term);

        if (isMatch) {
          card.style.display = 'flex';
          matchCount++;
        } else {
          card.style.display = 'none';
        }
      });

      if (visibleCountSpan) {
        visibleCountSpan.textContent = matchCount;
      }

      if (noPetsMsg) {
        noPetsMsg.style.display = matchCount === 0 ? 'block' : 'none';
      }
    });
  }
});
