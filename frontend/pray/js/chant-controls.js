// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import { effect } from '@preact/signals-core';
import {
  chantPlayback, prepareChantPlayback, playChant, pauseChantPlayback,
  changeChantPitch, previewChantPitch, changeChantTempo, stepChantForward, toggleSolesmesLengths,
  MIN_BPM, MAX_BPM,
} from './chant-player.js';

export function bindChantControls() {
  const dialog = document.getElementById('chant-context');
  const dock = document.getElementById('chant-controls-dock');
  const toolbar = document.getElementById('chant-playback-controls');
  const pitchSettings = toolbar.querySelector('[data-chant-settings]');
  const playPause = toolbar.querySelector('.play-pause');
  const tempoMinus = toolbar.querySelector('.tempo-minus');
  const tempoPlus = toolbar.querySelector('.tempo-plus');
  const tempoNumber = toolbar.querySelector('.tempo-number');
  const solesmes = toolbar.querySelector('.solesmes-lengths');
  let shown = false;
  let returnFocus;

  function openDialog() {
    returnFocus = document.activeElement;
    // Keep the same controls usable inside the modal, where the dock is inert.
    dialog.append(toolbar);
    pitchSettings.hidden = true;
    dialog.showModal();
  }

  function closeDialog() {
    if (!dialog.open) return;
    dialog.close();
    pitchSettings.hidden = false;
    dock.append(toolbar);
    if (returnFocus?.isConnected && (!toolbar.hidden || !toolbar.contains(returnFocus))) {
      returnFocus.focus({preventScroll: true});
    }
    returnFocus = null;
  }

  function hideControls() {
    shown = false;
    toolbar.hidden = true;
    closeDialog();
  }

  function openControls(element, startNote) {
    if (!prepareChantPlayback(element, startNote)) return;
    shown = true;
    toolbar.hidden = false;
    if (!dialog.open) {
      // Pointerdown on the score doesn't focus it; make it the dialog's return target.
      element.focus({preventScroll: true});
      openDialog();
    }
  }

  dialog.querySelector('[data-chant-close]').addEventListener('click', closeDialog);
  dialog.addEventListener('cancel', (event) => {
    event.preventDefault();
    closeDialog();
  });
  dialog.querySelector('[data-pitch-down]').addEventListener('click', () => changeChantPitch(-1));
  dialog.querySelector('[data-pitch-up]').addEventListener('click', () => changeChantPitch(1));
  dialog.querySelector('[data-pitch-preview]').addEventListener('click', previewChantPitch);
  pitchSettings.addEventListener('click', openDialog);
  playPause.addEventListener('click', () => {
    const state = chantPlayback.value;
    if (!state) return;
    if (state.playing) pauseChantPlayback();
    else playChant(state.element);
  });
  toolbar.querySelector('.step-forward').addEventListener('click', stepChantForward);
  toolbar.querySelector('.stop').addEventListener('click', () => {
    const element = chantPlayback.value?.element;
    pauseChantPlayback();
    hideControls();
    if (element?.isConnected) element.focus({preventScroll: true});
  });
  tempoMinus.addEventListener('click', () => changeChantTempo(-5));
  tempoPlus.addEventListener('click', () => changeChantTempo(5));
  solesmes.addEventListener('change', toggleSolesmesLengths);

  const pitchFields = Object.fromEntries(
    [...dialog.querySelectorAll('[data-chant-pitch]')].map((node) => [node.dataset.chantPitch, node]),
  );
  effect(() => {
    const state = chantPlayback.value;
    if (!state) {
      hideControls();
      return;
    }
    toolbar.hidden = !shown;
    for (const [key, node] of Object.entries(pitchFields)) node.textContent = state.pitch[key];
    tempoNumber.textContent = state.bpm;
    tempoMinus.disabled = state.bpm <= MIN_BPM;
    tempoPlus.disabled = state.bpm >= MAX_BPM;
    solesmes.checked = state.solesmes;
    playPause.textContent = state.playing ? playPause.dataset.pause : playPause.dataset.play;
  });

  return openControls;
}
