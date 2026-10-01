// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import { initChantElement } from './gabc-chant.js';
import { makePrayStore } from './pray-store.js';
import { makeDisplayStore, persistDisplayStore } from './pray-display.js';
import { bindPrayPage } from './pray-view.js';

initChantElement();

// Runs once the document is parsed (the bundle is loaded with defer)
const store = makePrayStore();
const display = makeDisplayStore();
persistDisplayStore(display);
// Before binding, so that every binding's first run already sees a rite path
store.init();
bindPrayPage(store, display);
// Keeps time-dependent state (whether the next hour may be said yet) current while the page stays open
setInterval(() => {
  store.now.value = Temporal.Now.plainDateTimeISO();
}, 60 * 1000);
