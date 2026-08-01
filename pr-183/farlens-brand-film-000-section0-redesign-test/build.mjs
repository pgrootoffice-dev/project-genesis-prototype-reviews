import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const read64 = (file) => fs.readFileSync(path.join(root, file)).toString("base64");
const logo = read64("source/shared/farlens-logo-ceo-original.jpg");
const textures = {
  a: read64("source/shared/atmosphere/direction-a-observation-birth-light.jpg"),
  b: read64("source/shared/atmosphere/direction-b-shared-horizon-light.jpg"),
  c: read64("source/shared/atmosphere/direction-c-converging-current-light.jpg"),
};

const defs = `<defs>
  <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#071B3A" flood-opacity=".16"/></filter>
  <filter id="blur"><feGaussianBlur stdDeviation="34"/></filter>
  <radialGradient id="core" cx="50%" cy="45%" r="62%"><stop offset="0" stop-color="#FFFDF8" stop-opacity=".98"/><stop offset=".62" stop-color="#F6F1E8" stop-opacity=".84"/><stop offset="1" stop-color="#F6F1E8" stop-opacity="0"/></radialGradient>
  <linearGradient id="aLine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1556A8"/><stop offset="1" stop-color="#4C9A9A"/></linearGradient>
  <linearGradient id="bLine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D96F5F"/><stop offset=".5" stop-color="#F39A19"/><stop offset="1" stop-color="#4C9A9A"/></linearGradient>
  <linearGradient id="cLine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A9CBD6"/><stop offset=".45" stop-color="#6C628D"/><stop offset="1" stop-color="#F39A19"/></linearGradient>
</defs>`;

const texture = (d, opacity) => `<rect width="1080" height="1920" fill="${d === "c" ? "#071B3A" : "#F6F1E8"}"/><image href="data:image/jpeg;base64,${textures[d]}" width="1080" height="1920" preserveAspectRatio="xMidYMid slice" opacity="${opacity}"/>`;
const integratedLogo = (y = 360, width = 840) => `<image href="data:image/jpeg;base64,${logo}" x="${(1080 - width) / 2}" y="${y}" width="${width}" height="${width}" preserveAspectRatio="xMidYMid meet" style="mix-blend-mode:multiply"/>`;

const variants = {
  "a1-aperture-assembly": {
    name: "A1 Aperture Assembly",
    direction: "A — Intelligent Clarity",
    body: `${texture("a", .58)}
      <ellipse cx="540" cy="760" rx="446" ry="500" fill="url(#core)"/>
      <g fill="none" stroke-linecap="round">
        <circle cx="540" cy="704" r="360" stroke="#071B3A" stroke-width="8" opacity=".82" stroke-dasharray="760 190 140 116"/>
        <circle cx="540" cy="704" r="310" stroke="url(#aLine)" stroke-width="16" opacity=".72" stroke-dasharray="410 92 280 166"/>
        <path d="M74 1170 C214 1074 316 968 408 850" stroke="#1556A8" stroke-width="12" opacity=".62"/>
        <path d="M1006 308 C862 406 760 512 672 626" stroke="#4C9A9A" stroke-width="12" opacity=".66"/>
      </g>
      ${integratedLogo(340, 860)}
      <g fill="none" stroke-linecap="round"><path d="M90 704 H258" stroke="#071B3A" stroke-width="7"/><path d="M822 704 H990" stroke="#071B3A" stroke-width="7"/><path d="M540 196 V326" stroke="#F39A19" stroke-width="9"/><path d="M540 1194 C598 1306 676 1370 758 1450" stroke="url(#aLine)" stroke-width="14"/></g>`,
  },
  "a2-field-alignment": {
    name: "A2 Field Alignment",
    direction: "A — Intelligent Clarity",
    body: `${texture("a", .46)}
      <rect width="1080" height="1920" fill="#FFFDF8" opacity=".18"/>
      <g fill="none" stroke="#071B3A" opacity=".22">
        <path d="M174 0 V1920"/><path d="M330 0 V1920"/><path d="M750 0 V1920"/><path d="M906 0 V1920"/>
        <path d="M0 420 H1080"/><path d="M0 1220 H1080"/>
      </g>
      <ellipse cx="540" cy="742" rx="410" ry="500" fill="url(#core)"/>
      <g fill="none" stroke-linecap="round">
        <path d="M98 346 C272 420 356 516 430 630" stroke="#1556A8" stroke-width="18" opacity=".62"/>
        <path d="M982 1120 C800 1038 718 950 654 842" stroke="#4C9A9A" stroke-width="18" opacity=".62"/>
        <circle cx="540" cy="690" r="342" stroke="#071B3A" stroke-width="7" stroke-dasharray="350 70 180 110"/>
        <circle cx="540" cy="690" r="292" stroke="#F39A19" stroke-width="8" stroke-dasharray="120 1715" transform="rotate(-42 540 690)"/>
      </g>
      ${integratedLogo(352, 840)}
      <path d="M540 1160 V1510" stroke="#071B3A" stroke-width="8" stroke-linecap="round"/><path d="M540 1240 C462 1344 398 1406 302 1470" stroke="url(#aLine)" stroke-width="13" fill="none" stroke-linecap="round"/>`,
  },
  "b1-shared-horizon": {
    name: "B1 Shared Horizon",
    direction: "B — Family Future",
    body: `${texture("b", .64)}
      <ellipse cx="540" cy="744" rx="442" ry="520" fill="url(#core)"/>
      <g fill="none" stroke-linecap="round">
        <path d="M70 1240 C240 1032 360 900 486 774" stroke="#D96F5F" stroke-width="18" opacity=".72"/>
        <path d="M1010 1240 C836 1028 720 900 594 774" stroke="#4C9A9A" stroke-width="18" opacity=".72"/>
        <path d="M80 872 C288 786 792 786 1000 872" stroke="#071B3A" stroke-width="10" opacity=".74"/>
        <path d="M170 930 C350 854 730 854 910 930" stroke="#F39A19" stroke-width="9" opacity=".78"/>
      </g>
      ${integratedLogo(352, 850)}
      <circle cx="382" cy="850" r="12" fill="#D96F5F"/><circle cx="698" cy="850" r="12" fill="#4C9A9A"/>
      <path d="M540 1164 C540 1298 594 1380 690 1474" stroke="#F39A19" stroke-width="15" fill="none" stroke-linecap="round"/>`,
  },
  "b2-two-viewpoints": {
    name: "B2 Two Viewpoints",
    direction: "B — Family Future",
    body: `${texture("b", .54)}
      <ellipse cx="540" cy="760" rx="450" ry="530" fill="url(#core)"/>
      <g fill="none" stroke-linecap="round">
        <circle cx="388" cy="736" r="300" stroke="#D96F5F" stroke-width="16" opacity=".62" stroke-dasharray="820 1065"/>
        <circle cx="700" cy="684" r="244" stroke="#4C9A9A" stroke-width="16" opacity=".66" stroke-dasharray="690 844"/>
        <path d="M92 1140 C250 1018 362 906 462 778" stroke="#D96F5F" stroke-width="12"/>
        <path d="M988 1080 C834 980 724 880 618 768" stroke="#4C9A9A" stroke-width="12"/>
        <path d="M156 932 C340 842 740 842 924 932" stroke="url(#bLine)" stroke-width="10"/>
      </g>
      ${integratedLogo(354, 850)}
      <path d="M540 1168 C476 1302 398 1392 300 1472" stroke="#D96F5F" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M540 1168 C616 1298 694 1384 784 1460" stroke="#4C9A9A" stroke-width="11" fill="none" stroke-linecap="round"/>`,
  },
  "c1-current-knot": {
    name: "C1 Current Knot",
    direction: "C — World in Motion",
    body: `${texture("c", .72)}
      <ellipse cx="540" cy="760" rx="452" ry="540" fill="url(#core)"/>
      <g fill="none" stroke-linecap="round">
        <path d="M-60 334 C172 366 320 488 430 626" stroke="#A9CBD6" stroke-width="36" opacity=".82"/>
        <path d="M1120 340 C886 414 744 512 650 634" stroke="#6C628D" stroke-width="38" opacity=".82"/>
        <path d="M-50 1208 C214 1106 354 980 458 838" stroke="#F39A19" stroke-width="26" opacity=".92"/>
        <path d="M1120 1160 C860 1076 728 958 634 838" stroke="#FFFDF8" stroke-width="18" opacity=".78"/>
      </g>
      ${integratedLogo(350, 860)}
      <circle cx="540" cy="704" r="356" fill="none" stroke="#071B3A" stroke-width="9" stroke-dasharray="680 320 190 1046"/>
      <path d="M540 1162 C612 1286 716 1368 864 1432" stroke="url(#cLine)" stroke-width="22" fill="none" stroke-linecap="round"/>`,
  },
  "c2-folded-orbit": {
    name: "C2 Folded Orbit",
    direction: "C — World in Motion",
    body: `${texture("c", .62)}
      <ellipse cx="540" cy="756" rx="452" ry="536" fill="url(#core)"/>
      <g fill="none" stroke-linejoin="round" stroke-linecap="round">
        <path d="M-20 188 L264 438 L432 646" stroke="#A9CBD6" stroke-width="40" opacity=".86"/>
        <path d="M1100 188 L820 424 L652 644" stroke="#6C628D" stroke-width="40" opacity=".86"/>
        <path d="M-40 1120 L266 984 L450 824" stroke="#F39A19" stroke-width="28" opacity=".92"/>
        <path d="M1120 1100 L812 972 L632 824" stroke="#FFFDF8" stroke-width="18" opacity=".76"/>
        <circle cx="540" cy="704" r="350" stroke="#071B3A" stroke-width="10" stroke-dasharray="220 82 560 1338"/>
      </g>
      ${integratedLogo(350, 860)}
      <path d="M540 1160 L540 1300 L742 1470" stroke="url(#cLine)" stroke-width="22" fill="none" stroke-linejoin="round" stroke-linecap="round"/>`,
  },
};

fs.mkdirSync(path.join(root, "source", "variants"), { recursive: true });
fs.mkdirSync(path.join(root, "composites"), { recursive: true });
for (const [slug, variant] of Object.entries(variants)) {
  const svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">${defs}<metadata>${variant.direction}; ${variant.name}; Section 0 logo emergence study; editable SVG source</metadata>${variant.body}</svg>\n`;
  fs.writeFileSync(path.join(root, "source", "variants", `${slug}.svg`), svg);
  fs.writeFileSync(path.join(root, "composites", `${slug}.svg`), svg);
}
fs.writeFileSync(path.join(root, "variants.json"), JSON.stringify(Object.entries(variants).map(([slug, value]) => ({ slug, name: value.name, direction: value.direction })), null, 2) + "\n");
console.log("Built 6 Section 0 editable SVG studies.");
