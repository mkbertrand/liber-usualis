const CURSUS_OCCASIONS = ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium'];

export function makePrayStore() {
  return {
    rite: '',
    displayPath: window.location.pathname
  }
}

export function isRitePath(path) {
  return /\/[a-z]{2}\/(officium|ritus)\/\d{4}-\d{1,2}-\d{1,2}(\/|$)/.test(path);
}

export function contentParameters(path) {
  if (!isRitePath(path)) return {};
  let pathVariables = path.match(/\/(?<locale>[a-z]{2})\/(?<prayerType>officium|ritus)\/(?<date>\d{4}-\d{1,2}-\d{1,2})(?:\/(?<select>officium-parvum-bmv|officium-defunctorum))?\/(?<occasion>[a-z-]+)/).groups;
  let params = new URLSearchParams(window.location.search);
  let votivestr = params.get('v');
  // For whatever reason, + is replaced with space
  let votives = votivestr ? votivestr.replaceAll(' ', '+').split('+') : [];
  let optMatch = document.cookie.match(/(?:^|;\s*)opt=([^;]*)/);
  let opt = optMatch ? decodeURIComponent(optMatch[1]).split('+').filter(t => t) : [];
  return {'locale': pathVariables.locale, 'prayerType': pathVariables.prayerType, 'date': Temporal.PlainDate.from(pathVariables.date), 'select': pathVariables.select || 'primarium', 'occasion': pathVariables.occasion, 'votives': votives, 'opt': opt};
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
