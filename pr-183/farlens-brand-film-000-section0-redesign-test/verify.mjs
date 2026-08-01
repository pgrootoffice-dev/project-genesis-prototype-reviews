import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const root=path.dirname(fileURLToPath(import.meta.url));
const variants=["a1-aperture-assembly","a2-field-alignment","b1-shared-horizon","b2-two-viewpoints","c1-current-knot","c2-folded-orbit"];
const fail=message=>{throw new Error(message)};
const digest=file=>crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const renderManifestPath=path.join(root,"render-manifest.json");if(!fs.existsSync(renderManifestPath))fail("render-manifest.json missing; run node record-render.mjs");const renderManifest=JSON.parse(fs.readFileSync(renderManifestPath,"utf8"));
const directInputs=["build.mjs","record-render.mjs","render-frame.html","source/shared/farlens-logo-ceo-original.jpg","source/shared/atmosphere/direction-a-observation-birth.png","source/shared/atmosphere/direction-a-observation-birth-light.jpg","source/shared/atmosphere/direction-b-shared-horizon.png","source/shared/atmosphere/direction-b-shared-horizon-light.jpg","source/shared/atmosphere/direction-c-converging-current.png","source/shared/atmosphere/direction-c-converging-current-light.jpg"];
for(const input of directInputs)if(renderManifest.inputs?.[input]!==digest(path.join(root,input)))fail(`${input}: build input changed; run node record-render.mjs`);
for(const variant of variants){
  const source=path.join(root,"source","variants",`${variant}.svg`);const svg=path.join(root,"composites",`${variant}.svg`);const png=path.join(root,"composites",`${variant}.png`);const preview=path.join(root,"previews",`${variant}.jpg`);
  for(const file of [source,svg,png,preview])if(!fs.existsSync(file))fail(`${variant}: missing ${path.basename(file)}`);
  if(fs.readFileSync(source,"utf8")!==fs.readFileSync(svg,"utf8"))fail(`${variant}: composite SVG is stale relative to editable source`);
  const bytes=fs.readFileSync(png);if(bytes.toString("ascii",1,4)!=="PNG")fail(`${variant}: not PNG`);if(bytes.readUInt32BE(16)!==1080||bytes.readUInt32BE(20)!==1920)fail(`${variant}: expected 1080x1920`);
  const sourceText=fs.readFileSync(source,"utf8");if(!sourceText.includes("mix-blend-mode:multiply"))fail(`${variant}: logo integration blend missing`);
  const record=renderManifest.renders?.[variant];if(!record)fail(`${variant}: render record missing`);
  if(record.source_svg_sha256!==digest(source)||record.composite_svg_sha256!==digest(svg)||record.png_sha256!==digest(png)||record.preview_sha256!==digest(preview))fail(`${variant}: stale render lineage; run node record-render.mjs`);
}
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
if((html.match(/class="frame-button"/g)||[]).length!==6)fail("review page must expose 6 tap targets");
if(html.includes("section-1")||html.includes("section-2"))fail("Section 1/2 assets are out of scope");
for(const variant of variants){if(!html.includes(`previews/${variant}.jpg`)||!html.includes(`composites/${variant}.png`))fail(`${variant}: review references missing`)}
const contact=path.join(root,"previews","contact-sheet.jpg");if(renderManifest.contact_sheet_sha256!==digest(contact))fail("contact sheet is stale; run node record-render.mjs");
const ledgerPath=path.join(root,"checksums.sha256");if(!fs.existsSync(ledgerPath))fail("checksums.sha256 missing");
const ledgerLines=fs.readFileSync(ledgerPath,"utf8").trim().split("\n");
const ledgerPaths=[];for(const line of ledgerLines){const [hash,...parts]=line.split(/\s+/);const relative=parts.join(" ");ledgerPaths.push(relative);const file=path.join(root,relative);if(!fs.existsSync(file)||digest(file)!==hash)fail(`${relative}: published checksum is stale`)}
const expectedPaths=[...directInputs,...variants.flatMap(variant=>[`source/variants/${variant}.svg`,`composites/${variant}.svg`,`composites/${variant}.png`,`previews/${variant}.jpg`]),"previews/contact-sheet.jpg","render-manifest.json"].sort();
const actualPaths=[...new Set(ledgerPaths)].sort();if(actualPaths.length!==ledgerPaths.length||JSON.stringify(actualPaths)!==JSON.stringify(expectedPaths))fail("checksum ledger path set does not match the required render contract");
console.log("PASS: 6 Section 0 masters are 1080x1920; source/composite parity and iPhone tap targets verified.");
