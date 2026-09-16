// Baut aus @phosphor-icons/react ein SVG-Sprite mit genau den Icons, die die App nutzt.
// Gewicht regular, gefüllte Pfade. Die Symbol-IDs tragen weiter Material-Namen,
// damit kein JS angefasst werden muss.
import { readFileSync, writeFileSync } from 'node:fs';

const P = 'C:/Users/bened/Documents/GitHub/bagruber/haushaltvis/node_modules/@phosphor-icons/react/dist/defs';

// Material-Icons-Name → Phosphor-Name, oder [Name, Gewicht].
// Gewicht `bold` für die Kontaktzeichen: sie stehen als weiße Glyphe in einer
// 26 px kleinen farbigen Fläche, `regular` fällt dort auseinander (16.09.2026).
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
  instagram:       ['InstagramLogo', 'bold'],
  threads:         ['ThreadsLogo', 'bold'],
  facebook:        ['FacebookLogo', 'bold'],
  kontakt_email:   ['Envelope', 'bold'],
  kontakt_website: ['Globe', 'bold'],
};

// Zeichen, die es bei Phosphor nicht gibt. LinkedIn führt sein Logo als
// schlichtes „in“; Phosphor kennt nur die Variante im Kasten.
// Pfad: Font Awesome Free 6.5.1, „linkedin-in“ (CC BY 4.0).
const EIGEN = {
  linkedin: {
    viewBox: '0 0 448 512',
    body: '<path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/>',
  },
};

// Die Gewichte stehen in den defs in fester Reihenfolge; geschnitten wird vom
// gesuchten Schlüssel bis zum nächsten.
const GRENZEN = { bold: ['"bold"', '"duotone"'], regular: ['"regular"', '"thin"'] };

const seen = new Map();
const symbols = [];
const missing = [];

for (const [name, eintrag] of Object.entries(MAP)) {
  const [phosphor, gewicht = 'regular'] = Array.isArray(eintrag) ? eintrag : [eintrag];
  const schluessel = `${phosphor}|${gewicht}`;
  if (seen.has(schluessel)) { seen.get(schluessel).push(name); continue; }
  seen.set(schluessel, [name]);
  let src;
  try {
    src = readFileSync(`${P}/${phosphor}.es.js`, 'utf8');
  } catch { missing.push(`${name} → ${phosphor}`); continue; }
  const [von, bis] = GRENZEN[gewicht];
  const schnitt = src.slice(src.indexOf(von), src.indexOf(bis));
  const body = [...schnitt.matchAll(/createElement\("(\w+)", \{([^}]*)\}/g)]
    .map(([, tag, props]) => {
      const attrs = [...props.matchAll(/(\w+): "([^"]*)"/g)].map(([, k, v]) => `${k}="${v}"`).join(' ');
      return `<${tag} ${attrs}/>`;
    }).join('');
  if (!body) { missing.push(`${name} → ${phosphor} (${gewicht}, keine Pfade)`); continue; }
  symbols.push({ schluessel, body, viewBox: '0 0 256 256' });
}

for (const [name, zeichen] of Object.entries(EIGEN)) {
  seen.set(name, [name]);
  symbols.push({ schluessel: name, body: zeichen.body, viewBox: zeichen.viewBox });
}

if (missing.length) {
  console.error('FEHLT:', missing.join(', '));
  process.exit(1);
}

const out = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
${symbols.map(s => {
  const names = seen.get(s.schluessel);
  return `<symbol id="i-${names[0]}" viewBox="${s.viewBox}" fill="currentColor">${s.body}</symbol>`
       + names.slice(1).map(n => `\n<symbol id="i-${n}" viewBox="${s.viewBox}"><use href="#i-${names[0]}"/></symbol>`).join('');
}).join('\n')}
</svg>`;

writeFileSync(process.argv[2], out);
console.log(`${symbols.length} Symbole für ${Object.keys(MAP).length + Object.keys(EIGEN).length} Namen, ${out.length} Bytes`);
