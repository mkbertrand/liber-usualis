export const CURSUS_OCCASIONS = ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium'];
export const RITE_TITLES = {
  'matutinum-laudes': 'Matutinum & Laudes', 'prima': 'Prima', 'tertia': 'Tertia',
  'sexta': 'Sexta', 'nona': 'Nona', 'vesperae': 'Vesperæ', 'completorium': 'Completorium',
  'psalmi-graduales': 'Psalmi Graduales', 'psalmi-poenitentiales': 'Psalmi Pœnitentiales',
  'ordo-commendationis-animae': 'Ordo Commendationis Animæ',
  'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis',
  'pro-prandio': 'Benedictio Mensæ (Pro Prandio)', 'pro-coena': 'Benedictio Mensæ (Pro Cœna)',
  'itinerarium': 'Itinerarium Clericorum'
};

export function isRitePath(path) {
  return /\/[a-z]{2}\/(officium|ritus)\/\d{4}-\d{1,2}-\d{1,2}(\/|$)/.test(path);
}

// path may include the query string (?v=...), which carries the votives
export function contentParameters(path) {
  let [pathname, search = ''] = path.split('?');
  if (!isRitePath(pathname)) return {};
  let pathVariables = pathname.match(/\/(?<locale>[a-z]{2})\/(?<prayerType>officium|ritus)\/(?<date>\d{4}-\d{1,2}-\d{1,2})(?:\/(?<select>officium-parvum-bmv|officium-defunctorum))?\/(?<occasion>[a-z-]+)/).groups;
  let votivestr = new URLSearchParams(search).get('v');
  // For whatever reason, + is replaced with space
  let votives = votivestr ? votivestr.replaceAll(' ', '+').split('+') : [];
  return {'locale': pathVariables.locale, 'prayerType': pathVariables.prayerType, 'date': Temporal.PlainDate.from(pathVariables.date), 'select': pathVariables.select || 'primarium', 'occasion': pathVariables.occasion, 'votives': votives};
}

export function makePath(params) {
  return `/${params.locale}/${params.prayerType}/${params.date}${params.select == 'primarium' ? '' : '/' + params.select}/${params.occasion}${params.votives.length == 0 ? '' : '?v=' + params.votives.join('+')}`;
}
export function isCursus(params) {
  return params.prayerType == 'officium' && params.select != 'officium-defunctorum'
    && CURSUS_OCCASIONS.includes(params.occasion);
}

export function nextHour(current) {
  let idx = CURSUS_OCCASIONS.indexOf(current.occasion);
  let wrapping = idx == CURSUS_OCCASIONS.length - 1;
  return {
    ...current,
    date: wrapping ? current.date.add({days: 1}) : current.date,
    occasion: wrapping ? CURSUS_OCCASIONS[0] : CURSUS_OCCASIONS[idx + 1],
    select: current.select,
    votives: current.votives
  };
}

export function suggestOccasion(now) {
  let hour = now.hour;
  if (hour < 6 || hour > 21) return 'matutinum-laudes';
  if (hour < 8) return 'prima';
  if (hour < 11) return 'tertia';
  if (hour < 14) return 'sexta';
  if (hour < 16) return 'nona';
  if (hour < 20) return 'vesperae';
  return 'completorium';
}
