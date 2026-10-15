// Paths of rite pages (/{locale}/{prayerType}/{date}[/{select}]/{occasion}[?v=...]), which every page may link to

export function makePath(params) {
  return `/${params.locale}/${params.prayerType}/${params.date}${params.select == 'primarium' ? '' : '/' + params.select}/${params.occasion}${params.votives.length == 0 ? '' : '?v=' + params.votives.join('+')}`;
}

// An hour of the office on date, with params' locale and votives. Only the Little Office carries over from params'
// select; anything else (including the Office of the Dead) opens the Office of the day.
export function officeHourPath(params, date, occasion) {
  return makePath({
    locale: params.locale,
    prayerType: 'officium',
    date: date,
    select: params.select == 'officium-parvum-bmv' ? 'officium-parvum-bmv' : 'primarium',
    occasion: occasion,
    votives: params.votives
  });
}
