(function () {
  "use strict";

  var REVEALS = {
    listen: "耳を澄ますと、草の音がだんだん近づいてくる。何かが、いつもそこを通り道にしているらしい。",
    climb: "高いところから見わたすと、足あとが遠くまで続いているのが見える。道は、まだ先にある。",
    follow: "光に近づくと、それは森の奥にある小さな灯りだとわかる。誰かが、そこで待っているようだ。"
  };

  var app = document.getElementById("app");
  var screenSetup = document.getElementById("screen-setup");
  var screenReveal = document.getElementById("screen-reveal");
  var revealText = document.getElementById("reveal-text");
  var retryButton = document.getElementById("retry");
  var choiceButtons = document.querySelectorAll(".choice");

  function showScreen(name) {
    app.setAttribute("data-screen", name);

    var setupActive = name === "setup";
    screenSetup.classList.toggle("active", setupActive);
    screenSetup.setAttribute("aria-hidden", String(!setupActive));

    var revealActive = name === "reveal";
    screenReveal.classList.toggle("active", revealActive);
    screenReveal.setAttribute("aria-hidden", String(!revealActive));
  }

  function handleChoice(event) {
    var choice = event.currentTarget.getAttribute("data-choice");
    var text = REVEALS[choice];
    if (!text) {
      return;
    }
    revealText.textContent = text;
    showScreen("reveal");
  }

  function handleRetry() {
    showScreen("setup");
  }

  for (var i = 0; i < choiceButtons.length; i += 1) {
    choiceButtons[i].addEventListener("click", handleChoice);
  }
  retryButton.addEventListener("click", handleRetry);

  showScreen("setup");
})();
