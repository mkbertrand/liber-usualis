// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import { initChantElement } from './gabc-chant.js';
import { makePrayStore, canSay } from './pray-store.js';
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
// Keeps time-dependent state (whether the next hour may be said yet) current while the page stays open
setInterval(() => {
  store.now.value = Temporal.Now.plainDateTimeISO();
}, 60 * 1000);

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
        {id: 'suboptimal-liturgical-content-banner-yes', content: text['suboptimal-content-banner-go'], action: async () => { await store.returnToCurrent(); }},
        {id: 'suboptimal-liturgical-content-banner-no', content: text['banner-remain-here'], action: () => {}}
      ]
    );
  } else if (!canSay(store.contentParams.value, store.now.value)) {
    makeBanner(
      store,
      'outdated-liturgical-content-banner',
      text['outdated-content-banner-message'],
      [
        {id: 'outdated-liturgical-content-banner-yes', content: text['outdated-content-banner-go'], action: async () => { await store.returnToCurrent(); }},
        {id: 'outdated-liturgical-content-banner-no', content: text['banner-remain-here'], action: () => { store.setNavigationType('hard'); }}
      ]
    );
  }
}
