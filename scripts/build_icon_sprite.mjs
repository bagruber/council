// Baut aus lucide-react ein SVG-Sprite mit genau den Icons, die die App nutzt.
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const L = 'C:/Users/bened/Documents/GitHub/bagruber/pridemap/node_modules/lucide-react/dist/esm/icons';

// Material-Icons-Name → Lucide-Name
const MAP = {
  account_balance: 'landmark',
  arrow_back:      'arrow-left',
  calendar_month:  'calendar',
  chevron_left:    'chevron-left',
  chevron_right:   'chevron-right',
  close:           'x',
  contrast:        'contrast',
  edit_note:       'square-pen',
  email:           'mail',
  expand_more:     'chevron-down',
  groups:          'users',
  help_outline:    'circle-question-mark',   // circle-help ist nur ein Alias
  how_to_vote:     'vote',
  info:            'info',
  insights:        'chart-line',
  language:        'globe',
  link:            'link',
  mail:            'mail',
  open_in_new:     'external-link',
  schedule:        'clock',
  search:          'search',
  settings:        'settings',
  swap_horiz:      'arrow-left-right',
  table_rows:      'rows-3',
  text_increase:   'a-large-small',
  // aus tags.json
  architecture:        'drafting-compass',
  commute:             'bus',
  museum:              'drama',
  park:                'trees',
  school:              'graduation-cap',
  shield:              'shield',
  sports:              'trophy',
  storefront:          'store',
  volunteer_activism:  'heart-handshake',
  // aus members.json (bodies)
  engineering: 'hard-hat',
  fact_check:  'clipboard-check',
  payments:    'banknote',
  person:      'user',
  savings:     'piggy-bank',
  water_drop:  'droplet',
  // Timeline
  description:  'file-text',
  flag:         'flag',
  cancel:       'circle-x',
  check_circle: 'circle-check',
};

const attrs = o => Object.entries(o)
  .filter(([k]) => k !== 'key')
  .map(([k, v]) => `${k}="${v}"`).join(' ');

const seen = new Map();
const symbols = [];
const missing = [];

for (const [name, lucide] of Object.entries(MAP)) {
  if (seen.has(lucide)) { seen.get(lucide).push(name); continue; }
  seen.set(lucide, [name]);
  let mod;
  try {
    mod = await import(pathToFileURL(`${L}/${lucide}.mjs`).href);
  } catch { missing.push(`${name} → ${lucide}`); continue; }
  const body = mod.__iconNode.map(([tag, o]) => `<${tag} ${attrs(o)}/>`).join('');
  symbols.push({ lucide, body });
}

if (missing.length) {
  console.error('FEHLT:', missing.join(', '));
  process.exit(1);
}

const out = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
${symbols.map(s => {
  const names = seen.get(s.lucide);
  return `<symbol id="i-${names[0]}" viewBox="0 0 24 24" fill="none" stroke="currentColor" `
       + `stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${s.body}</symbol>`
       + names.slice(1).map(n => `\n<symbol id="i-${n}" viewBox="0 0 24 24"><use href="#i-${names[0]}"/></symbol>`).join('');
}).join('\n')}
</svg>`;

writeFileSync(process.argv[2], out);
console.log(`${symbols.length} Symbole für ${Object.keys(MAP).length} Namen, ${out.length} Bytes`);
