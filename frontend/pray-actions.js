import { setOpt, loadRite, navigateRite } from './pray-store.js';
import { contentParameters, makePath, nextHour, isCursus } from './routing.js';

export async function toggleVotive(prayState, tag) {
  let current = contentParameters(prayState.displayPath);
  let votives = current.votives.includes(tag) ? current.votives.filter(v => v != tag) : [...current.votives, tag];
  await navigateRite(prayState, makePath({...current, votives: votives}));
}

export async function setDesired(prayState, select, optTag) {
  let current = contentParameters(prayState.displayPath);
  let tags = prayState.opt.filter(t => t == 'privata');
  if (optTag) tags.push(optTag);
  await setOpt(prayState, tags);
  if (current.select != select) {
    await navigateRite(prayState, makePath({...current, select: select}));
  } else {
    await loadRite(prayState, prayState.displayPath);
  }
}

export async function togglePriest(prayState) {
  let current = contentParameters(prayState.displayPath);
  let tags = prayState.opt.includes('privata') ? prayState.opt.filter(t => t != 'privata') : [...prayState.opt, 'privata'];
  await setOpt(prayState, tags);
  await loadRite(prayState, prayState.displayPath);
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

export function markAsDone(prayState) {
  let current = Pray.contentParameters(prayState.displayPath);
  if (!isCursus(current)) {
    return;
  }

  let lastCursusHour = {
    date: current.date.toString(), prayerType: current.prayerType, select: current.select,
    occasion: current.occasion, votives: current.votives
  };
  localStorage.setItem('lastCursusHour', JSON.stringify(lastCursusHour));
}
