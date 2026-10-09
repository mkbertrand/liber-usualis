// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import { effect } from '@preact/signals-core';
import { initChantElement } from './gabc-chant.js';
import { makePrayStore, canSay, nextCanSayChange } from './pray-store.js';
import { makeDisplayStore } from './pray-display.js';
import { bindPrayPage, makeBanner } from './pray-view.js';

initChantElement();

// Runs once the document is parsed (the bundle is loaded with defer)
const store = makePrayStore();
const display = makeDisplayStore();
display.persist();
// Before binding, so that every binding's first run already sees a rite path
store.init();
bindPrayPage(store, display);
// Soft navigation promises current content, so the clock is advanced exactly when what may be said can change. Hard
// navigation makes no such promise, so nothing is scheduled. Rescheduled each time the clock moves.
effect(() => {
  if (store.navigationType.value != 'soft') return;
  let timeout = setTimeout(store.updateNow, store.now.value.until(nextCanSayChange(store.now.value)).total('milliseconds'));
  return () => clearTimeout(timeout);
});
// Timers in a hidden tab can be delayed, so the clock is caught up whenever the page is shown again
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState == 'visible') {
    store.updateNow();
  }
});

// Localized text for the messages built here, written into the page by pray.tpl
const text = JSON.parse(document.getElementById('pray-script-text').textContent);

// If hard navigation is specified as hard already, this is because this navigation really comes from the user's history rather than a link (where navigationType would be null)
if (store.navigationType.value != 'hard') {
  if (canSay(store.contentParams.value, store.now.value) && (store.bestHour().occasion != store.contentParams.value.occasion || !store.bestHour().date.equals(store.contentParams.value.date))) {
    makeBanner(
      store,
      'suboptimal-liturgical-content-banner',
      text['suboptimal-content-banner-message'],
      [
        {id: 'suboptimal-liturgical-content-banner-yes', content: text['suboptimal-content-banner-go'], action: async () => { await store.returnToCurrent(); }, role: 'primary'},
        {id: 'suboptimal-liturgical-content-banner-no', content: text['banner-remain-here'], action: () => {}, role: 'secondary'}
      ]
    );
  } else if (!canSay(store.contentParams.value, store.now.value)) {
    showOutdatedBanner();
  }
}

function showOutdatedBanner() {
  makeBanner(
    store,
    'outdated-liturgical-content-banner',
    text['outdated-content-banner-message'],
    [
      {id: 'outdated-liturgical-content-banner-yes', content: text['outdated-content-banner-go'], action: async () => { await store.returnToCurrent(); }, role: 'primary'},
      {id: 'outdated-liturgical-content-banner-no', content: text['banner-remain-here'], action: () => { store.setNavigationType('hard'); }, role: 'secondary'}
    ]
  );
}

// In soft navigation, a rite that stops being sayable while it is shown gets the same banner as one that already was
let previous = null;
effect(() => {
  let path = store.displayPath.value;
  let sayable = canSay(store.contentParams.value, store.now.value);
  let becameOutdated = previous != null && previous.path == path && previous.sayable && !sayable;
  previous = {path: path, sayable: sayable};
  if (becameOutdated && store.navigationType.value == 'soft') {
    showOutdatedBanner();
  }
});
