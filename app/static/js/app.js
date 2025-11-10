/**
 * Main Application Logic
 * Global utilities and initialization
 */

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
  let toast = document.getElementById('toast');

  // Create toast if it doesn't exist
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast hidden';
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.className = `toast ${type}`;

  setTimeout(() => {
    toast.classList.add('hidden');
  }, duration);
}

/**
 * Mobile nav toggle
 */
document.addEventListener('DOMContentLoaded', function() {
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }

  // Close nav on link click (mobile)
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      navMenu?.classList.remove('active');
    });
  });

  // Update nav UI on page load
  Auth.updateNavUI();

  initThemeToggle();
  initBackToTopFab();
});

/**
 * Smooth scroll for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

/**
 * Form validation helper
 */
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Format currency (BDT)
 */
function formatCurrency(amount) {
  return `৳${parseFloat(amount).toLocaleString('en-BD', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Format percentage
 */
function formatPercent(value, decimals = 2) {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

const THEME_STORAGE_KEY = 'pf-theme';

function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  if (!toggleBtn) return;

  const icon = toggleBtn.querySelector('i');
  const label = toggleBtn.querySelector('.theme-toggle-label');
  const prefersLight = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;

  const setButtonState = (theme) => {
    toggleBtn.setAttribute('data-theme', theme);
    toggleBtn.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
    if (theme === 'light') {
      toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
      icon?.classList.remove('fa-moon');
      icon?.classList.add('fa-sun');
      if (label) label.textContent = 'Light';
    } else {
      toggleBtn.setAttribute('aria-label', 'Switch to light mode');
      icon?.classList.remove('fa-sun');
      icon?.classList.add('fa-moon');
      if (label) label.textContent = 'Dark';
    }
  };

  const applyTheme = (theme, persist = true) => {
    const normalized = theme === 'light' ? 'light' : 'dark';
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(`theme-${normalized}`);
    document.documentElement.setAttribute('data-theme', normalized);
    setButtonState(normalized);
    if (persist) {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, normalized);
      } catch (error) {
        /* noop */
      }
    }
  };

  const readStoredTheme = () => {
    try {
      return localStorage.getItem(THEME_STORAGE_KEY);
    } catch (error) {
      return null;
    }
  };

  const storedTheme = readStoredTheme();
  const initialTheme = storedTheme || (prefersLight?.matches ? 'light' : 'dark');
  applyTheme(initialTheme, false);

  toggleBtn.addEventListener('click', () => {
    const nextTheme = document.body.classList.contains('theme-light') ? 'dark' : 'light';
    applyTheme(nextTheme);
  });

  if (prefersLight?.addEventListener) {
    prefersLight.addEventListener('change', (event) => {
      if (readStoredTheme()) return;
      applyTheme(event.matches ? 'light' : 'dark', false);
    });
  } else if (prefersLight?.addListener) {
    prefersLight.addListener((event) => {
      if (readStoredTheme()) return;
      applyTheme(event.matches ? 'light' : 'dark', false);
    });
  }
}

/**
 * Back-to-top floating button handler
 */
function initBackToTopFab() {
  const fab = document.getElementById('backToTopFab');
  if (!fab) return;

  let isVisible = false;
  let ticking = false;
  let launchInProgress = false;

  const iconEl = fab.querySelector('.fab-icon i');
  const launchDuration = 1200;
  const prepDelay = 320;

  const setVisibility = () => {
    if (launchInProgress) {
      ticking = false;
      return;
    }

    const shouldShow = window.scrollY > 280;
    if (shouldShow && !isVisible) {
      fab.classList.remove('hidden');
      fab.setAttribute('aria-hidden', 'false');
      requestAnimationFrame(() => {
        fab.classList.add('fab-visible');
      });
      isVisible = true;
    } else if (!shouldShow && isVisible) {
      fab.classList.remove('fab-visible');
      fab.classList.add('hidden');
      fab.setAttribute('aria-hidden', 'true');
      resetFabState();
      isVisible = false;
    }

    ticking = false;
  };

  const handleScroll = () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(setVisibility);
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  setVisibility();

  fab.addEventListener('click', (event) => {
    event.preventDefault();
    if (launchInProgress) return;

    launchInProgress = true;
    fab.classList.add('launching');
    if (iconEl) {
      iconEl.classList.remove('fa-arrow-up');
      iconEl.classList.add('fa-rocket');
    }

    setTimeout(() => {
      fab.classList.add('in-flight');

      // Reset inline transform for animation loop
      fab.style.transition = 'none';
      fab.style.transform = 'translate3d(0, 0, 0)';

      startRocketScroll({
        duration: launchDuration,
        fab,
        ignitionHold: 0.12,
        accelerationWindow: 0.3,
        exitWindow: 0.58
      }, () => {
        setTimeout(() => {
          fab.classList.remove('in-flight', 'launching');
          fab.classList.add('hidden');
          fab.setAttribute('aria-hidden', 'true');
          resetFabState();
          isVisible = false;
          launchInProgress = false;
          setVisibility();
        }, 220);
      });
    }, prepDelay);
  });

  function resetFabState() {
    fab.classList.remove('launching', 'in-flight');
    fab.classList.remove('fab-visible');
    if (iconEl) {
      iconEl.classList.remove('fa-rocket');
      iconEl.classList.add('fa-arrow-up');
      iconEl.style.transform = '';
    }
    fab.style.removeProperty('transition');
    fab.style.transform = '';
  }
}

function startRocketScroll(config, onComplete) {
  const {
    duration = 1200,
    fab = null,
    ignitionHold = 0.12,
    accelerationWindow = 0.3,
    exitWindow = 0.58
  } = typeof config === 'number' ? { duration: config } : config;

  const startY = window.scrollY;
  if (startY <= 0) {
    if (fab) {
      fab.style.transform = 'translate3d(0, -160vh, 0)';
    }
    onComplete?.();
    return;
  }

  const root = document.documentElement;
  const body = document.body;
  const prevRootScroll = root.style.scrollBehavior;
  const prevBodyScroll = body.style.scrollBehavior;

  root.style.scrollBehavior = 'auto';
  body.style.scrollBehavior = 'auto';

  const finalize = () => {
    root.style.scrollBehavior = prevRootScroll;
    body.style.scrollBehavior = prevBodyScroll;
    onComplete?.();
  };

  const startTime = performance.now();
  const viewportHeight = window.innerHeight || 800;
  const holdOffset = viewportHeight * 0.32;
  const midOffset = viewportHeight * 0.55;
  const exitOffset = viewportHeight * 1.45;
  const totalTravel = holdOffset + midOffset + exitOffset;

  const easedIgnitionCap = 0.14;
  const fastPhaseCap = 0.965;

  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
  const easeOutExpo = (t) => (t >= 1) ? 1 : 1 - Math.pow(2, -10 * t);

  const calcScrollRatio = (progress) => {
    if (progress <= ignitionHold) {
      const ignitionProgress = progress / Math.max(ignitionHold, 0.0001);
      return easedIgnitionCap * easeOutCubic(ignitionProgress);
    }

    const accelEnd = ignitionHold + accelerationWindow;
    if (progress <= accelEnd) {
      const accelProgress = (progress - ignitionHold) / Math.max(accelerationWindow, 0.0001);
      return easedIgnitionCap + (fastPhaseCap - easedIgnitionCap) * easeOutExpo(accelProgress);
    }

    const exitProgress = (progress - accelEnd) / Math.max(exitWindow, 0.0001);
    return fastPhaseCap + (1 - fastPhaseCap) * easeOutCubic(exitProgress);
  };

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const scrollRatio = Math.min(calcScrollRatio(progress), 1);

    window.scrollTo(0, startY * (1 - scrollRatio));

    if (fab) {
      const offset = -totalTravel * scrollRatio;
      fab.style.transform = `translate3d(0, ${offset}px, 0)`;
    }

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      window.scrollTo(0, 0);
      if (fab) {
        fab.style.transform = 'translate3d(0, -160vh, 0)';
      }
      finalize();
    }
  }

  requestAnimationFrame(step);
}