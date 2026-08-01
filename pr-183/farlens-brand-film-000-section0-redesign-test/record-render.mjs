import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const root=path.dirname(fileURLToPath(import.meta.url));
const variants=["a1-aperture-assembly","a2-field-alignment","b1-shared-horizon","b2-two-viewpoints","c1-current-knot","c2-folded-orbit"];
const inputNames=[
  "build.mjs","record-render.mjs","render-frame.html","source/shared/farlens-logo-ceo-original.jpg",
  "source/shared/atmosphere/direction-a-observation-birth.png","source/shared/atmosphere/direction-a-observation-birth-light.jpg",
  "source/shared/atmosphere/direction-b-shared-horizon.png","source/shared/atmosphere/direction-b-shared-horizon-light.jpg",
  "source/shared/atmosphere/direction-c-converging-current.png","source/shared/atmosphere/direction-c-converging-current-light.jpg"
];
const digest=file=>crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const chromeCandidates=["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","/Applications/Chromium.app/Contents/MacOS/Chromium","google-chrome","chromium"];
const chrome=chromeCandidates.find(candidate=>{if(candidate.includes("/"))return fs.existsSync(candidate);const probe=spawnSync(candidate,["--version"],{stdio:"ignore",timeout:5000});return !probe.error&&probe.status===0});
if(!chrome)throw new Error("Chrome or Chromium is required");
const build=spawnSync(process.execPath,[path.join(root,"build.mjs")],{encoding:"utf8",timeout:30000});
if(build.status!==0)throw new Error(`build failed\n${build.stderr||build.stdout}`);
const temporaryRoot=fs.mkdtempSync(path.join(os.tmpdir(),"farlens-section0-render-"));

function run(command,args,label,timeout=30000){const result=spawnSync(command,args,{encoding:"utf8",timeout});if(result.status!==0)throw new Error(`${label} failed\n${result.stderr||result.stdout}`)}
function render(base){
  const url=pathToFileURL(path.join(root,"render-frame.html"));url.searchParams.set("asset",`${base}.svg`);
  const temporary=path.join(temporaryRoot,`${base}.png`);
  run(chrome,["--headless=new","--disable-gpu","--disable-extensions","--disable-background-networking","--disable-component-update","--disable-default-apps","--disable-sync","--metrics-recording-only","--no-first-run","--no-sandbox","--hide-scrollbars","--allow-file-access-from-files","--window-size=1080,1920","--force-device-scale-factor=1","--virtual-time-budget=1000",`--user-data-dir=${path.join(temporaryRoot,"profile")}`,`--screenshot=${temporary}`,url.href],base,45000);
  const bytes=fs.readFileSync(temporary);if(bytes.toString("ascii",1,4)!=="PNG"||bytes.readUInt32BE(16)!==1080||bytes.readUInt32BE(20)!==1920)throw new Error(`${base}: invalid render size`);
  fs.copyFileSync(temporary,path.join(root,"composites",`${base}.png`));
}

try{
  const renders={};
  for(const variant of variants){
    render(variant);
    const png=path.join(root,"composites",`${variant}.png`);const preview=path.join(root,"previews",`${variant}.jpg`);
    run("ffmpeg",["-loglevel","error","-y","-i",png,"-vf","scale=360:640","-q:v","4",preview],`${variant} preview`);
    renders[variant]={source_svg_sha256:digest(path.join(root,"source","variants",`${variant}.svg`)),composite_svg_sha256:digest(path.join(root,"composites",`${variant}.svg`)),png_sha256:digest(png),preview_sha256:digest(preview)};
  }
  const contact=path.join(root,"previews","contact-sheet.jpg");const inputs=variants.flatMap(variant=>["-i",path.join(root,"previews",`${variant}.jpg`)]);
  run("ffmpeg",["-loglevel","error","-y",...inputs,"-filter_complex","xstack=inputs=6:layout=0_0|360_0|0_640|360_640|0_1280|360_1280:fill=white","-q:v","3",contact],"contact sheet");
  const manifest={contract:"Build inputs, editable SVGs, masters, previews, and contact sheet are bound by this self-rendering command.",inputs:Object.fromEntries(inputNames.map(name=>[name,digest(path.join(root,name))])),renders,contact_sheet_sha256:digest(contact)};
  fs.writeFileSync(path.join(root,"render-manifest.json"),JSON.stringify(manifest,null,2)+"\n");
  const checksumNames=[...inputNames,...variants.flatMap(variant=>[`source/variants/${variant}.svg`,`composites/${variant}.svg`,`composites/${variant}.png`,`previews/${variant}.jpg`]),"previews/contact-sheet.jpg","render-manifest.json"];
  fs.writeFileSync(path.join(root,"checksums.sha256"),checksumNames.sort().map(name=>`${digest(path.join(root,name))}  ${name}`).join("\n")+"\n");
  console.log("Rendered 6 Section 0 masters and recorded the complete input-to-preview contract.");
}finally{fs.rmSync(temporaryRoot,{recursive:true,force:true})}
