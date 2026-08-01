import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { composeAll } from './compose-from-layers.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const variants = ['quiet-weave', 'mutual-ground', 'living-threshold'];
const layerFiles = ['01-background.svg','02-main-subject.svg','03-supporting-elements.svg','04-atmosphere.svg','05-typography.svg','06-transition-candidate.svg'];
const inputNames = ['compose-from-layers.mjs','record-render.mjs','render-frame.html'];
const digest = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const chromeCandidates = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Chromium.app/Contents/MacOS/Chromium','google-chrome','chromium'];
const chrome = chromeCandidates.find((candidate) => candidate.includes('/') ? fs.existsSync(candidate) : spawnSync(candidate,['--version'],{stdio:'ignore',timeout:5000}).status === 0);
if (!chrome) throw new Error('Chrome or Chromium is required');
fs.mkdirSync(path.join(root,'composites'),{recursive:true});
await composeAll(root,variants);
fs.mkdirSync(path.join(root,'previews'),{recursive:true});
const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(),'farlens-section0-zero-base-render-'));

function run(command,args,label,timeout=45000){
  const result = spawnSync(command,args,{encoding:'utf8',timeout});
  if(result.status !== 0) throw new Error(`${label} failed\n${result.stderr || result.stdout}`);
}
function render(base){
  const url = pathToFileURL(path.join(root,'render-frame.html'));
  url.searchParams.set('asset',`${base}.svg`);
  const temporary = path.join(temporaryRoot,`${base}.png`);
  run(chrome,['--headless=new','--disable-gpu','--disable-extensions','--disable-background-networking','--disable-component-update','--disable-default-apps','--disable-sync','--metrics-recording-only','--no-first-run','--no-sandbox','--hide-scrollbars','--allow-file-access-from-files','--window-size=1080,1920','--force-device-scale-factor=1','--virtual-time-budget=1000',`--user-data-dir=${path.join(temporaryRoot,`profile-${base}`)}`,`--screenshot=${temporary}`,url.href],base);
  const bytes = fs.readFileSync(temporary);
  if(bytes.toString('ascii',1,4) !== 'PNG' || bytes.readUInt32BE(16) !== 1080 || bytes.readUInt32BE(20) !== 1920) throw new Error(`${base}: invalid render size`);
  fs.copyFileSync(temporary,path.join(root,'composites',`${base}.png`));
}

try {
  const renders = {};
  for(const variant of variants){
    render(variant);
    const png = path.join(root,'composites',`${variant}.png`);
    const preview = path.join(root,'previews',`${variant}.jpg`);
    run('ffmpeg',['-loglevel','error','-y','-i',png,'-vf','scale=360:640','-q:v','3',preview],`${variant} preview`);
    renders[variant] = {
      layers: Object.fromEntries(layerFiles.map((file) => [file,digest(path.join(root,'source','directions',variant,file))])),
      composite_svg_sha256: digest(path.join(root,'composites',`${variant}.svg`)),
      png_sha256: digest(png), preview_sha256: digest(preview)
    };
  }
  const contact = path.join(root,'previews','contact-sheet.jpg');
  const inputs = variants.flatMap((variant) => ['-i',path.join(root,'previews',`${variant}.jpg`)]);
  run('ffmpeg',['-loglevel','error','-y',...inputs,'-filter_complex','xstack=inputs=3:layout=0_0|360_0|720_0:fill=#eee6da','-q:v','3',contact],'contact sheet');
  const manifest = {contract:'Zero-base editable vector layers to masters and lightweight previews. External and reference-image inputs: none.',inputs:Object.fromEntries(inputNames.map((name)=>[name,digest(path.join(root,name))])),renders,contact_sheet_sha256:digest(contact)};
  fs.writeFileSync(path.join(root,'render-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  const checksumNames = [...inputNames,...variants.flatMap((variant)=>[...layerFiles.map((file)=>`source/directions/${variant}/${file}`),`composites/${variant}.svg`,`composites/${variant}.png`,`previews/${variant}.jpg`]),'previews/contact-sheet.jpg','render-manifest.json'];
  fs.writeFileSync(path.join(root,'checksums.sha256'),checksumNames.sort().map((name)=>`${digest(path.join(root,name))}  ${name}`).join('\n')+'\n');
  console.log('Rendered 3 zero-base Section 0 masters; no external or reference images were used.');
} finally { fs.rmSync(temporaryRoot,{recursive:true,force:true}); }
