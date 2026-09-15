// Baut aus @phosphor-icons/react ein SVG-Sprite mit genau den Icons, die die App nutzt.
// Gewicht regular, gefüllte Pfade. Die Symbol-IDs tragen weiter Material-Namen,
// damit kein JS angefasst werden muss.
import { readFileSync, writeFileSync } from 'node:fs';

const P = 'C:/Users/bened/Documents/GitHub/bagruber/haushaltvis/node_modules/@phosphor-icons/react/dist/defs';

// Material-Icons-Name → Phosphor-Name
const MAP = {
  account_balance: 'Bank',
  arrow_back:      'ArrowLeft',
  calendar_month:  'CalendarDots',
  chevron_left:    'CaretLeft',
  chevron_right:   'CaretRight',
  close:           'X',
  contrast:        'CircleHalf',
  edit_note:       'NotePencil',
  email:           'Envelope',
  expand_more:     'CaretDown',
  groups:          'UsersThree',
  help_outline:    'Question',
  how_to_vote:     'ListChecks',
  info:            'Info',
  insights:        'ChartLineUp',
  language:        'Globe',
  link:            'Link',
  mail:            'Envelope',
  open_in_new:     'ArrowSquareOut',
  schedule:        'Clock',
  search:          'MagnifyingGlass',
  swap_horiz:      'ArrowsLeftRight',
  table_rows:      'Rows',
  text_increase:   'TextAa',
  sliders:         'SlidersHorizontal',
  // aus tags.json
  architecture:        'PencilRuler',
  commute:             'Bus',
  museum:              'MaskHappy',
  park:                'Tree',
  school:              'GraduationCap',
  shield:              'Shield',
  sports:              'SoccerBall',
  storefront:          'Storefront',
  volunteer_activism:  'HandHeart',
  // aus members.json (bodies)
  engineering: 'HardHat',
  fact_check:  'ClipboardText',
  payments:    'Money',
  person:      'User',
  savings:     'PiggyBank',
  water_drop:  'Drop',
  // Timeline
  description:  'FileText',
  flag:         'Flag',
  // Timeline-Marker sitzen auf der Achse: blanke Zeichen, keine Kreise —
  // sonst steht ein Kreis im Kreis.
  cancel:       'X',
  check_circle: 'Check',
  // Identitaets-Chips, gewählt am 15.09.2026 (Probe Formsprache)
  queer:      'Rainbow',
  flinta:     'GenderFemale',
  migrant:    'GlobeHemisphereWest',
  disability: 'Wheelchair',
  // Funktionen im Rat, gewählt am 15.09.2026; Megaphone noch nicht befriedigend
  referent:   'Megaphone',
  ausschuss:  'UsersThree',
  vorsitz:    'Gavel',
  aufsichtsrat: 'BuildingOffice',
  history:    'Clock',
  star:       'Star',
  badge:      'Medal',
  // Kontaktwege auf Profilen (16.09.2026): Phosphor statt Font-Awesome-Pfaden
  instagram:  'InstagramLogo',
  threads:    'ThreadsLogo',
  linkedin:   'LinkedinLogo',
  facebook:   'FacebookLogo',
};

const seen = new Map();
const symbols = [];
const missing = [];

for (const [name, phosphor] of Object.entries(MAP)) {
  if (seen.has(phosphor)) { seen.get(phosphor).push(name); continue; }
  seen.set(phosphor, [name]);
  let src;
  try {
    src = readFileSync(`${P}/${phosphor}.es.js`, 'utf8');
  } catch { missing.push(`${name} → ${phosphor}`); continue; }
  const regular = src.slice(src.indexOf('"regular"'), src.indexOf('"thin"'));
  const body = [...regular.matchAll(/createElement\("(\w+)", \{([^}]*)\}/g)]
    .map(([, tag, props]) => {
      const attrs = [...props.matchAll(/(\w+): "([^"]*)"/g)].map(([, k, v]) => `${k}="${v}"`).join(' ');
      return `<${tag} ${attrs}/>`;
    }).join('');
  if (!body) { missing.push(`${name} → ${phosphor} (keine Pfade)`); continue; }
  symbols.push({ phosphor, body });
}

if (missing.length) {
  console.error('FEHLT:', missing.join(', '));
  process.exit(1);
}

const out = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
${symbols.map(s => {
  const names = seen.get(s.phosphor);
  return `<symbol id="i-${names[0]}" viewBox="0 0 256 256" fill="currentColor">${s.body}</symbol>`
       + names.slice(1).map(n => `\n<symbol id="i-${n}" viewBox="0 0 256 256"><use href="#i-${names[0]}"/></symbol>`).join('');
}).join('\n')}
</svg>`;

writeFileSync(process.argv[2], out);
console.log(`${symbols.length} Symbole für ${Object.keys(MAP).length} Namen, ${out.length} Bytes`);
