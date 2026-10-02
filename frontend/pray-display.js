import { signal, effect } from '@preact/signals-core';

// Legacy key name, kept so that settings saved under it carry over
const DISPLAY_PARAMETERS_KEY = '_x_displayParameters';

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
  const displayParameters = signal({...DEFAULT_DISPLAY_PARAMETERS, ...readJSON(DISPLAY_PARAMETERS_KEY, {})});
  const optionsPanelOpen = signal(false);
  const ordoPanelOpen = signal(false);
  const ritesMenuOpen = signal(false);

  return {
    displayParameters: displayParameters,
    optionsPanelOpen: optionsPanelOpen,
    ordoPanelOpen: ordoPanelOpen,
    ritesMenuOpen: ritesMenuOpen,
    setDisplayParameter: (key, value) => {
      displayParameters.value = {...displayParameters.value, [key]: value};
    },
    toggleOptionsPanel: () => {
      optionsPanelOpen.value = !optionsPanelOpen.value;
    },
    closeOptionsPanel: () => {
      optionsPanelOpen.value = false;
    },
    toggleOrdoPanel: () => {
      ordoPanelOpen.value = !ordoPanelOpen.value;
    },
    closeOrdoPanel: () => {
      ordoPanelOpen.value = false;
    },
    toggleRitesMenu: () => {
      ritesMenuOpen.value = !ritesMenuOpen.value;
    },
    closeRitesMenu: () => {
      ritesMenuOpen.value = false;
    },
    // Saves the display parameters whenever they change
    persist: () => {
      effect(() => writeJSON(DISPLAY_PARAMETERS_KEY, displayParameters.value));
    }
  };
}
