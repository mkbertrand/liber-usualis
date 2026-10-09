import { signal, computed, batch } from '@preact/signals-core';
import { contentParameters, isRitePath, RITE_TITLES, makePath, nextHour, isCursus, suggestOccasion } from './routing.js';

async function fetchRite(path) {
  let contentParams = contentParameters(path);
  return fetch(`/api/rite?loc=${contentParams.locale}&date=${contentParams.date}&s=${contentParams.select}&occasion=${contentParams.occasion}+${contentParams.prayerType}&v=${contentParams.votives.join('+')}`).then(resp => resp.text());
}

// Day title straight from the rendered rite's <h1 class="large-title">, without the trailing period
// rite_title() (renderer/rendering_utils.py) always appends
function dayTitle(rite) {
  let match = rite.match(/<h1 class="large-title">(.*?)<\/h1>/);
  return match ? match[1].replace(/\.$/, '') : '';
}

export function makePrayStore() {
  // Always a rite path once init() has run, since a bare /pray visit is immediately redirected; bindings rely on this
  const displayPath = signal(window.location.pathname + window.location.search);
  // Document is hydrated (after a manner of speaking) so initial value of rite should be the already-provided HTML
  const rite = signal(document.querySelector('main').innerHTML);
  const opt = signal((() => {
    let optMatch = document.cookie.match(/(?:^|;\s*)opt=([^;]*)/);
    return optMatch ? decodeURIComponent(optMatch[1]).split('+').filter(t => t) : [];
  })());
  // Null suggests that a hardlink was manually pasted into the browser. This is handled within the user flow and is 'corrected' over to either hard or soft.
  const navigationType = signal(history.state?.navigationType ?? null);

  const lastCursusHour = signal((() => {
    try {
      let lastCompleted = JSON.parse(localStorage.getItem('lastCursusHour') || 'null');
      return lastCompleted ? {...lastCompleted, date: Temporal.PlainDate.from(lastCompleted.date)} : null;
    } catch {
      return null;
    }
  })());
  const now = signal(Temporal.Now.plainDateTimeISO());

  const contentParams = computed(() => contentParameters(displayPath.value));
  // The rite whose text is on the page. displayPath moves as soon as a navigation starts, so links follow at once;
  // this moves with the text itself, for what belongs to the rite shown (the next-hour button, marking it prayed).
  const ritePath = signal(displayPath.value);
  const riteParams = computed(() => contentParameters(ritePath.value));

  async function loadRite(path) {
    let html = await fetchRite(path);
    // A later navigation has superseded this one
    if (displayPath.value != path) return;
    batch(() => {
      rite.value = html;
      ritePath.value = path;
    });
    document.title = `${RITE_TITLES[contentParameters(path).occasion]} | ${dayTitle(html)} | Liber Usualis`;
    window.scrollTo(0, 0);
  }

  async function navigateRite(path, newNavigationType=null, action='push') {
    // NavigationType is only changed if explicitly specified by some action since hard vs soft navigationType significantly changes user flow; but many actions are the same between and therefore don't specify a type.
    batch(() => {
      if (newNavigationType) {
        navigationType.value = newNavigationType;
      }
      displayPath.value = path;
    });
    if (action == 'push') {
      history.pushState({navigationType: navigationType.value}, '', path);
    } else {
      history.replaceState({navigationType: navigationType.value}, '', path);
    }
    await loadRite(path);
  }

  async function setOpt(tags) {
    opt.value = tags;
    let cookie = tags.filter(t => t).join('+');
    if (cookie) {
      await cookieStore.set({name: 'opt', value: cookie, path: '/'});
    } else {
      await cookieStore.delete({name: 'opt', path: '/'});
    }
  }

  function bestHour() {
    let locale = window.location.pathname.match(/^\/([a-z]{2})\//)?.[1] || 'en';
    let currentNow = now.value;
    if (lastCursusHour.value === null || !canIncrementHour(lastCursusHour.value, currentNow)) {
      return {
        locale: locale,
        prayerType: 'officium',
        date: currentNow.toPlainDate(),
        select: 'primarium',
        occasion: suggestOccasion(currentNow),
        votives: []
      }
    } else {
      return {...nextHour(lastCursusHour.value), locale: locale, prayerType: 'officium'};
    }
  }

  return {
    displayPath: displayPath,
    rite: rite,
    opt: opt,
    navigationType: navigationType,
    now: now,
    updateNow: () => {
      now.value = Temporal.Now.plainDateTimeISO();
    },
    contentParams: contentParams,
    // Null until a rite is on the page (a bare /pray visit before its first rite loads)
    nextHourButton: computed(() => isRitePath(ritePath.value) ? nextHourTarget(riteParams.value, lastCursusHour.value, now.value) : null),
    navigateRite: navigateRite,
    bestHour: bestHour,
    // Leaves a pinned rite for the most relevant one; a new history entry, so Back returns to where the user was
    returnToCurrent: async () => {
      await navigateRite(makePath(bestHour()), 'soft');
    },
    // Changes the navigation type without navigating, recording it in the current history entry so it survives a reload
    setNavigationType: (newNavigationType) => {
      navigationType.value = newNavigationType;
      history.replaceState({...history.state, navigationType: newNavigationType}, '');
    },
    // Redirects a bare /pray visit, or a reload of a page reached by soft navigation, to the most relevant rite
    init: () => {
      const [navEntry] = performance.getEntriesByType('navigation');
      if (!isRitePath(window.location.pathname)) {
        navigateRite(makePath(bestHour()), 'soft', 'replace');
      }
    },
    // Back/forward only re-displays the entry; it must not push a new one
    handlePopstate: async () => {
      if (!isRitePath(window.location.pathname)) {
        await navigateRite(makePath(bestHour()), 'soft', 'replace');
        return;
      }
      let path = window.location.pathname + window.location.search;
      batch(() => {
        navigationType.value = history.state?.navigationType ?? null;
        displayPath.value = path;
      });
      await loadRite(path);
    },
    markHourAsDone: () => {
      let current = riteParams.value;
      if (!isCursus(current)) {
        return;
      }
      let hour = {date: current.date, prayerType: current.prayerType, select: current.select, occasion: current.occasion, votives: current.votives};
      lastCursusHour.value = hour;
      try {
        localStorage.setItem('lastCursusHour', JSON.stringify({...hour, date: hour.date.toString()}));
      } catch {
        // Some browsers throw an Error if localStorage is disabled (who does this?????)
      }
    },
    toggleVotive: async (tag) => {
      let current = contentParams.value;
      let votives = current.votives.includes(tag) ? current.votives.filter(v => v != tag) : [...current.votives, tag];
      await navigateRite(makePath({...current, votives: votives}));
    },
    setDesired: async (select, optTag) => {
      let current = contentParams.value;
      let tags = opt.value.filter(t => t == 'privata');
      if (optTag) tags.push(optTag);
      await setOpt(tags);
      if (current.select != select) {
        await navigateRite(makePath({...current, select: select}));
      } else {
        await loadRite(displayPath.value);
      }
    },
    togglePriest: async () => {
      let tags = opt.value.includes('privata') ? opt.value.filter(t => t != 'privata') : [...opt.value, 'privata'];
      await setOpt(tags);
      await loadRite(displayPath.value);
    }
  }
}

// The next moment canSay's answer can change: midnight, when the date moves on, and 14:00, from which the next day's
// Matins and Lauds may be anticipated
export function nextCanSayChange(now) {
  let today = now.toPlainDate();
  return now.hour < 14 ? today.toPlainDateTime({hour: 14}) : today.add({days: 1}).toPlainDateTime();
}

export function canSay(params, now) {
  if (params.occasion == 'matutinum-laudes' && Temporal.PlainDate.compare(params.date, now.toPlainDate().add({days: 1})) == 0) {
    return now.hour >= 14;
  }
  return Temporal.PlainDate.compare(params.date, now.toPlainDate()) == 0;
}

// The day other rite links lead to. Soft navigation onto Matins and Lauds anticipated the evening before still
// belongs to the current calendar day, so links lead to that day's rites rather than the anticipated day's.
export function riteLinksDate(params, navigationType, now) {
  let today = now.toPlainDate();
  let anticipatedMatins = isCursus(params) && params.occasion == 'matutinum-laudes' && Temporal.PlainDate.compare(params.date, today.add({days: 1})) == 0;
  return navigationType == 'soft' && anticipatedMatins ? today : params.date;
}

export function canIncrementHour(current, now) {
  return canSay(nextHour(current), now);
}

// What the next-hour button offers: the hour after the current one when on a cursus hour, otherwise the hour
// after the last one prayed (today's Matins and Lauds counts as prayed when none has been recorded yet).
export function nextHourTarget(current, lastCursusHour, now) {
  let reference = isCursus(current) ? current : lastCursusHour ?? {...current, prayerType: 'officium', date: now.toPlainDate(), select: 'primarium', occasion: 'matutinum-laudes', votives: []};
  let target = nextHour(reference);
  return {
    // Stored hours carry no locale, and ones recorded before prayerType was stored lack it; the cursus is always the Office
    path: makePath({...target, locale: current.locale, prayerType: 'officium'}),
    occasion: target.occasion,
    allowed: canSay(target, now)
  };
}
