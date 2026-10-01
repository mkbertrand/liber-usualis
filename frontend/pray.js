// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import * as Exsurge from 'exsurge';
import { initChantElement, stopChantPlayback } from './gabc-chant.js';
export { stopChantPlayback };
initChantElement();

export function abbreviateName(name) {
	name = name.replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.') + '.';
	name = name.replaceAll(/\.\.$/g, '.');
	return name;
}

import { makePrayStore } from './pray-store.js';
import { makeDisplayStore, persistDisplayStore } from './pray-display.js';
import { bindPrayPage } from './pray-view.js';
export { lineByLine } from './rite-markup.js';

// Runs once the document is parsed (the bundle is loaded with defer)
const store = makePrayStore();
const display = makeDisplayStore();
persistDisplayStore(display);
bindPrayPage(store, display);
// Keeps time-dependent state (whether the next hour may be said yet) current while the page stays open
setInterval(() => {
  store.now.value = Temporal.Now.plainDateTimeISO();
}, 60 * 1000);
store.init();
