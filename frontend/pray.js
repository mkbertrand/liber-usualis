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

if (!canSay(store.contentParams.value, store.now.value)) {
  makeBanner(
    store,
    'outdated-liturgical-content-banner',
    'The following liturgical content cannot be said! Would you like to view current liturgical content, or remain here?',
    [
      {id: 'outdated-liturgical-content-banner-yes', content: 'See current content.', action: async () => { await store.redirect(); }},
      {id: 'outdated-liturgical-content-banner-no', content: 'Remain here.', action: () => {}}
    ]
  );
}
