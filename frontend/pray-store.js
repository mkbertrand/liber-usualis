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
    opt: getOpt(),
    // Null suggests that a hardlink was manually pasted into the browser. This is handled within the user flow and is 'corrected' over to either hard or soft.
    navigationType: history.state?.navigationType
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

export async function navigateRite(prayState, path, navigationType=null, action='push') {
  prayState.displayPath = path;
  if (action == 'push') {
    history.pushState({navigationType: navigationType}, '', path);
  } else {
    history.replaceState({navigationType: navigationType}, '', path);
  }
  // NavigationType is only changed if explicitly specified by some action since hard vs soft navigationType significantly changes user flow; but many actions are the same between and therefore don't specify a type.
  if (navigationType) {
    prayState.navigationType = navigationType;
  }
  await loadRite(prayState, path);
}
