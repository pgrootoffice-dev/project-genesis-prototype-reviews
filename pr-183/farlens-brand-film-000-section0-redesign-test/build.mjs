import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { composeAll } from './compose-from-layers.mjs';

const root = path.dirname(fileURLToPath(import.meta.url));
if (!process.argv.includes('--initialize')) {
  throw new Error('Refusing to overwrite editable source layers. Use --initialize only when intentionally resetting all three directions.');
}
const head = '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">';
const wrap = (name, body) => `${head}\n<metadata>${name}; editable vector layer; no external image input</metadata>\n${body}\n</svg>\n`;

const directions = {
  'quiet-weave': {
    '01-background.svg': `<rect width="1080" height="1920" fill="#F2EADF"/>
<path d="M0 0H1080V560C846 490 668 533 476 604C287 674 142 683 0 627Z" fill="#E7DDD0" opacity=".62"/>
<path d="M0 1458C256 1386 415 1437 593 1506C773 1576 927 1582 1080 1522V1920H0Z" fill="#E9DFD2" opacity=".72"/>`,
    '02-main-subject.svg': `<path d="M214 828L456 676L534 726L342 877L514 993L432 1048L205 900Z" fill="#C26F57"/>
<path d="M866 730L633 684L547 747L751 803L568 958L659 1000L876 814Z" fill="#647C73"/>
<path d="M342 877L514 993L568 958L751 803L633 774L533 858L456 807Z" fill="#263F4A"/>
<path d="M514 993L432 1048L517 1103L659 1000L568 958Z" fill="#A99068"/>`,
    '03-supporting-elements.svg': `<path d="M86 662L278 582L345 625L154 716Z" fill="#B9A487" opacity=".7"/>
<path d="M752 1124L930 1026L982 1062L802 1170Z" fill="#8C746F" opacity=".55"/>
<path d="M132 1160L278 1088L335 1126L188 1205Z" fill="#87968B" opacity=".48"/>
<path d="M779 548L931 608L902 653L740 590Z" fill="#B7A789" opacity=".48"/>`,
    '04-atmosphere.svg': `<path d="M111 452L366 527" stroke="#8A6B60" stroke-width="3" opacity=".22"/>
<path d="M712 1368L966 1450" stroke="#51676B" stroke-width="3" opacity=".2"/>
<path d="M152 1323L340 1266" stroke="#9E835F" stroke-width="2" opacity=".2"/>`,
    '05-typography.svg': `<g id="typography" opacity="0"><text x="540" y="1670" text-anchor="middle">Reserved: optional FARLENS wordmark, not used in this study</text></g>`,
    '06-transition-candidate.svg': `<path d="M533 858L547 747" stroke="#EAC994" stroke-width="10" stroke-linecap="square"/>
<path d="M533 858L568 958" stroke="#EAC994" stroke-width="10" stroke-linecap="square"/>
<path d="M533 858L456 807" stroke="#EAC994" stroke-width="10" stroke-linecap="square"/>`,
  },
  'mutual-ground': {
    '01-background.svg': `<rect width="1080" height="1920" fill="#EFE6D9"/>
<path d="M0 314L392 130L1080 362V0H0Z" fill="#E5D8C8" opacity=".72"/>
<path d="M0 1612L380 1746L1080 1540V1920H0Z" fill="#E1D7CA" opacity=".65"/>`,
    '02-main-subject.svg': `<path d="M91 1004L344 790L505 867L505 1040L318 1157Z" fill="#895C5A"/>
<path d="M989 906L724 742L575 844L575 1023L778 1117Z" fill="#667B69"/>
<path d="M505 867L575 844L676 931L575 1023L505 1040L410 952Z" fill="#293D46"/>
<path d="M505 867L575 844V1023L505 1040Z" fill="#D6A96D"/>`,
    '03-supporting-elements.svg': `<path d="M169 724L302 616L431 686L344 790Z" fill="#B77A66" opacity=".62"/>
<path d="M840 612L941 685L824 785L724 742Z" fill="#84927C" opacity=".66"/>
<path d="M195 1242L318 1157L418 1219L287 1309Z" fill="#C39A75" opacity=".54"/>
<path d="M778 1117L903 1193L817 1269L688 1194Z" fill="#7C8580" opacity=".48"/>`,
    '04-atmosphere.svg': `<path d="M94 491L393 375L550 425L706 372L987 467" fill="none" stroke="#9E8271" stroke-width="3" opacity=".2"/>
<path d="M136 1414L381 1510L550 1466L733 1514L951 1427" fill="none" stroke="#62736F" stroke-width="3" opacity=".18"/>`,
    '05-typography.svg': `<g id="typography" opacity="0"><text x="540" y="1670" text-anchor="middle">Reserved: optional FARLENS wordmark, not used in this study</text></g>`,
    '06-transition-candidate.svg': `<path d="M540 728V844" stroke="#B18B67" stroke-width="7" opacity=".7"/>
<path d="M540 1041V1202" stroke="#B18B67" stroke-width="7" opacity=".7"/>
<path d="M540 1202L468 1290M540 1202L612 1290" stroke="#B18B67" stroke-width="5" opacity=".48"/>`,
  },
  'living-threshold': {
    '01-background.svg': `<rect width="1080" height="1920" fill="#F0E8DC"/>
<path d="M0 0H1080V1920H0Z" fill="#C9B8A0" opacity=".08"/>
<path d="M0 1540L279 1466L552 1532L813 1452L1080 1517V1920H0Z" fill="#DED5C8"/>`,
    '02-main-subject.svg': `<path d="M288 1132L347 750L474 604L531 754L487 1174Z" fill="#556C66"/>
<path d="M487 1174L531 754L608 605L723 768L794 1124Z" fill="#30484D"/>
<path d="M531 754L608 605L657 762L604 1173L487 1174Z" fill="#B86755"/>
<path d="M487 1174L604 1173L647 1307L443 1308Z" fill="#AD8D63"/>`,
    '03-supporting-elements.svg': `<path d="M176 986L253 828L347 750L317 1033Z" fill="#819183" opacity=".68"/>
<path d="M723 768L829 839L909 997L764 1011Z" fill="#8C7771" opacity=".6"/>
<path d="M237 1261L288 1132L443 1308L350 1382Z" fill="#BE9B73" opacity=".52"/>
<path d="M647 1307L794 1124L853 1267L742 1394Z" fill="#768681" opacity=".48"/>
<path d="M347 750L400 561L474 604Z" fill="#A8A07E" opacity=".62"/>
<path d="M608 605L666 544L723 768Z" fill="#B69A7E" opacity=".56"/>`,
    '04-atmosphere.svg': `<path d="M122 570L274 481L411 496" fill="none" stroke="#8B755F" stroke-width="3" opacity=".2"/>
<path d="M685 474L828 500L954 598" fill="none" stroke="#5F756D" stroke-width="3" opacity=".2"/>
<path d="M104 1442L313 1396M768 1412L967 1465" stroke="#7C6B60" stroke-width="3" opacity=".18"/>`,
    '05-typography.svg': `<g id="typography" opacity="0"><text x="540" y="1670" text-anchor="middle">Reserved: optional FARLENS wordmark, not used in this study</text></g>`,
    '06-transition-candidate.svg': `<path d="M531 754L608 605" stroke="#F0C88F" stroke-width="9"/>
<path d="M531 754L604 1173" stroke="#F0C88F" stroke-width="9"/>
<path d="M604 1173L647 1307" stroke="#F0C88F" stroke-width="7" opacity=".72"/>`,
  },
};

await mkdir(path.join(root, 'composites'), { recursive: true });
for (const [slug, layers] of Object.entries(directions)) {
  const dir = path.join(root, 'source', 'directions', slug);
  await mkdir(dir, { recursive: true });
  for (const [filename, body] of Object.entries(layers)) await writeFile(path.join(dir, filename), wrap(`${slug}; ${filename}`, body));
}
await composeAll(root, Object.keys(directions));
console.log(`Built ${Object.keys(directions).length} zero-base directions with six editable layers each.`);
