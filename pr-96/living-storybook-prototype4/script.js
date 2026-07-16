const world = document.querySelector('[data-living-world]');
const touchSurface = document.querySelector('[data-world-touch]');
const response = document.querySelector('[data-world-response]');
const reply = document.querySelector('[data-world-reply]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const WORLD_BREATH_MS = 8000;
const SILENCE_PHASE_MS = 1200;

let responseTimer;
let arrivalTimer;
let silenceTimer;
let presenceFrame;
let latestPointer;
let nextAnswerAt = 0;

world.dataset.rulePhase = 'living';
world.dataset.lastChoice = 'none';
world.dataset.worldBreathMs = String(WORLD_BREATH_MS);

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setWorldPoint(clientX, clientY, trackDepth = true) {
  const rect = world.getBoundingClientRect();
  const x = clamp((clientX - rect.left) / rect.width, 0, 1);
  const y = clamp((clientY - rect.top) / rect.height, 0, 1);

  world.style.setProperty('--response-x', `${(x * 100).toFixed(2)}%`);
  world.style.setProperty('--response-y', `${(y * 100).toFixed(2)}%`);
  const replyX = (x - 0.68) * rect.width;
  const replyY = (y - 0.39) * rect.height;
  const replyDistance = Math.hypot(replyX, replyY) || 1;
  const curve = Math.min(12, replyDistance * 0.06);
  const bendX = replyX * 0.48 - (replyY / replyDistance) * curve;
  const bendY = replyY * 0.48 + (replyX / replyDistance) * curve;

  world.style.setProperty('--reply-dx', `${replyX.toFixed(2)}px`);
  world.style.setProperty('--reply-dy', `${replyY.toFixed(2)}px`);
  world.style.setProperty('--reply-bend-x', `${bendX.toFixed(2)}px`);
  world.style.setProperty('--reply-bend-y', `${bendY.toFixed(2)}px`);

  if (trackDepth && !reducedMotion.matches) {
    world.style.setProperty('--drift-x', ((x - 0.5) * 4).toFixed(2));
    world.style.setProperty('--drift-y', ((y - 0.5) * 3).toFixed(2));
  }
}

function clearPresence() {
  if (presenceFrame) {
    window.cancelAnimationFrame(presenceFrame);
    presenceFrame = undefined;
  }

  world.classList.remove('is-aware');
  world.style.setProperty('--drift-x', '0');
  world.style.setProperty('--drift-y', '0');
}

function returnToCalm() {
  window.clearTimeout(responseTimer);
  window.clearTimeout(arrivalTimer);
  window.clearTimeout(silenceTimer);
  clearPresence();
  world.classList.remove('is-answering');
  world.classList.remove('is-silent');
  world.dataset.rulePhase = 'living';
}

function worldCanAnswer(now = performance.now()) {
  return now >= nextAnswerAt;
}

function chooseSilence() {
  window.clearTimeout(silenceTimer);
  clearPresence();
  world.classList.add('is-silent');
  world.dataset.rulePhase = 'silence';
  world.dataset.lastChoice = 'silence';

  silenceTimer = window.setTimeout(() => {
    world.classList.remove('is-silent');
    if (!world.classList.contains('is-answering')) {
      world.dataset.rulePhase = 'living';
    }
  }, SILENCE_PHASE_MS);
}

function trackPointer(event) {
  if (world.classList.contains('is-answering') || !worldCanAnswer()) {
    clearPresence();
    return;
  }

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
  setWorldPoint(clientX, clientY, false);
  window.clearTimeout(silenceTimer);
  clearPresence();

  world.classList.remove('is-answering');
  world.classList.remove('is-silent');
  void response.offsetWidth;
  void reply.offsetWidth;
  world.classList.add('is-answering');
  world.dataset.rulePhase = 'ahead';
  world.dataset.lastChoice = 'answer';

  window.clearTimeout(responseTimer);
  window.clearTimeout(arrivalTimer);
  arrivalTimer = window.setTimeout(() => {
    world.dataset.rulePhase = 'arrival';
  }, 1180);
  responseTimer = window.setTimeout(() => {
    returnToCalm();
  }, 2800);
}

function chooseAt(clientX, clientY) {
  if (world.classList.contains('is-answering')) {
    return;
  }

  const now = performance.now();
  if (!worldCanAnswer(now)) {
    chooseSilence();
    return;
  }

  nextAnswerAt = now + WORLD_BREATH_MS;
  respondAt(clientX, clientY);
}

function respondToPointer(event) {
  if (event.pointerType === 'mouse' && event.button !== 0) {
    return;
  }

  touchSurface.blur();
  chooseAt(event.clientX, event.clientY);
}

function handlePointerLeave(event) {
  if (event.pointerType !== 'touch' && !world.classList.contains('is-answering')) {
    clearPresence();
  }
}

function handlePointerCancel() {
  if (!world.classList.contains('is-answering')) {
    clearPresence();
  }
}

function handleClick(event) {
  if (event.detail !== 0) {
    touchSurface.blur();
  }
}

function respondToKeyboard(event) {
  if ((event.key !== 'Enter' && event.key !== ' ') || event.repeat) {
    return;
  }

  event.preventDefault();

  const rect = world.getBoundingClientRect();
  chooseAt(rect.left + rect.width * 0.5, rect.top + rect.height * 0.72);
}

touchSurface.addEventListener('pointermove', trackPointer);
touchSurface.addEventListener('pointerdown', respondToPointer);
touchSurface.addEventListener('pointerleave', handlePointerLeave);
touchSurface.addEventListener('pointercancel', handlePointerCancel);
touchSurface.addEventListener('click', handleClick);
touchSurface.addEventListener('keydown', respondToKeyboard);
