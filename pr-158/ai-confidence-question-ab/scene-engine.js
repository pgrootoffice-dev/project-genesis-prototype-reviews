/*
  Minimal, dependency-free timeline runner shared by A and B.
  Every scene is pre-authored as static HTML (a `.scene[data-start][data-end]`
  element inside `.stage`); this engine only toggles which one is
  `.is-active` at the current playhead time, drives the progress bar, and
  (optionally, muted by default) plays short, fully-synthesized tones via
  the Web Audio API -- no external audio file of any kind.
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
        return {
          el: el,
          start: parseFloat(el.dataset.start),
          end: parseFloat(el.dataset.end),
          tone: el.dataset.tone ? el.dataset.tone.split(",").map(Number) : null,
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
      if (
        active &&
        scene.tone &&
        !this.muted &&
        !this.playedTones[scene.start]
      ) {
        this.playedTones[scene.start] = true;
        this.tones.blip(scene.tone[0], scene.tone[1]);
      }
    }, this);

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
