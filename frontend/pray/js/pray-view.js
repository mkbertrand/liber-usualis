// Binds the pray page's server-rendered markup to the pray and display stores.
// Each binding is a signal effect (state -> DOM) and/or an event listener (DOM -> state).

import { effect, computed, untracked, createModel } from '@preact/signals-core';
import { makePath, RITE_TITLES, officeHourPath } from './routing.js';
import { canSay, riteLinksDate } from './pray-store.js';
import { stopChantPlayback } from './gabc-chant.js';
import { setShown, trapFocus, closeOnOutsideClick, positionUnderLeftAligned, labelFor } from './dom-bindings.js';
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

function bindRitesMenu(prayStore, displayStore) {
  let menu = document.getElementById('rites-menu-wrapper');
  let toggleButton = document.getElementById('rites-menu-toggle-button');
  toggleButton.addEventListener('click', displayStore.toggleRitesMenu);
  closeOnOutsideClick(menu, displayStore.ritesMenuOpen, displayStore.closeRitesMenu, toggleButton);
  // Fixed rather than inside the button's group, which scrolls sideways and would clip it; so it is placed under
  // the button on opening and follows it if the window resizes or the group scrolls
  let hoursGroup = document.getElementById('second-bar-center-aligned-container');
  effect(() => {
    let open = displayStore.ritesMenuOpen.value;
    setShown(menu, open);
    if (!open) return;
    let reposition = () => positionUnderLeftAligned(menu, toggleButton);
    reposition();
    window.addEventListener('resize', reposition);
    hoursGroup.addEventListener('scroll', reposition);
    return () => {
      window.removeEventListener('resize', reposition);
      hoursGroup.removeEventListener('scroll', reposition);
    };
  });

  // Every copy of the rite links: in this menu and in the hour picker
  for (let link of document.querySelectorAll('.rite-link')) {
    effect(() => {
      let params = prayStore.contentParams.value;
      link.href = makePath({...params, date: riteLinksDate(params, prayStore.navigationType.value, prayStore.now.value), prayerType: link.dataset.prayerType, select: link.dataset.select, occasion: link.dataset.occasion});
    });
    link.addEventListener('click', displayStore.closeRitesMenu);
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
function bindHourLinks(prayStore) {
  // Every copy: in the second bar and in the hour picker
  for (let link of document.querySelectorAll('.hour-link')) {
    effect(() => {
      let params = prayStore.contentParams.value;
      link.href = officeHourPath(params, riteLinksDate(params, prayStore.navigationType.value, prayStore.now.value), link.dataset.occasion);
    });
  }
  for (let nextMatins of document.querySelectorAll('.next-matins-link')) {
    effect(() => {
      let params = prayStore.contentParams.value;
      let date = riteLinksDate(params, prayStore.navigationType.value, prayStore.now.value).add({days: 1});
      nextMatins.href = officeHourPath(params, date, 'matutinum-laudes');
      nextMatins.title = date.toString();
      setShown(nextMatins, canSay({...params, date: date, occasion: 'matutinum-laudes'}, prayStore.now.value) && prayStore.navigationType.value == 'soft');
    });
  }
}

function bindRite(prayStore, displayStore) {
  let main = document.getElementById('rite-container');
  // Display preferences are shared by every locale, so a translation saved as shown elsewhere is ignored where there is none
  let hasTranslation = main.dataset.hasTranslation == 'true';
  let showTranslation = computed(() => hasTranslation && displayStore.displayParameters.value.showTranslation);
  let lineByLineMode = computed(() => showTranslation.value && !displayStore.displayParameters.value.sideBySide);
  let riteHTML = computed(() => lineByLineMode.value ? lineByLine(prayStore.rite.value) : prayStore.rite.value);

  // Only replace the markup when it actually changes, since doing so re-creates every chant element
  let renderedHTML = main.innerHTML;
  effect(() => {
    let html = riteHTML.value;
    if (html != renderedHTML) {
      main.innerHTML = html;
      renderedHTML = html;
    }
  });

  // The reader's side-by-side split, if they have chosen one, overrides the stylesheet's default
  effect(() => {
    let share = displayStore.displayParameters.value.sideBySideLatinShare;
    if (share == null) {
      document.documentElement.style.removeProperty('--side-by-side-latin-share');
    } else {
      document.documentElement.style.setProperty('--side-by-side-latin-share', share);
    }
  });

  effect(() => {
    let parameters = displayStore.displayParameters.value;
    let translated = showTranslation.value;
    main.classList.toggle('chant-shown', parameters.chant);
    main.classList.toggle('chant-hidden', !parameters.chant);
    main.classList.toggle('chant-playback', parameters.chant && parameters.playChant);
    main.classList.toggle('side-by-side', translated && parameters.sideBySide);
    main.classList.toggle('line-by-line', translated && !parameters.sideBySide);
    main.classList.toggle('no-translation', !translated);
  });
}

function bindNextHour(prayStore) {
  let container = document.getElementById('next-hour-button-container');
  let button = document.getElementById('next-hour-button');
  let occasionName = document.getElementById('next-hour-occasion');
  let forbiddenTitle = button.dataset.forbiddenTitle;

  // Follows the rite on the page, so it changes together with the text above it
  effect(() => {
    let target = prayStore.nextHourButton.value;
    if (!target) return;
    button.href = target.path;
    occasionName.textContent = RITE_TITLES[target.occasion];
    button.classList.toggle('next-hour-button-forbidden', !target.allowed);
    button.title = target.allowed ? '' : forbiddenTitle;
  });
  button.addEventListener('click', (event) => {
    event.preventDefault();
    let target = prayStore.nextHourButton.value;
    if (target?.allowed) {
      prayStore.navigateRite(target.path);
    }
  });

  // Reaching the end of an hour (within 400px of the next-hour button) counts as having prayed it
  new IntersectionObserver((entries) => {
    if (entries.some(entry => entry.isIntersecting)) {
      prayStore.markHourAsDone();
    }
  }, {rootMargin: '0px 0px 400px 0px'}).observe(container);
}

function bindCheckbox(input, isChecked, onChange) {
  effect(() => {
    input.checked = isChecked();
  });
  input.addEventListener('change', () => onChange(input.checked));
}

function bindDisplayParameterCheckbox(displayStore, inputId, key, dependsOn) {
  let input = document.getElementById(inputId);
  // Translation toggles are omitted for Latin
  if (!input) return;
  bindCheckbox(input, () => displayStore.displayParameters.value[key], (checked) => {
    displayStore.setDisplayParameter(key, checked);
    if (!checked && (key == 'chant' || key == 'playChant')) {
      stopChantPlayback();
    }
  });
  if (dependsOn) {
    let label = labelFor(input);
    effect(() => {
      let enabled = displayStore.displayParameters.value[dependsOn];
      input.disabled = !enabled;
      label.classList.toggle('option-disabled', !enabled);
    });
  }
}

// Only meaningful in side-by-side layout, so disabled when the translation is off or shown line by line
function bindSideBySideShareSlider(displayStore) {
  let slider = document.getElementById('side-by-side-latin-share');
  // Translation options are omitted for Latin
  if (!slider) return;
  // Read with no reader's choice applied, so it is the stylesheet's default
  let defaultShare = getComputedStyle(document.documentElement).getPropertyValue('--side-by-side-latin-share').trim();
  // A share saved before the slider's range changed is brought within it, so the layout matches what the slider shows
  let saved = displayStore.displayParameters.value.sideBySideLatinShare;
  if (saved != null) {
    let withinRange = Math.min(Math.max(saved, Number(slider.min)), Number(slider.max));
    if (withinRange != saved) {
      displayStore.setDisplayParameter('sideBySideLatinShare', withinRange);
    }
  }
  effect(() => {
    let parameters = displayStore.displayParameters.value;
    slider.value = parameters.sideBySideLatinShare ?? defaultShare;
    slider.disabled = !(parameters.showTranslation && parameters.sideBySide);
  });
  slider.addEventListener('input', () => displayStore.setDisplayParameter('sideBySideLatinShare', Number(slider.value)));
}

function bindOptionsPanel(prayStore, liturgyStore, displayStore) {
  bindDisplayParameterCheckbox(displayStore, 'translation-toggle', 'showTranslation');
  bindDisplayParameterCheckbox(displayStore, 'side-by-side-toggle', 'sideBySide', 'showTranslation');
  bindDisplayParameterCheckbox(displayStore, 'chant-toggle', 'chant');
  bindDisplayParameterCheckbox(displayStore, 'play-chant-toggle', 'playChant', 'chant');
  bindSideBySideShareSlider(displayStore);

  bindCheckbox(document.getElementById('priest-toggle'), () => !prayStore.opt.value.includes('privata'), () => prayStore.togglePriest());

  for (let radio of document.querySelectorAll('input[name="desired"]')) {
    effect(() => {
      radio.checked = prayStore.contentParams.value.select == radio.dataset.select && prayStore.opt.value.filter(t => t != 'privata').join('+') == radio.dataset.optTag;
    });
    radio.addEventListener('change', () => prayStore.setDesired(radio.dataset.select, radio.dataset.optTag));
  }

  for (let checkbox of document.querySelectorAll('input[data-votive]')) {
    effect(() => {
      checkbox.checked = liturgyStore.votives.value.includes(checkbox.dataset.votive);
    });
    checkbox.addEventListener('change', () => prayStore.toggleVotive(checkbox.dataset.votive));
  }
}

// Links marked data-rite-link navigate within the page instead of reloading it, keeping the current navigation type
// unless the link names one (data-rite-link="hard" keeps the chosen rite on reload; "soft" lets a reload move on to
// a more relevant rite).
// Pointing at (or focusing) a rite link or the next-hour button starts fetching its rite, so it's ready on click
function bindRitePrefetch(prayStore) {
  let prefetch = (event) => {
    let link = event.target.closest?.('a[data-rite-link], #next-hour-button');
    if (link?.href) {
      let url = new URL(link.href);
      prayStore.prefetchRite(url.pathname + url.search);
    }
  };
  document.addEventListener('pointerover', prefetch);
  document.addEventListener('focusin', prefetch);
}

function bindRiteLinks(prayStore) {
  document.addEventListener('click', (event) => {
    let link = event.target.closest('a[data-rite-link]');
    // Leave modified clicks (new tab/window) to the browser
    if (!link || event.button != 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    let url = new URL(link.href);
    prayStore.navigateRite(url.pathname + url.search, link.dataset.riteLink || null);
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
function bindOrdo(prayStore, displayStore) {
  effect(() => {
    if (!displayStore.ordoPanelOpen.value) return;
    // Untracked, so the page changing while the panel is open doesn't restart the session
    let session = untracked(() => new OrdoPanelSession(prayStore.contentParams.value));
    return () => session[Symbol.dispose]();
  });
  for (let link of document.querySelectorAll('.ordo-rite-link')) {
    link.addEventListener('click', displayStore.closeOrdoPanel);
  }
}

export function bindPrayPage(prayStore, liturgyStore, displayStore) {
  bindOverlayPanel(document.getElementById('options-panel-background'), document.getElementById('options-panel-wrapper'), document.getElementById('options-gear-button'), displayStore.optionsPanelOpen, displayStore.toggleOptionsPanel, displayStore.closeOptionsPanel);
  bindOverlayPanel(document.getElementById('ordo-panel-background'), document.getElementById('ordo-panel-wrapper'), document.getElementById('ordo-panel-toggle-button'), displayStore.ordoPanelOpen, displayStore.toggleOrdoPanel, displayStore.closeOrdoPanel);
  bindRitesMenu(prayStore, displayStore);
  bindRite(prayStore, displayStore);
  bindNextHour(prayStore);
  bindHourLinks(prayStore);
  bindOptionsPanel(prayStore, liturgyStore, displayStore);
  bindRiteLinks(prayStore);
  bindRitePrefetch(prayStore);
  bindOrdo(prayStore, displayStore);
  bindBanners(prayStore);
  bindReturnToCurrent(prayStore);
  bindHourPicker(prayStore, displayStore);
  window.addEventListener('popstate', () => prayStore.handlePopstate());
}

const bannerContainer = document.querySelector('#system-banner-container');
const bannerTemplate = document.querySelector('#system-banner');
const bannerAnswerTemplate = document.querySelector('#system-banner-answer');
// Offered while the user has pinned (hard navigation) a rite other than the one that would be chosen for them now
function bindReturnToCurrent(prayStore) {
  // Every copy: in the second bar and in the hour picker
  for (let button of document.querySelectorAll('.return-to-current-button')) {
    // Localized tooltip with a {date} placeholder
    let titleTemplate = button.dataset.titleTemplate;
    effect(() => {
      let params = prayStore.contentParams.value;
      // bestHour() reads the clock and the last prayed hour, so this reruns when either changes
      let current = prayStore.bestHour();
      let onCurrent = current.occasion == params.occasion && Temporal.PlainDate.compare(current.date, params.date) == 0;
      setShown(button, prayStore.navigationType.value == 'hard' && !onCurrent);
      button.title = titleTemplate.replace('{date}', params.date.toString());
    });
    button.addEventListener('click', prayStore.returnToCurrent);
  }
}

// The bottom bar's hour picker: a sheet of the day's hours and the other rites, used instead of the second bar's
// row of hours on narrow screens
function bindHourPicker(prayStore, displayStore) {
  let button = document.getElementById('hour-picker-button');
  let sheet = document.getElementById('hour-picker');
  let current = document.getElementById('hour-picker-current');
  button.addEventListener('click', displayStore.toggleHourPicker);
  closeOnOutsideClick(sheet, displayStore.hourPickerOpen, displayStore.closeHourPicker, button);
  // Choosing anything in the sheet (an hour, a rite, returning to the current hour) closes it
  sheet.addEventListener('click', (event) => {
    if (event.target.closest('a, button')) {
      displayStore.closeHourPicker();
    }
  });
  effect(() => {
    let open = displayStore.hourPickerOpen.value;
    setShown(sheet, open);
    button.setAttribute('aria-expanded', open);
  });
  effect(() => {
    let occasion = prayStore.contentParams.value.occasion;
    current.textContent = RITE_TITLES[occasion] ?? occasion;
  });
}

// Banners belong to the rite they were shown for, so navigating to another rite removes them all
function bindBanners(prayStore) {
  let bannerPath = prayStore.displayPath.peek();
  effect(() => {
    let path = prayStore.displayPath.value;
    if (path == bannerPath) return;
    bannerPath = path;
    for (let banner of bannerContainer.querySelectorAll('.system-banner')) {
      banner.remove();
    }
  });
}

export function makeBanner(prayStore, bannerID, bannerContent, answers) {
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
    bannerButton.classList.add(answer.role == 'primary' ? 'ui-button-primary' : 'ui-button-secondary');
    answerContainer.appendChild(bannerButtonClone);
    bannerButton.addEventListener('click', async () => { document.getElementById(bannerID).remove(); await answer.action(); });
  }
  bannerContainer.appendChild(bannerClone);
}
