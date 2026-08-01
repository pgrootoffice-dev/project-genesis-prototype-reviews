import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { readDirectionComposite, layerFiles as renderLayerFiles } from './compose-from-layers.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
const variants = ['quiet-weave','mutual-ground','living-threshold'];
const sourceLayerFiles = ['01-background.svg','02-main-subject.svg','03-supporting-elements.svg','04-atmosphere.svg','05-typography.svg','06-transition-candidate.svg'];
const directInputs = ['compose-from-layers.mjs','record-render.mjs','render-frame.html'];
const fail = (message) => { throw new Error(message); };
const digest = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const manifestPath = path.join(root,'render-manifest.json');
if(!fs.existsSync(manifestPath)) fail('render-manifest.json missing; run node record-render.mjs');
const manifest = JSON.parse(fs.readFileSync(manifestPath,'utf8'));
if(!manifest.contract.includes('External and reference-image inputs: none')) fail('render contract must declare zero image inputs');
for(const input of directInputs) if(manifest.inputs?.[input] !== digest(path.join(root,input))) fail(`${input}: build input changed; rerender`);
if(JSON.stringify(renderLayerFiles) !== JSON.stringify(['01-background.svg','04-atmosphere.svg','03-supporting-elements.svg','02-main-subject.svg','05-typography.svg','06-transition-candidate.svg'])) fail('unexpected layer render order');

for(const variant of variants){
  const sourceDir = path.join(root,'source','directions',variant);
  const composite = path.join(root,'composites',`${variant}.svg`);
  const png = path.join(root,'composites',`${variant}.png`);
  const preview = path.join(root,'previews',`${variant}.jpg`);
  for(const file of [...sourceLayerFiles.map((name)=>path.join(sourceDir,name)),composite,png,preview]) if(!fs.existsSync(file)) fail(`${variant}: missing ${path.relative(root,file)}`);
  const currentComposite = fs.readFileSync(composite,'utf8');
  const expectedComposite = await readDirectionComposite(root,variant);
  if(currentComposite !== expectedComposite) fail(`${variant}: composite stale relative to layers`);
  const bytes = fs.readFileSync(png);
  if(bytes.toString('ascii',1,4) !== 'PNG' || bytes.readUInt32BE(16) !== 1080 || bytes.readUInt32BE(20) !== 1920) fail(`${variant}: expected 1080x1920 PNG`);
  const record = manifest.renders?.[variant];
  for(const file of sourceLayerFiles) if(record?.layers?.[file] !== digest(path.join(sourceDir,file))) fail(`${variant}/${file}: stale lineage`);
  if(record.composite_svg_sha256 !== digest(composite) || record.png_sha256 !== digest(png) || record.preview_sha256 !== digest(preview)) fail(`${variant}: stale render lineage`);
}

const forbidden = /farlens-logo|ceo-original|aperture-assembly|field-alignment|shared-horizon|two-viewpoints|current-knot|folded-orbit|data:image|<image\b/i;
for(const relative of [...directInputs,'index.html','styles.css','script.js','variants.json','README.md',...variants.flatMap((variant)=>sourceLayerFiles.map((file)=>`source/directions/${variant}/${file}`))]){
  const text = fs.readFileSync(path.join(root,relative),'utf8');
  if(forbidden.test(text)) fail(`${relative}: old direction or image reference found`);
}
const html = fs.readFileSync(path.join(root,'index.html'),'utf8');
if((html.match(/class="frame-button"/g)||[]).length !== 3) fail('review page must expose exactly 3 tap targets');
for(const variant of variants) if(!html.includes(`previews/${variant}.jpg`) || !html.includes(`composites/${variant}.png`)) fail(`${variant}: page reference missing`);
if(!html.includes('Previous / Rejected Direction')) fail('rejected history boundary missing');
const contact = path.join(root,'previews','contact-sheet.jpg');
if(manifest.contact_sheet_sha256 !== digest(contact)) fail('contact sheet stale');
const ledgerLines = fs.readFileSync(path.join(root,'checksums.sha256'),'utf8').trim().split('\n');
const ledgerPaths = [];
for(const line of ledgerLines){const [hash,...parts] = line.split(/\s+/); const relative=parts.join(' '); ledgerPaths.push(relative); if(!fs.existsSync(path.join(root,relative)) || digest(path.join(root,relative)) !== hash) fail(`${relative}: stale checksum`);}
const expectedPaths = [...directInputs,...variants.flatMap((variant)=>[...sourceLayerFiles.map((file)=>`source/directions/${variant}/${file}`),`composites/${variant}.svg`,`composites/${variant}.png`,`previews/${variant}.jpg`]),'previews/contact-sheet.jpg','render-manifest.json'].sort();
const actualPaths = [...new Set(ledgerPaths)].sort();
if(actualPaths.length !== ledgerPaths.length || JSON.stringify(actualPaths) !== JSON.stringify(expectedPaths)) fail('checksum ledger path set mismatch');
console.log('PASS: 3 zero-base 1080x1920 masters, 18 editable layers, lineage, tap targets, and old-logo reference exclusion verified.');
