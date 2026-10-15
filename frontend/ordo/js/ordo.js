// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import { effect } from '@preact/signals-core';
import { makeLiturgyStore } from '../../shared/js/liturgy-store.js';
import { OrdoModel } from '../../shared/js/ordo-model.js';
import { bindOrdo } from '../../shared/js/ordo-view.js';

// The ?date= of the address, so a browsed day can be reloaded or shared; today when absent or invalid
function initialDate() {
  let date = new URLSearchParams(window.location.search).get('date');
  try {
    return date ? Temporal.PlainDate.from(date) : Temporal.Now.plainDateISO();
  } catch {
    return Temporal.Now.plainDateISO();
  }
}

// Runs once the document is parsed (the bundle is loaded with defer)
const liturgyStore = makeLiturgyStore();
const locale = window.location.pathname.match(/^\/([a-z]{2})\//)?.[1] || 'en';
// The page offers no votive options of its own: it shows the ordo, and links to the hours, with the reader's
// preferred votives
const ordo = new OrdoModel({date: initialDate(), votives: liturgyStore.votives.value});
bindOrdo(ordo, {locale: locale, select: 'primarium'});

// Today is left out of the address, so a bare /ordo always opens on the current day
effect(() => {
  let date = ordo.date.value;
  let url = new URL(window.location.href);
  if (date.equals(Temporal.Now.plainDateISO())) {
    url.searchParams.delete('date');
  } else {
    url.searchParams.set('date', date.toString());
  }
  history.replaceState(history.state, '', url);
});
