// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Duration, pitch, and sequencing follow bbloomf/jgabc (Unlicense).

import { signal } from '@preact/signals-core';

export const BPM = 165;
export const MIN_BPM = 40;
export const MAX_BPM = 360;
export const QUILISMA = 3;
export const LONG_PRESS_MS = 2000;
const DRAG_THRESHOLD = 8;
const SINGING_CENTER = 4 * 12 + 7;
const A4_INT = 4 * 12 + 9;
const NOTE_NAMES = ['C', 'C\u266f', 'D', 'E\u266d', 'E', 'F', 'F\u266f', 'G', 'A\u266d', 'A', 'B\u266d', 'B'];
const SOLFEGE_NAMES = ['Do', 'Di', 'Re', 'Me', 'Mi', 'Fa', 'Fi', 'Sol', 'Si', 'La', 'Te', 'Ti'];
const INTERVALS = ['P1', 'm2', 'M2', 'm3', 'M3', 'P4', 'A4', 'P5', 'm6', 'M6', 'm7', 'M7'];

const playbackState = signal(null);
export const chantPlayback = { get value() { return playbackState.value; } };

export function isNote(item) {
  return Boolean(item && item.pitch && !item.isDivider);
}

export function flattenNotations(notations) {
  return notations.flatMap((notation) => notation.notes || notation).filter((item) => !item.isAccidental);
}

function ctorName(item) {
  return item?.constructor?.name ?? '';
}

export function isSkippedDivider(item) {
  return Boolean(item?.isDivider) && (ctorName(item) === 'QuarterBar' || item.bar === 'quarter');
}

export function isLongDivider(item) {
  return Boolean(item?.isDivider) && (ctorName(item) === 'FullBar' || ctorName(item) === 'DoubleBar' || item.bar === 'full');
}

function neighborNote(notes, index) {
  if (index < 0 || index >= notes.length) return null;
  const item = notes[index];
  return isNote(item) ? item : null;
}

function pitchesEqual(...pitches) {
  if (pitches.length <= 1) return true;
  const first = pitches[0];
  return pitches.every((pitch) => pitch.step === first.step && pitch.octave === first.octave);
}

export function isSalicus(notes, noteId, solesmes = true) {
  const note = neighborNote(notes, noteId);
  const nextNote = neighborNote(notes, noteId + 1);
  const prevNote = neighborNote(notes, noteId - 1);
  if (!note || !nextNote || !prevNote || !note.ictus) return false;
  const riseFromPrev = note.pitch.toInt() - prevNote.pitch.toInt();
  const riseToNext = nextNote.pitch.toInt() - note.pitch.toInt();
  if (riseFromPrev === 7 && riseToNext === 1) return true;
  const glyph = note.glyphVisualizer?.glyphCode;
  return solesmes && note.ictus.glyphCode === 'VerticalEpisemaBelow'
    && (glyph === 'PodatusLower' || glyph === 'BeginningAscLiquescent')
    && riseFromPrev > 0
    && riseToNext > 0;
}

export function noteDuration(notes, noteId, solesmes = true) {
  const note = notes[noteId];
  const nextNote = neighborNote(notes, noteId + 1);
  const prevNote = neighborNote(notes, noteId - 1);
  if (note.morae.length) return 2;
  if (nextNote && (nextNote.morae.length > 1 || nextNote.shape === QUILISMA || isSalicus(notes, noteId, solesmes))) return 1.8;
  if (note.episemata.length) {
    let episemataCount = 1;
    if (prevNote?.episemata.length) episemataCount += 1;
    if (nextNote?.episemata.length) episemataCount += 1;
    return 1 + 0.9 / episemataCount;
  }
  return 1;
}

export function itemDuration(notes, index, solesmes = true) {
  const item = notes[index];
  if (isNote(item)) return noteDuration(notes, index, solesmes);
  if (!item?.isDivider || isSkippedDivider(item)) return 0;
  if (isLongDivider(item)) return 2;
  return 1;
}

export function isApostropha(note) {
  const neume = note.neume;
  return Boolean(neume?.isNeume && neume.notes.length > 1 && pitchesEqual(...neume.notes.map((n) => n.pitch)));
}

function isPressusStart(notes, index) {
  const note = neighborNote(notes, index);
  const nextNote = neighborNote(notes, index + 1);
  if (!note || !nextNote) return false;
  const lastInNeume = note === note.neume.notes[note.neume.notes.length - 1];
  const firstInNeume = nextNote === nextNote.neume.notes[0];
  return lastInNeume
    && firstInNeume
    && note.morae.length === 0
    && nextNote.morae.length === 0
    && pitchesEqual(note.pitch, nextNote.pitch)
    && !isApostropha(note)
    && !isApostropha(nextNote)
    && (nextNote.neume.lyrics || []).length === 0;
}

export function pressusPair(notes, noteId) {
  const note = neighborNote(notes, noteId);
  if (!note) return null;
  if (isPressusStart(notes, noteId) && !isPressusStart(notes, noteId - 1)) {
    return [note, neighborNote(notes, noteId + 1)];
  }
  if (isPressusStart(notes, noteId - 1) && !isPressusStart(notes, noteId - 2)) {
    return [neighborNote(notes, noteId - 1), note];
  }
  return null;
}

export function soundDuration(notes, noteId, solesmes = true) {
  const note = notes[noteId];
  if (!isNote(note)) return 0;
  if (isApostropha(note) && note.neume.notes[0] === note) {
    return note.neume.notes.reduce((sum, member) => sum + noteDuration(notes, notes.indexOf(member), solesmes), 0);
  }
  const pressus = pressusPair(notes, noteId);
  if (pressus && pressus[0] === note) {
    return noteDuration(notes, noteId, solesmes) + noteDuration(notes, noteId + 1, solesmes);
  }
  if (isApostropha(note) || pressus) return 0;
  return noteDuration(notes, noteId, solesmes);
}

export function durationList(notes, solesmes = true) {
  return notes.map((_, index) => itemDuration(notes, index, solesmes));
}

export function cumulativeStarts(durations) {
  const starts = [];
  let time = 0;
  for (const duration of durations) {
    starts.push(time);
    time += duration;
  }
  return {starts, total: time};
}

export function indexAtTime(starts, total, time) {
  if (starts.length === 0) return 0;
  if (time <= 0) return 0;
  if (time >= total) return starts.length - 1;
  let index = starts.findIndex((start) => start > time);
  if (index < 0) return starts.length - 1;
  return index === 0 ? 0 : index - 1;
}

function pitchRange(notes) {
  let range = null;
  for (const note of notes) {
    if (!isNote(note)) continue;
    const pitch = note.pitch.toInt();
    if (!range) range = { first: pitch, low: pitch, high: pitch };
    range.low = Math.min(range.low, pitch);
    range.high = Math.max(range.high, pitch);
  }
  return range;
}

function centeredTranspose({low, high}) {
  return SINGING_CENTER - Math.floor((low + high) / 2);
}

export function defaultTranspose(notes) {
  const range = pitchRange(notes);
  return range ? centeredTranspose(range) : 0;
}

function pitchClass(pitch) {
  return ((pitch % 12) + 12) % 12;
}

function pitchName(pitch, names = NOTE_NAMES) {
  return names[pitchClass(pitch)] + Math.floor(pitch / 12);
}

export function describeChantPitch({first, low, high}, transpose) {
  const distance = high - low;
  const [quality, degree] = INTERVALS[distance % 12];
  return {
    first: pitchName(first + transpose),
    low: pitchName(low + transpose),
    high: pitchName(high + transpose),
    lowSolfege: pitchName(low, SOLFEGE_NAMES),
    highSolfege: pitchName(high, SOLFEGE_NAMES),
    interval: quality + (Number(degree) + 7 * Math.floor(distance / 12)),
    doPitch: NOTE_NAMES[pitchClass(transpose)],
  };
}

export function pitchToHz(pitch, transpose = 0) {
  return pitchIntToHz(pitch.toInt() + transpose);
}

function pitchIntToHz(pitch) {
  return 440 * 2 ** ((pitch - A4_INT) / 12);
}

export function noteFromEvent(event) {
  const use = event.target.closest?.('use');
  if (!use?.source?.pitch || use.source.isDivider) return null;
  return use.source;
}

export function indexNearestPoint(points, x, y) {
  let best = 0;
  let bestDist = Infinity;
  for (let i = 0; i < points.length; i++) {
    const dist = (points[i].x - x) ** 2 + (points[i].y - y) ** 2;
    if (dist < bestDist) {
      bestDist = dist;
      best = i;
    }
  }
  return best;
}

export function isPlaybackEnabled() {
  return Boolean(document.getElementById('rite-container')?.classList.contains('chant-playback'));
}

let audioContext;
let wave;
const voices = new Set();
let active = null;
let bpm = BPM;
let solesmes = true;
let playRequest = 0;
const transpositions = new WeakMap();

function getContext() {
  if (!audioContext) {
    const Context = window.AudioContext || window.webkitAudioContext;
    audioContext = new Context();
    wave = audioContext.createPeriodicWave(new Float32Array([0, 0.3, 0.03, 0.05]), new Float32Array([0, 0, 0, 0]));
  }
  return audioContext;
}

function silence() {
  if (!audioContext) return;
  const now = audioContext.currentTime;
  for (const {oscillator, envelope} of voices) {
    try {
      envelope.gain.cancelScheduledValues(now);
      envelope.gain.setTargetAtTime(0, now, 0.03);
      oscillator.stop(now + 0.2);
    } catch {
    }
  }
  voices.clear();
}

function playFrequency(hz, durationSec, when) {
  const context = getContext();
  const startAt = Math.max(when, context.currentTime);
  const oscillator = context.createOscillator();
  const envelope = context.createGain();
  oscillator.setPeriodicWave(wave);
  oscillator.frequency.setValueAtTime(hz, startAt);
  oscillator.connect(envelope);
  envelope.connect(context.destination);
  envelope.gain.setValueAtTime(0, startAt);
  envelope.gain.setTargetAtTime(0.33, startAt, 0.05 / 3);
  envelope.gain.setTargetAtTime(0, startAt + Math.max(durationSec, 0.05), 0.3 / 3);
  oscillator.start(startAt);
  oscillator.stop(startAt + durationSec + 0.8);
  const voice = {oscillator, envelope};
  voices.add(voice);
  oscillator.onended = () => {
    voices.delete(voice);
    oscillator.disconnect();
    envelope.disconnect();
  };
}

function clearHighlight() {
  if (!active) return;
  for (const node of active.highlighted) {
    node.classList.remove('active', 'porrectus-left', 'porrectus-right');
  }
  active.highlighted = [];
}

function highlightItem(item) {
  clearHighlight();
  if (!item || !isNote(item) || !item.svgNode) return;
  let node = item.svgNode;
  const href = node.getAttribute?.('href') || node.getAttributeNS?.('http://www.w3.org/1999/xlink', 'href') || '';
  if (href === '#None' && node.previousSibling) {
    node = node.previousSibling;
    node.classList.add('porrectus-right');
  } else if (/^#Porrectus/.test(href)) {
    node.classList.add('porrectus-left');
  }
  node.classList.add('active');
  active.highlighted.push(node);
  const group = node.closest?.('.ChantNotationElement') || node.parentElement?.parentElement;
  const lyric = group?.querySelector('text.lyric, text');
  if (lyric) {
    lyric.classList.add('active');
    active.highlighted.push(lyric);
  }
}

function stopTimer() {
  if (active?.timer != null) {
    clearTimeout(active.timer);
    active.timer = null;
  }
}

function markElement(element, playing) {
  element.classList.add('chant-active');
  element.classList.toggle('chant-playing', playing);
}

function publishPlayback() {
  playbackState.value = active && {
    element: active.element,
    playing: active.playing,
    pitch: describeChantPitch(active.range, active.transpose),
    bpm,
    solesmes,
  };
}

function elapsedNow() {
  if (!active) return 0;
  if (!active.playing) return active.elapsed;
  const duration = itemDuration(active.notes, active.index, solesmes);
  return active.elapsed + Math.min((getContext().currentTime - active.startedAt) * bpm / 60, duration);
}

function finishPlayback() {
  if (!active) return;
  silence();
  stopTimer();
  clearHighlight();
  active.playing = false;
  active.index = 0;
  active.elapsed = 0;
  markElement(active.element, false);
  publishPlayback();
}

function scheduleFrom(index) {
  const context = getContext();
  active.playing = true;
  markElement(active.element, true);
  publishPlayback();

  const step = (from) => {
    if (!active?.playing) return;
    let i = from;
    while (i < active.notes.length && itemDuration(active.notes, i, solesmes) === 0) i += 1;
    if (i >= active.notes.length) {
      finishPlayback();
      return;
    }
    active.index = i;
    active.elapsed = active.starts[i];
    active.startedAt = context.currentTime;
    const duration = itemDuration(active.notes, i, solesmes);
    const quarterSeconds = 60 / bpm;
    highlightItem(active.notes[i]);
    const sound = soundDuration(active.notes, i, solesmes);
    if (sound > 0) {
      playFrequency(pitchToHz(active.notes[i].pitch, active.transpose), sound * quarterSeconds, context.currentTime);
    }
    active.timer = setTimeout(() => {
      step(i + 1);
    }, duration * quarterSeconds * 1000);
  };

  step(index);
}

function bindScore(element, startNote) {
  const notes = flattenNotations(element.score.notations);
  const range = pitchRange(notes);
  if (!range) return false;
  stopChantPlayback();
  const durations = durationList(notes, solesmes);
  const {starts, total} = cumulativeStarts(durations);
  let index = startNote ? notes.indexOf(startNote) : 0;
  if (index < 0) index = 0;
  active = {
    element,
    notes,
    starts,
    total,
    index,
    range,
    transpose: transpositions.get(element) ?? centeredTranspose(range),
    playing: false,
    elapsed: starts[index] ?? 0,
    startedAt: 0,
    timer: null,
    highlighted: [],
  };
  markElement(element, false);
  publishPlayback();
  return true;
}

export function stopChantPlayback() {
  playRequest++;
  stopTimer();
  silence();
  clearHighlight();
  active?.element.classList.remove('chant-active', 'chant-playing');
  active = null;
  publishPlayback();
}

export function pauseChantPlayback() {
  playRequest++;
  silence();
  if (!active?.playing) return;
  active.elapsed = elapsedNow();
  active.playing = false;
  stopTimer();
  markElement(active.element, false);
  publishPlayback();
}

export function seekToIndex(index) {
  if (!active) return;
  pauseChantPlayback();
  let i = Math.max(0, Math.min(index, active.notes.length - 1));
  while (i < active.notes.length && itemDuration(active.notes, i, solesmes) === 0) i += 1;
  if (i >= active.notes.length) i = active.notes.length - 1;
  active.index = i;
  active.elapsed = active.starts[i] ?? 0;
  highlightItem(active.notes[i]);
}

export function prepareChantPlayback(element, startNote) {
  if (!isPlaybackEnabled() || !element.isConnected || !element.score) return false;
  return active?.element === element || bindScore(element, startNote);
}

async function resumeAudio() {
  const context = getContext();
  try {
    if (context.state !== 'running') await context.resume();
  } catch {
    return false;
  }
  return context.state === 'running';
}

export async function playChant(element, startNote) {
  if (!prepareChantPlayback(element, startNote) || active.playing) return;
  const request = ++playRequest;
  if (!await resumeAudio() || playRequest !== request || !isPlaybackEnabled()) return;
  silence();
  const index = active.elapsed >= active.total ? 0 : indexAtTime(active.starts, active.total, active.elapsed);
  scheduleFrom(index);
}

export function changeChantPitch(delta) {
  if (!active) return;
  active.transpose += delta;
  transpositions.set(active.element, active.transpose);
  updatePlaybackSettings();
}

async function auditionPitch(pitch, duration) {
  const request = ++playRequest;
  if (!await resumeAudio() || playRequest !== request || !isPlaybackEnabled()) return;
  playFrequency(pitchIntToHz(pitch), duration, getContext().currentTime);
}

export function previewChantPitch() {
  if (!active) return;
  pauseChantPlayback();
  return auditionPitch(active.range.first + active.transpose, 0.45);
}

export function changeChantTempo(delta) {
  bpm = Math.max(MIN_BPM, Math.min(MAX_BPM, bpm + delta));
  if (active) updatePlaybackSettings();
}

export function toggleSolesmesLengths() {
  if (!active) return;
  solesmes = !solesmes;
  const {starts, total} = cumulativeStarts(durationList(active.notes, solesmes));
  active.starts = starts;
  active.total = total;
  updatePlaybackSettings();
}

function updatePlaybackSettings() {
  active.elapsed = active.starts[active.index];
  silence();
  if (active.playing) {
    stopTimer();
    scheduleFrom(active.index);
  } else {
    publishPlayback();
  }
}

export function stepChantForward() {
  if (!active) return;
  const index = active.notes.findIndex((item, i) => i > active.index && isNote(item));
  if (index < 0) {
    pauseChantPlayback();
    return;
  }
  seekToIndex(index);
  return auditionPitch(active.notes[index].pitch.toInt() + active.transpose, 60 / bpm);
}

export function handleChantClick(element, event) {
  if (!isPlaybackEnabled() || !element.score) return;
  if (active?.element === element && active.playing) {
    pauseChantPlayback();
    return;
  }
  playChant(element, noteFromEvent(event));
}

function seekToPointer(element, event) {
  if (active?.element !== element) return;
  const points = [];
  for (let i = 0; i < active.notes.length; i++) {
    const node = active.notes[i].svgNode;
    if (!isNote(active.notes[i]) || !node?.getBoundingClientRect) continue;
    const rect = node.getBoundingClientRect();
    points.push({index: i, x: rect.left + rect.width / 2, y: rect.top + rect.height / 2});
  }
  if (points.length === 0) return;
  const nearest = points[indexNearestPoint(points, event.clientX, event.clientY)];
  seekToIndex(nearest.index);
}

export function attachChantPointerControls(element, openControls) {
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let seeking = false;
  let scrolling = false;
  let pressTimer;

  const reset = () => {
    clearTimeout(pressTimer);
    element.classList.remove('chant-seeking');
    pointerId = null;
    seeking = false;
    scrolling = false;
  };

  element.addEventListener('pointerdown', (event) => {
    if (!isPlaybackEnabled() || !element.score || !event.target.closest?.('.chantelement-chant-content > svg')) return;
    if (pointerId !== null || !event.isPrimary || event.button !== 0) return;
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    seeking = false;
    scrolling = false;
    if (event.pointerType === 'mouse') event.preventDefault();
    pressTimer = setTimeout(() => {
      reset();
      if (element.isConnected && isPlaybackEnabled()) openControls(element, noteFromEvent(event));
    }, LONG_PRESS_MS);
  });

  element.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointerId) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;
    if (!seeking && !scrolling) {
      if (Math.abs(dx) < DRAG_THRESHOLD && Math.abs(dy) < DRAG_THRESHOLD) return;
      clearTimeout(pressTimer);
      if (Math.abs(dy) >= Math.abs(dx)) {
        scrolling = true;
        return;
      }
      seeking = true;
      element.classList.add('chant-seeking');
      window.getSelection?.()?.removeAllRanges();
      element.setPointerCapture?.(event.pointerId);
      if (prepareChantPlayback(element)) pauseChantPlayback();
    }
    if (seeking) seekToPointer(element, event);
  });

  element.addEventListener('pointerup', (event) => {
    if (event.pointerId !== pointerId) return;
    if (!seeking && !scrolling && event.target.closest?.('.chantelement-chant-content > svg')) handleChantClick(element, event);
    reset();
  });

  for (const type of ['pointercancel', 'lostpointercapture', 'pointerleave']) {
    element.addEventListener(type, (event) => {
      if (event.pointerId === pointerId && (type !== 'pointerleave' || !seeking)) reset();
    });
  }

  element.addEventListener('contextmenu', (event) => {
    if (isPlaybackEnabled() && event.target.closest?.('.chantelement-chant-content > svg')) event.preventDefault();
  });

  element.addEventListener('keydown', (event) => {
    if (event.target !== element || event.repeat || !isPlaybackEnabled() || !element.score) return;
    if (event.key === 'ContextMenu' || (event.shiftKey && event.key === 'F10')) {
      event.preventDefault();
      openControls(element);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleChantClick(element, event);
    }
  });
}

export function notifyChantRelayout(element) {
  if (active?.element !== element) return;
  const elapsed = active.playing ? elapsedNow() : active.elapsed;
  pauseChantPlayback();
  const notes = flattenNotations(element.score.notations);
  const durations = durationList(notes, solesmes);
  const {starts, total} = cumulativeStarts(durations);
  active.notes = notes;
  active.starts = starts;
  active.total = total;
  active.index = indexAtTime(starts, total, elapsed);
  active.elapsed = starts[active.index] ?? 0;
  highlightItem(active.notes[active.index]);
}
