const root = document.querySelector('[data-city]');
const choiceButtons = Array.from(document.querySelectorAll('[data-choice]'));
const discoveryEl = document.querySelector('[data-discovery]');

const PHASE_TIMELINE = [
  { phase: 'reveal', at: 4000 },
  { phase: 'awaken', at: 8000 },
  { phase: 'choices', at: 12000 },
  { phase: 'prompt', at: 18000 },
];

const TRAVEL_MS = 2400;

const DISCOVERY_TEXT = {
  water: 'きらきら……',
  dark: 'ひかった……',
  light: 'あれ……？',
};

root.dataset.phase = 'dark';
root.dataset.chosen = 'none';

function setPhase(phase) {
  root.dataset.phase = phase;
  root.classList.add(`is-${phase}`);
}

function scheduleTimeline() {
  PHASE_TIMELINE.forEach(({ phase, at }) => {
    window.setTimeout(() => setPhase(phase), at);
  });
}

function canChoose() {
  return root.dataset.chosen === 'none' && root.classList.contains('is-choices');
}

function choose(id) {
  if (!canChoose()) {
    return;
  }

  root.dataset.chosen = id;

  choiceButtons.forEach((button) => {
    if (button.dataset.choice === id) {
      button.classList.add('is-chosen');
    } else {
      button.classList.add('is-fading');
    }
  });

  setPhase('traveling');
  playChoiceTone();

  window.setTimeout(() => {
    setPhase('discovered');
    if (discoveryEl) {
      discoveryEl.textContent = DISCOVERY_TEXT[id] || '';
    }
    playDiscoveryChime();
  }, TRAVEL_MS);
}

choiceButtons.forEach((button) => {
  button.addEventListener('click', () => choose(button.dataset.choice));
});

scheduleTimeline();

/* ---- ambient sound: synthesized via Web Audio only, no audio files, no new
   dependency, no autoplay before a user gesture (iOS/Safari require one anyway) ---- */

let audioCtx;
let ambientStarted = false;

function ensureAudioContext() {
  if (audioCtx) {
    return audioCtx;
  }

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) {
    return null;
  }

  audioCtx = new AudioContextClass();
  return audioCtx;
}

function startAmbientHum() {
  const ctx = ensureAudioContext();
  if (!ctx || ambientStarted) {
    return;
  }

  ambientStarted = true;

  if (ctx.state === 'suspended' && typeof ctx.resume === 'function') {
    ctx.resume();
  }

  const hum = ctx.createOscillator();
  const wobble = ctx.createOscillator();
  const humGain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  hum.type = 'sine';
  hum.frequency.value = 58;
  wobble.type = 'sine';
  wobble.frequency.value = 61.5;
  filter.type = 'lowpass';
  filter.frequency.value = 220;

  humGain.gain.value = 0;
  hum.connect(filter);
  wobble.connect(filter);
  filter.connect(humGain);
  humGain.connect(ctx.destination);

  hum.start();
  wobble.start();
  humGain.gain.linearRampToValueAtTime(0.045, ctx.currentTime + 3);
}

function playTone(frequency, options = {}) {
  const { delay = 0, duration = 0.18, gain = 0.05, type = 'sine' } = options;
  const ctx = ensureAudioContext();
  if (!ctx) {
    return;
  }

  const start = ctx.currentTime + delay;
  const osc = ctx.createOscillator();
  const toneGain = ctx.createGain();

  osc.type = type;
  osc.frequency.value = frequency;
  toneGain.gain.setValueAtTime(0, start);
  toneGain.gain.linearRampToValueAtTime(gain, start + duration * 0.3);
  toneGain.gain.linearRampToValueAtTime(0, start + duration);

  osc.connect(toneGain);
  toneGain.connect(ctx.destination);
  osc.start(start);
  osc.stop(start + duration + 0.05);
}

function playChoiceTone() {
  playTone(420, { duration: 0.16, gain: 0.045 });
}

function playDiscoveryChime() {
  playTone(660, { delay: 0, duration: 0.4, gain: 0.05 });
  playTone(880, { delay: 0.14, duration: 0.5, gain: 0.045 });
  playTone(990, { delay: 0.3, duration: 0.6, gain: 0.04 });
}

function unlockAudioOnce() {
  startAmbientHum();
  document.removeEventListener('pointerdown', unlockAudioOnce);
  document.removeEventListener('keydown', unlockAudioOnce);
}

document.addEventListener('pointerdown', unlockAudioOnce, { once: true });
document.addEventListener('keydown', unlockAudioOnce, { once: true });
