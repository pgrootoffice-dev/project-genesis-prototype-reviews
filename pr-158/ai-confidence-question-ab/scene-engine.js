/*
  Minimal, dependency-free timeline runner shared by A and B.
  Every scene is pre-authored as static HTML (a `.scene[data-start][data-end]`
  element inside `.stage`); this engine only toggles which one is
  `.is-active` at the current playhead time, drives the progress bar, and
  (optionally, muted by default) plays short, fully-synthesized tones via
  the Web Audio API -- no external audio file of any kind.

  Two declarative, JS-driven class-toggle mechanisms on top of that, both
  using the same principle (a CSS transition or animation fires because a
  class was toggled at a specific playhead time, never a CSS
  `animation-delay` counted from page load -- see README.md "What Was
  Fixed" for the real bug that principle exists to prevent):

  - `data-reveal-at="<seconds>"` -- element gains `.is-revealed` once the
    playhead passes that time, and keeps it (one-directional). Used for the
    quiz Reveal highlight, the causal-line draw-in, and the 5-beat time
    dial's ticks. Optionally paired with `data-tone="freq,durationMs"` on
    the same element to play a short chime the instant that one item's own
    reveal fires (used only for the quiz's Reveal moment) -- distinct from
    the per-scene `data-tone`/`data-sweep` above, which fire once at a
    scene's own start.
  - `data-hide-from="<seconds>"` + `data-hide-until="<seconds>"` -- element
    gains `.is-hidden-now` for exactly that window, then loses it again.
    Used for the O2 particles (vanish, then return) and the flame
    (weakens while O2 is gone, relights once it returns) -- cause and
    effect share one timing source instead of two separately-authored
    animations that could drift apart.
*/
(function () {
  "use strict";

  function createTonePlayer() {
    var ctx = null;
    function ensureCtx() {
      if (!ctx) {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return null;
        ctx = new AudioCtx();
      }
      return ctx;
    }
    return {
      // A short, soft, originally-synthesized sine blip. freq in Hz,
      // durationMs in milliseconds. Never loads or plays any external file.
      blip: function (freq, durationMs) {
        var audioCtx = ensureCtx();
        if (!audioCtx) return;
        var osc = audioCtx.createOscillator();
        var gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(
          0.18,
          audioCtx.currentTime + 0.03
        );
        gain.gain.exponentialRampToValueAtTime(
          0.0001,
          audioCtx.currentTime + durationMs / 1000
        );
        osc.connect(gain).connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + durationMs / 1000 + 0.02);
      },
      // A short descending sweep -- used only for the O2-vanish moment, to
      // give "disappearing" its own distinct, still fully self-synthesized
      // sound (no sample, no external file). freqFrom/freqTo in Hz.
      sweep: function (freqFrom, freqTo, durationMs) {
        var audioCtx = ensureCtx();
        if (!audioCtx) return;
        var osc = audioCtx.createOscillator();
        var gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freqFrom, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(
          freqTo,
          audioCtx.currentTime + durationMs / 1000
        );
        gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(
          0.16,
          audioCtx.currentTime + 0.04
        );
        gain.gain.exponentialRampToValueAtTime(
          0.0001,
          audioCtx.currentTime + durationMs / 1000
        );
        osc.connect(gain).connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + durationMs / 1000 + 0.02);
      },
      resume: function () {
        var audioCtx = ensureCtx();
        if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
      },
    };
  }

  function ShortPlayer(root, opts) {
    this.root = root;
    this.stage = root.querySelector(".stage");
    this.scenes = Array.prototype.slice
      .call(this.stage.querySelectorAll(".scene"))
      .map(function (el) {
        var tone = null;
        var sweep = null;
        if (el.dataset.tone) {
          tone = el.dataset.tone.split(",").map(Number);
        }
        if (el.dataset.sweep) {
          sweep = el.dataset.sweep.split(",").map(Number);
        }
        return {
          el: el,
          start: parseFloat(el.dataset.start),
          end: parseFloat(el.dataset.end),
          tone: tone,
          sweep: sweep,
        };
      });
    this.revealables = Array.prototype.slice
      .call(this.stage.querySelectorAll("[data-reveal-at]"))
      .map(function (el) {
        var tone = el.dataset.tone ? el.dataset.tone.split(",").map(Number) : null;
        return { el: el, at: parseFloat(el.dataset.revealAt), tone: tone, played: false };
      });
    this.hideables = Array.prototype.slice
      .call(this.stage.querySelectorAll("[data-hide-from]"))
      .map(function (el) {
        return {
          el: el,
          from: parseFloat(el.dataset.hideFrom),
          until: parseFloat(el.dataset.hideUntil),
        };
      });
    this.totalSeconds = Math.max.apply(
      null,
      this.scenes.map(function (s) {
        return s.end;
      })
    );
    this.progressFill = root.querySelector(".progress-fill");
    this.playBtn = root.querySelector("[data-action='play']");
    this.muteBtn = root.querySelector("[data-action='mute']");
    this.muted = true;
    this.tones = createTonePlayer();
    this.playedTones = {};
    this.rafId = null;
    this.startedAt = null;
    this.onScene = opts && opts.onScene ? opts.onScene : function () {};

    if (this.playBtn) {
      this.playBtn.addEventListener("click", this.restart.bind(this));
    }
    if (this.muteBtn) {
      this.muteBtn.addEventListener("click", this.toggleMute.bind(this));
      this.muteBtn.textContent = "🔇 音: オフ";
    }
  }

  ShortPlayer.prototype.toggleMute = function () {
    this.muted = !this.muted;
    if (!this.muted) this.tones.resume();
    this.muteBtn.textContent = this.muted ? "🔇 音: オフ" : "🔊 音: オン";
  };

  ShortPlayer.prototype.restart = function () {
    if (this.rafId) cancelAnimationFrame(this.rafId);
    this.playedTones = {};
    this.revealables.forEach(function (item) {
      item.played = false;
    });
    this.startedAt = performance.now();
    this.tick();
  };

  ShortPlayer.prototype.tick = function () {
    var elapsed = (performance.now() - this.startedAt) / 1000;
    var t = Math.min(elapsed, this.totalSeconds);

    this.scenes.forEach(function (scene) {
      var active = t >= scene.start && t < scene.end;
      scene.el.classList.toggle("is-active", active);
      if (active) this.onScene(scene.el.dataset.id || "");
      if (active && !this.muted && !this.playedTones[scene.start]) {
        if (scene.tone) {
          this.playedTones[scene.start] = true;
          this.tones.blip(scene.tone[0], scene.tone[1]);
        } else if (scene.sweep) {
          this.playedTones[scene.start] = true;
          this.tones.sweep(scene.sweep[0], scene.sweep[1], scene.sweep[2]);
        }
      }
    }, this);

    this.revealables.forEach(function (item) {
      var revealed = t >= item.at;
      item.el.classList.toggle("is-revealed", revealed);
      // Fires once, the instant this item's own reveal threshold is
      // crossed -- e.g. the quiz's quiet Reveal chime. Same one-directional,
      // played-once-per-item principle as the per-scene tone above, just
      // keyed to a sub-scene threshold instead of the scene's own start.
      if (revealed && !item.played && !this.muted && item.tone) {
        item.played = true;
        this.tones.blip(item.tone[0], item.tone[1]);
      }
    }, this);

    this.hideables.forEach(function (item) {
      item.el.classList.toggle("is-hidden-now", t >= item.from && t < item.until);
    });

    if (this.progressFill) {
      this.progressFill.style.width =
        (t / this.totalSeconds) * 100 + "%";
    }

    if (elapsed < this.totalSeconds) {
      this.rafId = requestAnimationFrame(this.tick.bind(this));
    }
  };

  window.FarlensShortPlayer = ShortPlayer;
})();
