import { signal, effect, batch, createModel } from '@preact/signals-core';
import { officeHourPath } from './routing.js';

// /api/ordo responses for one set of votives, by date and time. Kept across ordo panel sessions; any change of votives
// discards them all. Holds the pending promise, so simultaneous requests for a day share one fetch.
let ordoCache = new Map();
let ordoCacheVotives = null;

export function ordo(date, time, votives) {
  let votivesKey = votives.join('+');
  if (votivesKey != ordoCacheVotives) {
    ordoCache = new Map();
    ordoCacheVotives = votivesKey;
  }
  let cache = ordoCache;
  let key = `${date}|${time}`;
  if (!cache.has(key)) {
    // A failed request isn't kept, so the day can be fetched again
    cache.set(key, fetch(`/api/ordo?date=${date}&time=${time}&votives=${votivesKey}`).then(response => response.json()).catch(error => {
      cache.delete(key);
      throw error;
    }));
  }
  return cache.get(key);
}

// Most specific first, since a feast carries both its class and the broader rank (e.g. duplex and duplex-i-classis)
const RANK_NAMES = [
  ['duplex-i-classis', 'Duplex I. classis'],
  ['duplex-ii-classis', 'Duplex II. classis'],
  ['dominica-i-classis', 'Dominica I. classis'],
  ['dominica-ii-classis', 'Dominica II. classis'],
  ['duplex-majus', 'Duplex majus'],
  ['duplex-minus', 'Duplex minus'],
  ['duplex', 'Duplex'],
  ['semiduplex', 'Semiduplex'],
  ['simplex', 'Simplex'],
  ['feria-major', 'Feria major'],
  ['feria', 'Feria']
];

export function rankName(tags) {
  return RANK_NAMES.find(([tag]) => tags.includes(tag))?.[1] ?? '';
}

export function ordoSummary(response) {
  return {
    primarium: response.primary[0],
    rank: rankName(response.primary[1]),
    commemorations: response.commemorations.filter(([, tags]) => !tags.includes('suffragium')).map(([name]) => name)
  };
}

// An hour of the office for the browsed date and votives, with the page's locale and Little Office select
export function ordoRitePath(date, votives, pageParams, occasion) {
  return officeHourPath({...pageParams, votives: votives}, date, occasion);
}

// One browsing session of the ordo, created from the page's rite when the panel opens and disposed when it closes
export const OrdoModel = createModel((initialParams) => {
  const date = signal(initialParams.date);
  const votives = signal(initialParams.votives);
  // Raw /api/ordo responses for the date's diurnal and vesperal offices, null until loaded
  const daytime = signal(null);
  const evening = signal(null);
  // Date and votives of the latest request, so a slower earlier response can't overwrite it
  let requestedKey = null;

  // Fetches whenever the browsed date or votives change
  effect(() => {
    let currentDate = date.value;
    let currentVotives = votives.value;
    let key = `${currentDate}|${currentVotives.join('+')}`;
    if (key == requestedKey) return;
    requestedKey = key;
    Promise.all([ordo(currentDate, 'diurnale', currentVotives), ordo(currentDate, 'vesperale', currentVotives)]).then(([daytimeResponse, eveningResponse]) => {
      if (key != requestedKey) return;
      batch(() => {
        daytime.value = daytimeResponse;
        evening.value = eveningResponse;
      });
    });
  });

  return {
    date: date,
    votives: votives,
    daytime: daytime,
    evening: evening,
    // The only writer of the browsed date, whether it comes from the day arrows or the calendar picker
    setDate: (newDate) => {
      date.value = newDate;
    }
  };
});
