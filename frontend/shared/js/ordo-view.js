// Binds the ordo's markup (date controls, the daytime and evening offices, and links to the day's hours) to an
// OrdoModel. Shared by the pray page's ordo panel and the ordo page, which use the same element ids.

import { effect } from '@preact/signals-core';
import { ordoSummary, ordoRitePath } from './ordo-model.js';

// A paragraph of the ordo cloned from its <template>, listing names one per line
function ordoSection(templateId, names) {
  let section = document.getElementById(templateId).content.firstElementChild.cloneNode(true);
  section.querySelector('.ordo-section-names').replaceChildren(...names.flatMap((name, index) => index == 0 ? [name] : [document.createElement('br'), name]));
  return section;
}

function bindOrdoTime(response, idPrefix) {
  let primarium = document.getElementById(`${idPrefix}-primarium`);
  let rank = document.getElementById(`${idPrefix}-primarium-rank`);
  let details = document.getElementById(`${idPrefix}-details`);
  effect(() => {
    let summary = response.value ? ordoSummary(response.value) : {primarium: '', rank: '', commemorations: [], omissions: [], psalmi: null};
    primarium.textContent = summary.primarium;
    rank.textContent = summary.rank;
    // Only the paragraphs that have something to say
    details.replaceChildren(...[
      summary.psalmi && ordoSection('ordo-psalmi-template', [summary.psalmi]),
      summary.commemorations.length > 0 && ordoSection('ordo-commemorations-template', summary.commemorations),
      summary.omissions.length > 0 && ordoSection('ordo-omissions-template', summary.omissions)
    ].filter(section => section));
  });
}

// pageParams supplies the locale and select of the hour links. Event listeners are removed when listenerSignal
// aborts; the effects are disposed with whatever model or effect scope this is called within.
export function bindOrdo(ordo, pageParams, listenerSignal) {
  let datePicker = document.getElementById('ordo-date-picker');
  effect(() => {
    datePicker.value = ordo.date.value.toString();
  });
  // Clearing the picker leaves its value empty; keep the current date until a full date is chosen
  datePicker.addEventListener('change', () => {
    if (datePicker.value) {
      ordo.setDate(Temporal.PlainDate.from(datePicker.value));
    }
  }, {signal: listenerSignal});
  document.getElementById('ordo-date-previous').addEventListener('click', () => ordo.setDate(ordo.date.value.subtract({days: 1})), {signal: listenerSignal});
  document.getElementById('ordo-date-next').addEventListener('click', () => ordo.setDate(ordo.date.value.add({days: 1})), {signal: listenerSignal});

  bindOrdoTime(ordo.daytime, 'ordo-daytime');
  bindOrdoTime(ordo.evening, 'ordo-evening');

  for (let link of document.querySelectorAll('.ordo-rite-link')) {
    effect(() => {
      link.href = ordoRitePath(ordo.date.value, ordo.votives.value, pageParams, link.dataset.occasion);
    });
  }
}
