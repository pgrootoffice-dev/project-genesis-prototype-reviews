import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const scriptSource = fs.readFileSync(new URL('./script.js', import.meta.url), 'utf8');

function createClassList() {
  const values = new Set();

  return {
    add(...names) {
      names.forEach((name) => values.add(name));
    },
    remove(...names) {
      names.forEach((name) => values.delete(name));
    },
    contains(name) {
      return values.has(name);
    },
  };
}

const styleValues = new Map();
const listeners = new Map();
const world = {
  dataset: {},
  classList: createClassList(),
  style: {
    setProperty(name, value) {
      styleValues.set(name, value);
    },
  },
  getBoundingClientRect() {
    return {
      left: 0,
      top: 0,
      width: 400,
      height: 800,
    };
  },
};

const touchSurface = {
  addEventListener(name, listener) {
    listeners.set(name, listener);
  },
  blur() {},
};

const response = { offsetWidth: 1 };
const reply = { offsetWidth: 1 };

const elements = new Map([
  ['[data-living-world]', world],
  ['[data-world-touch]', touchSurface],
  ['[data-world-response]', response],
  ['[data-world-reply]', reply],
]);

let now = 0;
let timerId = 0;
const timers = new Map();

function setTimer(callback, delay = 0) {
  timerId += 1;
  timers.set(timerId, {
    at: now + delay,
    callback,
  });
  return timerId;
}

function clearTimer(id) {
  timers.delete(id);
}

function advance(milliseconds) {
  const target = now + milliseconds;

  while (true) {
    let nextId;
    let nextTimer;

    for (const [id, timer] of timers) {
      if (timer.at <= target && (!nextTimer || timer.at < nextTimer.at)) {
        nextId = id;
        nextTimer = timer;
      }
    }

    if (!nextTimer) {
      break;
    }

    now = nextTimer.at;
    timers.delete(nextId);
    nextTimer.callback();
  }

  now = target;
}

const windowMock = {
  matchMedia() {
    return { matches: false };
  },
  requestAnimationFrame(callback) {
    return setTimer(callback, 16);
  },
  cancelAnimationFrame: clearTimer,
  setTimeout: setTimer,
  clearTimeout: clearTimer,
};

const context = vm.createContext({
  console,
  document: {
    querySelector(selector) {
      return elements.get(selector);
    },
  },
  performance: {
    now() {
      return now;
    },
  },
  window: windowMock,
});

vm.runInContext(scriptSource, context, {
  filename: 'script.js',
});

function pointerDown(clientX, clientY) {
  listeners.get('pointerdown')({
    pointerType: 'touch',
    button: 0,
    clientX,
    clientY,
  });
}

assert.equal(world.dataset.rulePhase, 'living');
assert.equal(world.dataset.lastChoice, 'none');
assert.equal(world.dataset.worldBreathMs, '8000');

pointerDown(100, 600);
assert.equal(world.dataset.lastChoice, 'answer');
assert.equal(world.dataset.rulePhase, 'ahead');
assert.equal(world.classList.contains('is-answering'), true);
assert.equal(styleValues.get('--response-x'), '25.00%');
assert.equal(styleValues.get('--response-y'), '75.00%');

advance(1180);
assert.equal(world.dataset.rulePhase, 'arrival');

advance(1620);
assert.equal(world.dataset.rulePhase, 'living');
assert.equal(world.classList.contains('is-answering'), false);

pointerDown(300, 200);
assert.equal(world.dataset.lastChoice, 'silence');
assert.equal(world.dataset.rulePhase, 'silence');
assert.equal(world.classList.contains('is-silent'), true);
assert.equal(world.classList.contains('is-answering'), false);
assert.equal(styleValues.get('--response-x'), '25.00%');
assert.equal(styleValues.get('--response-y'), '75.00%');

advance(1200);
assert.equal(world.dataset.rulePhase, 'living');
assert.equal(world.classList.contains('is-silent'), false);

advance(4001);
pointerDown(300, 200);
assert.equal(world.dataset.lastChoice, 'answer');
assert.equal(world.dataset.rulePhase, 'ahead');
assert.equal(world.classList.contains('is-answering'), true);
assert.equal(styleValues.get('--response-x'), '75.00%');
assert.equal(styleValues.get('--response-y'), '25.00%');

console.log('prototype4-behavior: ok');
