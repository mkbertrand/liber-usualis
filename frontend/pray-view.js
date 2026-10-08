// Binds the pray page's server-rendered markup to the pray and display stores.
// Each binding is a signal effect (state -> DOM) and/or an event listener (DOM -> state).

import { effect, computed, untracked, createModel } from '@preact/signals-core';
import { makePath, RITE_TITLES, officeHourPath } from './routing.js';
import { canSay, riteLinksDate } from './pray-store.js';
import { stopChantPlayback } from './gabc-chant.js';
import { setShown, trapFocus, closeOnOutsideClick, positionUnderRightAligned, labelFor } from './dom-bindings.js';
import { OrdoModel, ordoSummary, ordoRitePath } from './pray-ordo.js';

// A panel shown over an overlay. Wrappers marked data-trap-focus (desktop only) trap focus and lock page scroll.
function bindOverlayPanel(background, wrapper, toggleButton, isOpen, toggle, close) {
  toggleButton.addEventListener('click', toggle);
  closeOnOutsideClick(wrapper, isOpen, close, toggleButton);
  let trapsFocus = wrapper.hasAttribute('data-trap-focus');
  effect(() => {
    let open = isOpen.value;
    setShown(background, open);
    if (open && trapsFocus) {
      return trapFocus(wrapper);
    }
  });
}

function bindRitesMenu(store, display) {
  let menu = document.getElementById('rites-menu-wrapper');
  let toggleButton = document.getElementById('rites-menu-toggle-button');
  toggleButton.addEventListener('click', display.toggleRitesMenu);
  closeOnOutsideClick(menu, display.ritesMenuOpen, display.closeRitesMenu, toggleButton);
  // Fixed rather than inside the button's group, which scrolls sideways and would clip it; so it is placed under
  // the button on opening and follows it if the window resizes or the group scrolls
  let hoursGroup = document.getElementById('second-bar-center-aligned-container');
  effect(() => {
    let open = display.ritesMenuOpen.value;
    setShown(menu, open);
    if (!open) return;
    let reposition = () => positionUnderRightAligned(menu, toggleButton);
    reposition();
    window.addEventListener('resize', reposition);
    hoursGroup.addEventListener('scroll', reposition);
    return () => {
      window.removeEventListener('resize', reposition);
      hoursGroup.removeEventListener('scroll', reposition);
    };
  });

  for (let link of menu.querySelectorAll('.rite-link')) {
    effect(() => {
      let params = store.contentParams.value;
      link.href = makePath({...params, date: riteLinksDate(params, store.navigationType.value, store.now.value), prayerType: link.dataset.prayerType, select: link.dataset.select, occasion: link.dataset.occasion});
    });
    link.addEventListener('click', display.closeRitesMenu);
  }
}

// Modifies actual HTMl to alternate between Latin and English lines. A single HTML fragment can't represent both the side-by-side and line-by-line displays without breaking initial lettering (believe me, I tried)
function lineByLine(rite) {
  let riteSplit = rite.split(/(<div class="rite-text-container.+?>.+?<\/div>)/);
  let riteRet = [];
  for (let i = 0; i < riteSplit.length; i++) {
    if (i % 2 == 0) {
      riteRet.push(riteSplit[i]);
    } else {
      let style = riteSplit[i].match(/"rite-text-container (.*?)"/)[1];
      let latinColumn = riteSplit[i].match(/<p class="rite-text rite-text-latin.+?>(.*?)<\/p>/)[1];
      let transColumn = riteSplit[i].match(/<p class="rite-text rite-text-translation.+?>(.*?)<\/p>/)[1];
      let latinColumnLines = latinColumn.split('<br>');
      let transColumnLines = transColumn.split('<br>');
      let para = `<div class="rite-text-container ${style}"><p class="rite-text">`;
      for (let j = 0; j < latinColumnLines.length; j++) {
        para += latinColumnLines[j];
        if (transColumnLines[j]) {
          para += `<br><span class="rite-text-translation">${transColumnLines[j]}</span>`;
        }
        if (j != latinColumnLines.length - 1) {
          para += '<br>';
        }
      }
      para += '</p></div>';
      riteRet.push(para);
    }
  }
  return riteRet.join('');
}

// The hours of the day given by riteLinksDate, plus the next day's Matins once it may be said
function bindHourLinks(store) {
  for (let link of document.querySelectorAll('.second-bar-hour-link')) {
    effect(() => {
      let params = store.contentParams.value;
      link.href = officeHourPath(params, riteLinksDate(params, store.navigationType.value, store.now.value), link.dataset.occasion);
    });
  }
  let nextMatins = document.getElementById('second-bar-next-matins-link');
  effect(() => {
    let params = store.contentParams.value;
    let date = riteLinksDate(params, store.navigationType.value, store.now.value).add({days: 1});
    nextMatins.href = officeHourPath(params, date, 'matutinum-laudes');
    nextMatins.title = date.toString();
    setShown(nextMatins, canSay({...params, date: date, occasion: 'matutinum-laudes'}, store.now.value));
  });
}

function bindRite(store, display) {
  let main = document.getElementById('rite-container');
  // Display preferences are shared by every locale, so a translation saved as shown elsewhere is ignored where there is none
  let hasTranslation = main.dataset.hasTranslation == 'true';
  let showTranslation = computed(() => hasTranslation && display.displayParameters.value.showTranslation);
  let lineByLineMode = computed(() => showTranslation.value && !display.displayParameters.value.sideBySide);
  let riteHTML = computed(() => lineByLineMode.value ? lineByLine(store.rite.value) : store.rite.value);

  // Only replace the markup when it actually changes, since doing so re-creates every chant element
  let renderedHTML = main.innerHTML;
  effect(() => {
    let html = riteHTML.value;
    if (html != renderedHTML) {
      main.innerHTML = html;
      renderedHTML = html;
    }
  });

  effect(() => {
    let parameters = display.displayParameters.value;
    let translated = showTranslation.value;
    main.classList.toggle('chant-shown', parameters.chant);
    main.classList.toggle('chant-hidden', !parameters.chant);
    main.classList.toggle('chant-playback', parameters.chant && parameters.playChant);
    main.classList.toggle('side-by-side', translated && parameters.sideBySide);
    main.classList.toggle('line-by-line', translated && !parameters.sideBySide);
    main.classList.toggle('no-translation', !translated);
  });
}

function bindNextHour(store) {
  let container = document.getElementById('next-hour-button-container');
  let button = document.getElementById('next-hour-button');
  let occasionName = document.getElementById('next-hour-occasion');
  let forbiddenTitle = button.dataset.forbiddenTitle;

  effect(() => {
    let target = store.nextHourButton.value;
    button.href = target.path;
    occasionName.textContent = RITE_TITLES[target.occasion];
    button.classList.toggle('next-hour-button-forbidden', !target.allowed);
    button.title = target.allowed ? '' : forbiddenTitle;
  });
  button.addEventListener('click', (event) => {
    event.preventDefault();
    let target = store.nextHourButton.value;
    if (target.allowed) {
      store.navigateRite(target.path);
    }
  });

  // Reaching the end of an hour (within 400px of the next-hour button) counts as having prayed it
  new IntersectionObserver((entries) => {
    if (entries.some(entry => entry.isIntersecting)) {
      store.markHourAsDone();
    }
  }, {rootMargin: '0px 0px 400px 0px'}).observe(container);
}

function bindCheckbox(input, isChecked, onChange) {
  effect(() => {
    input.checked = isChecked();
  });
  input.addEventListener('change', () => onChange(input.checked));
}

function bindDisplayParameterCheckbox(display, inputId, key, dependsOn) {
  let input = document.getElementById(inputId);
  // Translation toggles are omitted for Latin
  if (!input) return;
  bindCheckbox(input, () => display.displayParameters.value[key], (checked) => {
    display.setDisplayParameter(key, checked);
    if (!checked && (key == 'chant' || key == 'playChant')) {
      stopChantPlayback();
    }
  });
  if (dependsOn) {
    let label = labelFor(input);
    effect(() => {
      let enabled = display.displayParameters.value[dependsOn];
      input.disabled = !enabled;
      label.classList.toggle('option-disabled', !enabled);
    });
  }
}

function bindOptionsPanel(store, display) {
  bindDisplayParameterCheckbox(display, 'translation-toggle', 'showTranslation');
  bindDisplayParameterCheckbox(display, 'side-by-side-toggle', 'sideBySide', 'showTranslation');
  bindDisplayParameterCheckbox(display, 'chant-toggle', 'chant');
  bindDisplayParameterCheckbox(display, 'play-chant-toggle', 'playChant', 'chant');

  bindCheckbox(document.getElementById('priest-toggle'), () => !store.opt.value.includes('privata'), () => store.togglePriest());

  for (let radio of document.querySelectorAll('input[name="desired"]')) {
    effect(() => {
      radio.checked = store.contentParams.value.select == radio.dataset.select && store.opt.value.filter(t => t != 'privata').join('+') == radio.dataset.optTag;
    });
    radio.addEventListener('change', () => store.setDesired(radio.dataset.select, radio.dataset.optTag));
  }

  for (let checkbox of document.querySelectorAll('input[data-votive]')) {
    effect(() => {
      checkbox.checked = store.contentParams.value.votives.includes(checkbox.dataset.votive);
    });
    checkbox.addEventListener('change', () => store.toggleVotive(checkbox.dataset.votive));
  }
}

// Links marked data-rite-link navigate within the page instead of reloading it, keeping the current navigation type
// unless the link names one (data-rite-link="hard" keeps the chosen rite on reload; "soft" lets a reload move on to
// a more relevant rite).
function bindRiteLinks(store) {
  document.addEventListener('click', (event) => {
    let link = event.target.closest('a[data-rite-link]');
    // Leave modified clicks (new tab/window) to the browser
    if (!link || event.button != 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    let url = new URL(link.href);
    store.navigateRite(url.pathname + url.search, link.dataset.riteLink || null);
  });
}

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

// The ordo panel's bindings for one browsing session. Created when the panel opens; disposing it disposes every
// effect created here, including the OrdoModel's.
const OrdoPanelSession = createModel((pageParams) => {
  const ordo = new OrdoModel(pageParams);
  // Event listeners aren't effects, so they are removed through this when the session is disposed
  const listeners = new AbortController();
  effect(() => () => listeners.abort());

  let datePicker = document.getElementById('ordo-date-picker');
  effect(() => {
    datePicker.value = ordo.date.value.toString();
  });
  // Clearing the picker leaves its value empty; keep the current date until a full date is chosen
  datePicker.addEventListener('change', () => {
    if (datePicker.value) {
      ordo.setDate(Temporal.PlainDate.from(datePicker.value));
    }
  }, {signal: listeners.signal});
  document.getElementById('ordo-date-previous').addEventListener('click', () => ordo.setDate(ordo.date.value.subtract({days: 1})), {signal: listeners.signal});
  document.getElementById('ordo-date-next').addEventListener('click', () => ordo.setDate(ordo.date.value.add({days: 1})), {signal: listeners.signal});

  bindOrdoTime(ordo.daytime, 'ordo-daytime');
  bindOrdoTime(ordo.evening, 'ordo-evening');

  for (let link of document.querySelectorAll('.ordo-rite-link')) {
    effect(() => {
      link.href = ordoRitePath(ordo.date.value, ordo.votives.value, pageParams, link.dataset.occasion);
    });
  }
  return {};
});

// Browsing in the panel changes only its session; the page changes only when one of its rite links is followed
function bindOrdo(store, display) {
  effect(() => {
    if (!display.ordoPanelOpen.value) return;
    // Untracked, so the page changing while the panel is open doesn't restart the session
    let session = untracked(() => new OrdoPanelSession(store.contentParams.value));
    return () => session[Symbol.dispose]();
  });
  for (let link of document.querySelectorAll('.ordo-rite-link')) {
    link.addEventListener('click', display.closeOrdoPanel);
  }
}

export function bindPrayPage(store, display) {
  bindOverlayPanel(document.getElementById('options-panel-background'), document.getElementById('options-panel-wrapper'), document.getElementById('options-gear-button'), display.optionsPanelOpen, display.toggleOptionsPanel, display.closeOptionsPanel);
  bindOverlayPanel(document.getElementById('ordo-panel-background'), document.getElementById('ordo-panel-wrapper'), document.getElementById('ordo-panel-toggle-button'), display.ordoPanelOpen, display.toggleOrdoPanel, display.closeOrdoPanel);
  bindRitesMenu(store, display);
  bindRite(store, display);
  bindNextHour(store);
  bindHourLinks(store);
  bindOptionsPanel(store, display);
  bindRiteLinks(store);
  bindOrdo(store, display);
  bindBanners(store);
  bindReturnToCurrent(store);
  window.addEventListener('popstate', () => store.handlePopstate());
}

const bannerContainer = document.querySelector('#system-banner-container');
const bannerTemplate = document.querySelector('#system-banner');
const bannerAnswerTemplate = document.querySelector('#system-banner-answer');
// Offered while the user has pinned (hard navigation) a rite other than the one that would be chosen for them now
function bindReturnToCurrent(store) {
  let button = document.getElementById('return-to-current-button');
  // Localized tooltip with a {date} placeholder
  let titleTemplate = button.dataset.titleTemplate;
  effect(() => {
    let params = store.contentParams.value;
    // bestHour() reads the clock and the last prayed hour, so this reruns when either changes
    let current = store.bestHour();
    let onCurrent = current.occasion == params.occasion && Temporal.PlainDate.compare(current.date, params.date) == 0;
    setShown(button, store.navigationType.value == 'hard' && !onCurrent);
    button.title = titleTemplate.replace('{date}', params.date.toString());
  });
  button.addEventListener('click', store.returnToCurrent);
}

// Banners belong to the rite they were shown for, so navigating to another rite removes them all
function bindBanners(store) {
  let bannerPath = store.displayPath.peek();
  effect(() => {
    let path = store.displayPath.value;
    if (path == bannerPath) return;
    bannerPath = path;
    for (let banner of bannerContainer.querySelectorAll('.system-banner')) {
      banner.remove();
    }
  });
}

export function makeBanner(store, bannerID, bannerContent, answers) {
  const bannerClone = document.importNode(bannerTemplate.content, true);
  let banner = bannerClone.querySelector('.system-banner');
  banner.id = bannerID;
  let content = bannerClone.querySelector('.system-banner-content');
  content.textContent = bannerContent;
  let answerContainer = bannerClone.querySelector('.system-banner-answer-container');
  for (let answer of answers) {
    const bannerButtonClone = document.importNode(bannerAnswerTemplate.content, true);
    let bannerButton = bannerButtonClone.querySelector('button');
    bannerButton.textContent = answer.content;
    bannerButton.id = answer.id;
    answerContainer.appendChild(bannerButtonClone);
    bannerButton.addEventListener('click', async () => { document.getElementById(bannerID).remove(); await answer.action(); });
  }
  let bannerCloseButton = bannerClone.querySelector('.system-banner-close');
  bannerCloseButton.addEventListener('click', () => { document.getElementById(bannerID).remove(); });

  bannerContainer.appendChild(bannerClone);
}
