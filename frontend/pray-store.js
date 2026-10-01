import { contentParameters, RITE_TITLES, makePath, nextHour, isCursus } from './routing.js';

// Wraps getting document cookies
function getOpt() {
  let optMatch = document.cookie.match(/(?:^|;\s*)opt=([^;]*)/);
  return optMatch ? decodeURIComponent(optMatch[1]).split('+').filter(t => t) : [];
}

async function fetchRite(path) {
  let contentParams = contentParameters(path);
  return fetch(`/api/rite?loc=${contentParams.locale}&date=${contentParams.date}&s=${contentParams.select}&occasion=${contentParams.occasion}+${contentParams.prayerType}&v=${contentParams.votives.join('+')}`).then(resp => resp.text());
}

export function makePrayStore() {

  let displayPath = window.location.pathname;
  let contentParams = () => contentParameters(displayPath);
  let rite = document.querySelector('main').innerHTML;
  let opt = getOpt();
  // Null suggests that a hardlink was manually pasted into the browser. This is handled within the user flow and is 'corrected' over to either hard or soft.
  let navigationType = history.state?.navigationType;

  async function loadRite(path) {
    rite = await fetchRite(path);
    displayPath = path;
    let match = rite.match(/<h1 class="large-title">(.*?)<\/h1>/);
    let dayTitle = match ? match[1].replace(/\.$/, '') : '';
    document.title = `${RITE_TITLES[contentParameters(path).occasion]} | ${dayTitle} | Liber Usualis`;
    window.scrollTo(0, 0);
  }

  async function navigateRite(path, navigationType=null, action='push') {
    displayPath = path;
    if (action == 'push') {
      history.pushState({navigationType: navigationType}, '', path);
    } else {
      history.replaceState({navigationType: navigationType}, '', path);
    }
    // NavigationType is only changed if explicitly specified by some action since hard vs soft navigationType significantly changes user flow; but many actions are the same between and therefore don't specify a type.
    if (navigationType) {
      navigationType = navigationType;
    }
    await loadRite(path);
  }

  async function setOpt(tags) {
    opt = tags;
    let cookie = tags.filter(t => t).join('+');
    if (cookie) {
      await cookieStore.set({name: 'opt', value: cookie, path: '/'});
    } else {
      await cookieStore.delete({name: 'opt', path: '/'});
    }
  }

  return {
    contentParams: contentParams,
    rite: () => rite,
    opt: () => opt,
    navigationType: () => navigationType,
    navigateRite: navigateRite,
    lastCompletedHour: () => {
      let lastCompleted = JSON.parse(localStorage.getItem('lastCursusHour') || 'null')
      if (lastCompleted) {
        return {...lastCompleted, date: Temporal.PlainDate.from(lastCompleted.date)};
      } else {
        return {...contentParameters(displayPath), prayerType: 'officium', date: Temporal.Now.plainDateISO(), select: 'primarium', occasion: 'matutinum-laudes', votives: []};
      }
    },
    markHourAsDone: () => {
      let current = contentParams();
      if (!isCursus(current)) {
        return;
      }

      let lastCursusHour = {
        date: current.date.toString(), prayerType: current.prayerType, select: current.select,
        occasion: current.occasion, votives: current.votives
      };
      localStorage.setItem('lastCursusHour', JSON.stringify(lastCursusHour));
    },
    toggleVotive: async (tag) => {
      let current = contentParams();
      let votives = current.votives.includes(tag) ? current.votives.filter(v => v != tag) : [...current.votives, tag];
      await navigateRite(makePath({...current, votives: votives}));
    },
    setDesired: async (select, optTag) => {
      let current = contentParams();
      let tags = opt.filter(t => t == 'privata');
      if (optTag) tags.push(optTag);
      await setOpt(tags);
      if (current.select != select) {
        await navigateRite(makePath({...current, select: select}));
      } else {
        await loadRite(displayPath);
      }
    },
    togglePriest: async () => {
      let current = contentParams();
      let tags = opt.includes('privata') ? opt.filter(t => t != 'privata') : [...opt, 'privata'];
      await setOpt(tags);
      await loadRite(displayPath);
    }
  }
}

async function fetchOrdo(date, time, votives) {
  return fetch(`/api/ordo?date=${date}&time=${time}&votives=${votives.join('+')}`)
}
export async function ordo(date, time, votives) {
  return await fetchOrdo(date, time, votives).then(response => response.json());
}

export function canSay(params, now) {
  if (params.occasion == 'matutinum-laudes' && Temporal.PlainDate.compare(params.date, now.toPlainDate().add({days: 1})) == 0) {
    return now.hour >= 14;
  }
  return Temporal.PlainDate.compare(params.date, now.toPlainDate()) == 0;
}

export function canIncrementHour(current, now) {
  return canSay(nextHour(current), now);
}
