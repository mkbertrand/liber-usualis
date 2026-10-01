import { signal, effect } from '@preact/signals-core';

// Legacy key names, kept so that settings saved under them carry over
const DISPLAY_PARAMETERS_KEY = '_x_displayParameters';
const BOTTOM_PANEL_ENABLED_KEY = '_x_bottomPanelEnabled';

const DEFAULT_DISPLAY_PARAMETERS = {
  'chant': false,
  'displayTrivialChants': false,
  'showTranslation': true,
  'sideBySide': false,
  'playChant': false
};

function readJSON(key, fallback) {
  try {
    let stored = localStorage.getItem(key);
    return stored === null ? fallback : JSON.parse(stored);
  } catch {
    return fallback;
  }
}

function writeJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage unavailable (e.g. private browsing) - preferences just don't persist
  }
}

export function makeDisplayStore() {
  return {
    displayParameters: signal({...DEFAULT_DISPLAY_PARAMETERS, ...readJSON(DISPLAY_PARAMETERS_KEY, {})}),
    bottomPanelEnabled: signal(readJSON(BOTTOM_PANEL_ENABLED_KEY, false)),
    bottomPanelOpen: signal(true),
    optionsPanelOpen: signal(false),
    ordoPanelOpen: signal(false),
    ritesMenuOpen: signal(false),
  };
}

export function setDisplayParameter(display, key, value) {
  display.displayParameters.value = {...display.displayParameters.value, [key]: value};
}

export function persistDisplayStore(display) {
  effect(() => writeJSON(DISPLAY_PARAMETERS_KEY, display.displayParameters.value));
  effect(() => writeJSON(BOTTOM_PANEL_ENABLED_KEY, display.bottomPanelEnabled.value));
}
