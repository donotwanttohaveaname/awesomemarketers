/* ==============================
   The Awesome Marketers — App JS
   ============================== */

// ===== NAV =====
const nav = document.getElementById('nav');
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

window.addEventListener('scroll', () => {
  nav.classList.toggle('nav--scrolled', window.scrollY > 50);
});

navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('active');
});

// Close nav on link click
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('active'));
});

// Mobile dropdown toggle
const dropdownToggle = document.querySelector('.nav__dropdown-toggle');
if (dropdownToggle) {
  dropdownToggle.addEventListener('click', () => {
    const dropdown = dropdownToggle.closest('.nav__dropdown');
    dropdown.classList.toggle('open');
  });
}

// ===== COUNTER ANIMATION =====
function animateCounters() {
  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(counter => {
    const target = parseInt(counter.dataset.count);
    const duration = 2000;
    const start = performance.now();

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = Math.round(eased * target);
      counter.textContent = current.toLocaleString();
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  });
}

// Trigger counters when hero is visible
const heroObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounters();
      heroObserver.disconnect();
    }
  });
}, { threshold: 0.3 });

const heroStats = document.querySelector('.hero__stats');
if (heroStats) heroObserver.observe(heroStats);

// ===== ROTATING STAT LABEL =====
const rotatingLabel = document.getElementById('rotatingLabel');
if (rotatingLabel) {
  const labels = [
    'marketers on Slack',
    'marketers sharing job leads right now',
    'marketers who actually reply to questions',
    'marketers venting about bad briefs',
    'marketers celebrating each other\'s wins',
    'marketers arguing about attribution models',
    'marketers who know what UTM stands for',
    'marketers giving honest feedback on CVs',
    'marketers who\'ve survived a rebrand',
    'marketers recommending tools nobody asked about',
    'marketers debating SEO vs paid',
    'marketers posting "anyone hiring?"',
    'marketers who read the whole Slack thread'
  ];
  let labelIndex = 0;

  setInterval(() => {
    rotatingLabel.classList.add('fade-out');
    setTimeout(() => {
      labelIndex = (labelIndex + 1) % labels.length;
      rotatingLabel.textContent = labels[labelIndex];
      rotatingLabel.classList.remove('fade-out');
    }, 500);
  }, 4000);
}

// ===== FIREWORK ON JOIN BUTTON HOVER =====
document.querySelectorAll('.hero__actions .btn--primary, .btn--nav').forEach(btn => {
  btn.addEventListener('mouseenter', (e) => {
    const rect = btn.getBoundingClientRect();
    const colors = ['#FFB452', '#A615FF', '#FF6B9D', '#FFD700', '#FF8C42'];
    for (let i = 0; i < 12; i++) {
      const particle = document.createElement('span');
      particle.className = 'sparkle-particle';
      particle.style.left = (rect.left + rect.width / 2) + 'px';
      particle.style.top = (rect.top + rect.height / 2) + 'px';
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];
      const angle = (Math.PI * 2 * i) / 12 + (Math.random() - 0.5) * 0.5;
      const distance = 30 + Math.random() * 40;
      particle.style.setProperty('--dx', Math.cos(angle) * distance + 'px');
      particle.style.setProperty('--dy', Math.sin(angle) * distance + 'px');
      particle.style.animationDuration = (0.4 + Math.random() * 0.3) + 's';
      document.body.appendChild(particle);
      particle.addEventListener('animationend', () => particle.remove());
    }
  });
});

// ===== SCROLL ANIMATIONS =====
const animateObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      animateObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.about__card, .manifesto__item, .video__card, .mentorship__info-card').forEach(el => {
  animateObserver.observe(el);
});

// ===== YOUTUBE VIDEOS =====
// Uses YouTube RSS feed via a public CORS proxy or the YouTube Data API
// Channel ID: UCpe-pB4GRuQlOddwWwCM8AQ

const YOUTUBE_CHANNEL_ID = 'UCpe-pB4GRuQlOddwWwCM8AQ';
const VIDEOS_COUNT = 3;

async function loadYouTubeVideos() {
  const grid = document.getElementById('videosGrid');

  try {
    // Try YouTube RSS feed via public proxy
    const feedUrl = `https://www.youtube.com/feeds/videos.xml?channel_id=${YOUTUBE_CHANNEL_ID}`;
    const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(feedUrl)}`;

    const response = await fetch(proxyUrl);
    if (!response.ok) throw new Error('Feed fetch failed');

    const xmlText = await response.text();
    const parser = new DOMParser();
    const xml = parser.parseFromString(xmlText, 'text/xml');

    const entries = xml.querySelectorAll('entry');
    if (entries.length === 0) throw new Error('No videos found');

    const videos = [];
    for (let i = 0; i < Math.min(VIDEOS_COUNT, entries.length); i++) {
      const entry = entries[i];
      const videoId = entry.querySelector('id').textContent.split(':').pop();
      const title = entry.querySelector('title').textContent;
      const published = entry.querySelector('published').textContent;
      videos.push({ videoId, title, published });
    }

    renderVideos(videos);
  } catch (err) {
    console.log('RSS fetch failed, using fallback embeds:', err.message);
    renderFallbackVideos();
  }
}

function renderVideos(videos) {
  const grid = document.getElementById('videosGrid');
  grid.innerHTML = videos.map(video => `
    <div class="video__card">
      <div class="video__embed">
        <iframe
          src="https://www.youtube.com/embed/${video.videoId}"
          title="${escapeHtml(video.title)}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy">
        </iframe>
      </div>
      <div class="video__info">
        <h3 class="video__title">${escapeHtml(video.title)}</h3>
        <p class="video__date">${formatDate(video.published)}</p>
      </div>
    </div>
  `).join('');
}

function renderFallbackVideos() {
  // Fallback: embed the channel's latest uploads playlist
  const grid = document.getElementById('videosGrid');
  // UU playlist = channel uploads (replace UC with UU in channel ID)
  const playlistId = YOUTUBE_CHANNEL_ID.replace('UC', 'UU');
  grid.innerHTML = `
    <div class="video__card" style="grid-column: 1 / -1;">
      <div class="video__embed" style="padding-top: 40%;">
        <iframe
          src="https://www.youtube.com/embed/videoseries?list=${playlistId}"
          title="Latest videos from The Awesome Marketers"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy">
        </iframe>
      </div>
      <div class="video__info">
        <h3 class="video__title">Latest webinars and talks</h3>
        <p class="video__date">Watch our recorded sessions</p>
      </div>
    </div>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ===== LINKEDIN EVENTS (via SociableKIT) =====
// SociableKIT pulls events from your LinkedIn company page in real-time.
// Setup instructions:
// 1. Go to https://www.sociablekit.com/app/
// 2. Create a "LinkedIn Page Events" widget
// 3. Connect it to: https://fi.linkedin.com/company/the-awesome-marketers
// 4. Copy the embed ID and replace YOUR_SOCIABLEKIT_EMBED_ID in index.html
// Free tier: auto-refreshes, shows upcoming events, styled to match your site

function loadEvents() {
  const widget = document.getElementById('eventsWidget');
  const fallback = document.getElementById('eventsFallback');
  if (!widget || !fallback) return;
  const skWidget = widget.querySelector('.sk-ww-linkedin-page-event');
  const embedId = skWidget ? skWidget.dataset.embedId : '';

  if (embedId && embedId !== 'YOUR_SOCIABLEKIT_EMBED_ID') {
    // Load the SociableKIT script to activate the widget
    const script = document.createElement('script');
    script.src = 'https://widgets.sociablekit.com/linkedin-page-events/widget.js';
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    // If widget fails to render within 10s, show fallback
    setTimeout(() => {
      if (skWidget && skWidget.children.length === 0) {
        widget.style.display = 'none';
        fallback.style.display = 'block';
      }
    }, 10000);
  } else {
    // No widget ID configured yet — show LinkedIn fallback
    widget.style.display = 'none';
    fallback.style.display = 'block';
  }
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  loadYouTubeVideos();
  loadEvents();
});
