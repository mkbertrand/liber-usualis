import { contentParameters, RITE_TITLES } from './routing.js';

// Wraps getting document cookies
function getOpt() {
  let optMatch = document.cookie.match(/(?:^|;\s*)opt=([^;]*)/);
  return optMatch ? decodeURIComponent(optMatch[1]).split('+').filter(t => t) : [];
}

export function makePrayStore() {
  return {
    rite: document.querySelector('main').innerHTML,
    displayPath: window.location.pathname,
    opt: getOpt()
  }
}

export async function setOpt(prayState, tags) {
  prayState.opt = tags;
  let opt = tags.filter(t => t).join('+');
  if (opt) {
    await cookieStore.set({name: 'opt', value: opt, path: '/'});
  } else {
    await cookieStore.delete({name: 'opt', path: '/'});
  }
}

// Returns a default last completed hour of today's Matins and Lauds (not a pure function)
export function lastCompletedHour(params) {
  let lastCompleted = JSON.parse(localStorage.getItem('lastCursusHour') || 'null')
  if (lastCompleted) {
    return {...lastCompleted, date: Temporal.PlainDate.from(lastCompleted.date)};
  } else {
    return {...contentParameters(params.displayPath), prayerType: 'officium', date: Temporal.Now.plainDateISO(), select: 'primarium', occasion: 'matutinum-laudes', votives: []};
  }
}

async function fetchRite(path) {
  let contentParams = contentParameters(path);
  return fetch(`/api/rite?loc=${contentParams.locale}&date=${contentParams.date}&s=${contentParams.select}&occasion=${contentParams.occasion}+${contentParams.prayerType}&v=${contentParams.votives.join('+')}`).then(resp => resp.text());
}

export async function loadRite(prayState, path) {
  prayState.rite = await fetchRite(path);
  prayState.displayPath = path;
  let match = prayState.rite.match(/<h1 class="large-title">(.*?)<\/h1>/);
  let dayTitle = match ? match[1].replace(/\.$/, '') : '';
  document.title = `${RITE_TITLES[contentParameters(path).occasion]} | ${dayTitle} | Liber Usualis`;
  window.scrollTo(0, 0);
}

export async function navigateRite(prayState, path, navigationType='soft', action='push') {
  prayState.displayPath = path;
  if (action == 'push') {
    history.pushState({navigationType: navigationType}, '', path);
  } else {
    history.replaceState({navigationType: navigationType}, '', path);
  }
  await loadRite(prayState, path);
}
