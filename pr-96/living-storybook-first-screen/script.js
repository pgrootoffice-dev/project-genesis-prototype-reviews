const world = document.querySelector('[data-living-world]');
const touchSurface = document.querySelector('[data-world-touch]');
const response = document.querySelector('[data-world-response]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

let responseTimer;
let presenceFrame;
let latestPointer;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setWorldPoint(clientX, clientY, trackDepth = true) {
  const rect = world.getBoundingClientRect();
  const x = clamp((clientX - rect.left) / rect.width, 0, 1);
  const y = clamp((clientY - rect.top) / rect.height, 0, 1);

  world.style.setProperty('--response-x', `${(x * 100).toFixed(2)}%`);
  world.style.setProperty('--response-y', `${(y * 100).toFixed(2)}%`);

  if (trackDepth && !reducedMotion.matches) {
    world.style.setProperty('--drift-x', ((x - 0.5) * 5).toFixed(2));
    world.style.setProperty('--drift-y', ((y - 0.5) * 4).toFixed(2));
  }
}

function returnToCalm() {
  world.classList.remove('is-aware');
  world.style.setProperty('--drift-x', '0');
  world.style.setProperty('--drift-y', '0');
}

function trackPointer(event) {
  if (event.pointerType === 'mouse' || event.pointerType === 'pen') {
    latestPointer = event;
    world.classList.add('is-aware');

    if (!presenceFrame) {
      presenceFrame = window.requestAnimationFrame(() => {
        setWorldPoint(latestPointer.clientX, latestPointer.clientY);
        presenceFrame = undefined;
      });
    }
  }
}

function respondAt(clientX, clientY) {
  setWorldPoint(clientX, clientY);

  world.classList.remove('is-responding');
  void response.offsetWidth;
  world.classList.add('is-responding');

  window.clearTimeout(responseTimer);
  responseTimer = window.setTimeout(() => {
    world.classList.remove('is-responding');
    returnToCalm();
  }, 1400);
}

function respondToPointer(event) {
  if (event.pointerType === 'mouse' && event.button !== 0) {
    return;
  }

  respondAt(event.clientX, event.clientY);
}

function respondToKeyboard(event) {
  if (event.detail !== 0) {
    return;
  }

  const rect = world.getBoundingClientRect();
  respondAt(rect.left + rect.width * 0.5, rect.top + rect.height * 0.42);
}

touchSurface.addEventListener('pointermove', trackPointer);
touchSurface.addEventListener('pointerdown', respondToPointer);
touchSurface.addEventListener('pointerleave', returnToCalm);
touchSurface.addEventListener('pointercancel', returnToCalm);
touchSurface.addEventListener('click', respondToKeyboard);
