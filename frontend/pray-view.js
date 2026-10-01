// Binds the pray page's server-rendered markup to the pray and display stores.
// Each binding is a signal effect (state -> DOM) and/or an event listener (DOM -> state).

import { effect, computed } from '@preact/signals-core';
import { makePath, RITE_TITLES, shiftDatePath, cursusHourPath, isCurrentCursusHour } from './routing.js';
import { setDisplayParameter } from './pray-display.js';
import { lineByLine } from './rite-markup.js';
import { stopChantPlayback } from './gabc-chant.js';
import { setShown, trapFocus, closeOnOutsideClick, toggleOnClick, labelFor } from './dom-bindings.js';

// A panel shown over an overlay. Wrappers marked data-trap-focus (desktop only) trap focus and lock page scroll.
function bindOverlayPanel(background, wrapper, isOpen, toggleButton) {
  toggleOnClick(toggleButton, isOpen);
  closeOnOutsideClick(wrapper, isOpen, toggleButton);
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
  toggleOnClick(toggleButton, display.ritesMenuOpen);
  closeOnOutsideClick(menu, display.ritesMenuOpen, toggleButton);
  effect(() => setShown(menu, display.ritesMenuOpen.value));

  for (let link of menu.querySelectorAll('.rite-link')) {
    effect(() => {
      if (!store.onRitePage.value) return;
      link.href = makePath({...store.contentParams.value, prayerType: link.dataset.prayerType, select: link.dataset.select, occasion: link.dataset.occasion});
    });
    link.addEventListener('click', () => {
      display.ritesMenuOpen.value = false;
    });
  }
}

function bindRite(store, display) {
  let main = document.getElementById('rite-container');
  let lineByLineMode = computed(() => display.displayParameters.value.showTranslation && !display.displayParameters.value.sideBySide);
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
    main.classList.toggle('chant-shown', parameters.chant);
    main.classList.toggle('chant-hidden', !parameters.chant);
    main.classList.toggle('chant-playback', parameters.chant && parameters.playChant);
    main.classList.toggle('side-by-side', parameters.showTranslation && parameters.sideBySide);
    main.classList.toggle('line-by-line', parameters.showTranslation && !parameters.sideBySide);
    main.classList.toggle('no-translation', !parameters.showTranslation);
  });
}

function bindNextHour(store) {
  let container = document.getElementById('next-hour-button-container');
  let button = document.getElementById('next-hour-button');
  let occasionName = document.getElementById('next-hour-occasion');
  let forbiddenTitle = button.dataset.forbiddenTitle;

  effect(() => {
    let target = store.nextHourButton.value;
    // Off a rite page the server-rendered href stays until the redirect lands on one
    if (target.path) {
      button.href = target.path;
    }
    occasionName.textContent = RITE_TITLES[target.occasion];
    button.classList.toggle('next-hour-button-forbidden', !target.allowed);
    button.title = target.allowed ? '' : forbiddenTitle;
  });
  button.addEventListener('click', (event) => {
    event.preventDefault();
    let target = store.nextHourButton.value;
    if (target.allowed && target.path) {
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

function bindBottomPanel(store, display) {
  let container = document.getElementById('bottom-easy-select-container');
  let hideButton = document.getElementById('bottom-easy-select-hide');
  let hideIcon = document.getElementById('bottom-easy-select-hide-icon');
  let content = document.getElementById('bottom-easy-select-content-container');

  effect(() => setShown(container, display.bottomPanelEnabled.value));
  toggleOnClick(hideButton, display.bottomPanelOpen);
  effect(() => {
    setShown(content, display.bottomPanelOpen.value);
    hideIcon.classList.toggle('bottom-easy-select-hide-icon-closed', !display.bottomPanelOpen.value);
  });

  let decrement = document.getElementById('date-selector-decrement');
  let increment = document.getElementById('date-selector-increment');
  let dateInput = document.getElementById('date-selector-text');
  let dateSubmit = document.getElementById('date-selector-text-submit');

  let setSubmitHref = () => {
    if (store.onRitePage.value && dateInput.value) {
      dateSubmit.href = makePath({...store.contentParams.value, date: dateInput.value});
    }
  };
  effect(() => {
    if (!store.onRitePage.value) return;
    let params = store.contentParams.value;
    decrement.href = shiftDatePath(params, -1);
    increment.href = shiftDatePath(params, 1);
    // Navigating resets the picker to the displayed date
    dateInput.value = params.date.toString();
    setSubmitHref();
  });
  dateInput.addEventListener('input', setSubmitHref);

  for (let button of document.querySelectorAll('.cursus-rite-selector-button')) {
    effect(() => {
      if (!store.onRitePage.value) return;
      let params = store.contentParams.value;
      button.href = cursusHourPath(params, button.dataset.occasion);
      button.classList.toggle('cursus-rite-selector-button-selected', isCurrentCursusHour(params, button.dataset.occasion));
    });
  }
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
    setDisplayParameter(display, key, checked);
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
  bindCheckbox(document.getElementById('bottom-panel-toggle'), () => display.bottomPanelEnabled.value, (checked) => {
    display.bottomPanelEnabled.value = checked;
  });

  for (let radio of document.querySelectorAll('input[name="desired"]')) {
    effect(() => {
      if (!store.onRitePage.value) return;
      radio.checked = store.contentParams.value.select == radio.dataset.select && store.opt.value.filter(t => t != 'privata').join('+') == radio.dataset.optTag;
    });
    radio.addEventListener('change', () => store.setDesired(radio.dataset.select, radio.dataset.optTag));
  }

  for (let checkbox of document.querySelectorAll('input[data-votive]')) {
    effect(() => {
      if (!store.onRitePage.value) return;
      checkbox.checked = store.contentParams.value.votives.includes(checkbox.dataset.votive);
    });
    checkbox.addEventListener('change', () => store.toggleVotive(checkbox.dataset.votive));
  }
}

// Links marked data-rite-link navigate within the page instead of reloading it.
// data-rite-link="hard" keeps the chosen rite on reload; otherwise ("soft") a reload may move on to a more relevant rite.
function bindRiteLinks(store) {
  document.addEventListener('click', (event) => {
    let link = event.target.closest('a[data-rite-link]');
    // Leave modified clicks (new tab/window) to the browser
    if (!link || event.button != 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    let url = new URL(link.href);
    store.navigateRite(url.pathname + url.search, link.dataset.riteLink || 'soft');
  });
}

export function bindPrayPage(store, display) {
  bindOverlayPanel(document.getElementById('options-panel-background'), document.getElementById('options-panel-wrapper'), display.optionsPanelOpen, document.getElementById('options-gear-button'));
  bindOverlayPanel(document.getElementById('ordo-panel-background'), document.getElementById('ordo-panel-wrapper'), display.ordoPanelOpen, document.getElementById('ordo-panel-toggle-button'));
  bindRitesMenu(store, display);
  bindRite(store, display);
  bindNextHour(store);
  bindBottomPanel(store, display);
  bindOptionsPanel(store, display);
  bindRiteLinks(store);
  window.addEventListener('popstate', () => store.handlePopstate());
}
