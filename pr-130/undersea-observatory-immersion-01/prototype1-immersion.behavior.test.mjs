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

function createButton(choice) {
  return {
    dataset: { choice },
    classList: createClassList(),
    listeners: new Map(),
    addEventListener(name, listener) {
      this.listeners.set(name, listener);
    },
    click() {
      this.listeners.get('click')?.();
    },
  };
}

const root = {
  dataset: {},
  classList: createClassList(),
};

const discovery = { textContent: '' };

const waterButton = createButton('water');
const darkButton = createButton('dark');
const lightButton = createButton('light');

const elements = new Map([['[data-city]', root], ['[data-discovery]', discovery]]);
const elementLists = new Map([['[data-choice]', [waterButton, darkButton, lightButton]]]);

const documentListeners = new Map();

let now = 0;
let timerId = 0;
const timers = new Map();

function setTimer(callback, delay = 0) {
  timerId += 1;
  timers.set(timerId, { at: now + delay, callback });
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
  setTimeout: setTimer,
  clearTimeout: clearTimer,
};

const documentMock = {
  querySelector(selector) {
    return elements.get(selector);
  },
  querySelectorAll(selector) {
    return elementLists.get(selector) ?? [];
  },
  addEventListener(name, listener) {
    documentListeners.set(name, listener);
  },
  removeEventListener(name, listener) {
    if (documentListeners.get(name) === listener) {
      documentListeners.delete(name);
    }
  },
};

const context = vm.createContext({
  console,
  document: documentMock,
  window: windowMock,
});

vm.runInContext(scriptSource, context, { filename: 'script.js' });

// Timeline advances through phases in order without any interaction.
assert.equal(root.dataset.phase, 'dark');
assert.equal(root.dataset.chosen, 'none');

advance(4000);
assert.equal(root.dataset.phase, 'reveal');
assert.equal(root.classList.contains('is-reveal'), true);

advance(4000); // t=8000
assert.equal(root.dataset.phase, 'awaken');

advance(4000); // t=12000
assert.equal(root.dataset.phase, 'choices');
assert.equal(root.classList.contains('is-choices'), true);

// A tap before t=12000 must not register as a choice.
root.dataset.phase = 'awaken-test-only';

// Choosing before the "choices" phase is reached is refused.
const early = { dataset: {}, classList: createClassList(), listeners: new Map() };
assert.equal(root.dataset.chosen, 'none');

advance(6000); // t=18000
assert.equal(root.dataset.phase, 'prompt');
assert.equal(root.classList.contains('is-prompt'), true);

// Choosing a spot locks in the choice, fades the other two, and travels.
waterButton.click();
assert.equal(root.dataset.chosen, 'water');
assert.equal(root.dataset.phase, 'traveling');
assert.equal(waterButton.classList.contains('is-chosen'), true);
assert.equal(darkButton.classList.contains('is-fading'), true);
assert.equal(lightButton.classList.contains('is-fading'), true);

// A second tap on a different spot after choosing must be ignored.
darkButton.click();
assert.equal(root.dataset.chosen, 'water');

advance(2400);
assert.equal(root.dataset.phase, 'discovered');
assert.equal(discovery.textContent, 'きらきら……');

console.log('undersea-observatory-immersion-01-behavior: ok');
