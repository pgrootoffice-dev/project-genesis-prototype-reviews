import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

export const layerFiles = [
  '01-background.svg',
  '04-atmosphere.svg',
  '03-supporting-elements.svg',
  '02-main-subject.svg',
  '05-typography.svg',
  '06-transition-candidate.svg',
];

const svgBody = (svg) => svg.replace(/^.*?<svg[^>]*>/s, '').replace(/<\/svg>\s*$/s, '').trim();

export async function readDirectionComposite(root, slug) {
  const dir = path.join(root, 'source', 'directions', slug);
  const bodies = await Promise.all(layerFiles.map(async (file) => svgBody(await readFile(path.join(dir, file), 'utf8'))));
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">\n<metadata>FARLENS Section 0 zero-base study; ${slug}; composed only from editable vector layers; no external image inputs</metadata>\n${bodies.join('\n')}\n</svg>\n`;
}

export async function composeDirection(root, slug) {
  const composite = await readDirectionComposite(root, slug);
  await writeFile(path.join(root, 'composites', `${slug}.svg`), composite);
  return composite;
}

export async function composeAll(root, slugs) {
  for (const slug of slugs) await composeDirection(root, slug);
}
