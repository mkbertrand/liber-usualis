// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Duration, pitch, and sequencing follow bbloomf/jgabc (Unlicense).

export const BPM = 165;
export const QUARTER_SECONDS = 60 / BPM;
export const QUILISMA = 3;
const DRAG_THRESHOLD = 8;
const SINGING_CENTER = 4 * 12 + 7;
const A4_INT = 4 * 12 + 9;

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

export function isSalicus(notes, noteId) {
  const note = neighborNote(notes, noteId);
  const nextNote = neighborNote(notes, noteId + 1);
  const prevNote = neighborNote(notes, noteId - 1);
  if (!note || !nextNote || !prevNote || !note.ictus) return false;
  const riseFromPrev = note.pitch.toInt() - prevNote.pitch.toInt();
  const riseToNext = nextNote.pitch.toInt() - note.pitch.toInt();
  if (riseFromPrev === 7 && riseToNext === 1) return true;
  const glyph = note.glyphVisualizer?.glyphCode;
  return note.ictus.glyphCode === 'VerticalEpisemaBelow'
    && (glyph === 'PodatusLower' || glyph === 'BeginningAscLiquescent')
    && riseFromPrev > 0
    && riseToNext > 0;
}

export function noteDuration(notes, noteId) {
  const note = notes[noteId];
  const nextNote = neighborNote(notes, noteId + 1);
  const prevNote = neighborNote(notes, noteId - 1);
  if (note.morae.length) return 2;
  if (nextNote && (nextNote.morae.length > 1 || nextNote.shape === QUILISMA || isSalicus(notes, noteId))) return 1.8;
  if (note.episemata.length) {
    let episemataCount = 1;
    if (prevNote?.episemata.length) episemataCount += 1;
    if (nextNote?.episemata.length) episemataCount += 1;
    return 1 + 0.9 / episemataCount;
  }
  return 1;
}

export function itemDuration(notes, index) {
  const item = notes[index];
  if (isNote(item)) return noteDuration(notes, index);
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

export function soundDuration(notes, noteId) {
  const note = notes[noteId];
  if (!isNote(note)) return 0;
  if (isApostropha(note) && note.neume.notes[0] === note) {
    return note.neume.notes.reduce((sum, member) => sum + noteDuration(notes, notes.indexOf(member)), 0);
  }
  const pressus = pressusPair(notes, noteId);
  if (pressus && pressus[0] === note) {
    return noteDuration(notes, noteId) + noteDuration(notes, noteId + 1);
  }
  if (isApostropha(note) || pressus) return 0;
  return noteDuration(notes, noteId);
}

export function durationList(notes) {
  return notes.map((_, index) => itemDuration(notes, index));
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

export function defaultTranspose(notes) {
  const pitched = notes.filter(isNote);
  if (pitched.length === 0) return 0;
  const ints = pitched.map((note) => note.pitch.toInt());
  return SINGING_CENTER - Math.floor((Math.min(...ints) + Math.max(...ints)) / 2);
}

export function pitchToHz(pitch, transpose = 0) {
  return 440 * 2 ** ((pitch.toInt() + transpose - A4_INT) / 12);
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
let voices = [];
let active = null;

function getContext() {
  if (!audioContext) {
    const Context = window.AudioContext || window.webkitAudioContext;
    audioContext = new Context();
    wave = audioContext.createPeriodicWave(new Float32Array([0, 0.3, 0.03, 0.05]), new Float32Array([0, 0, 0, 0]));
  }
  return audioContext;
}

function silence() {
  if (!audioContext) {
    voices = [];
    return;
  }
  const now = audioContext.currentTime;
  for (const {oscillator, envelope} of voices) {
    try {
      envelope.gain.cancelScheduledValues(now);
      envelope.gain.setTargetAtTime(0, now, 0.03);
      oscillator.stop(now + 0.2);
    } catch {
    }
  }
  voices = [];
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
  voices.push({oscillator, envelope});
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
  document.querySelectorAll('gabc-chant.chant-active').forEach((node) => {
    node.classList.remove('chant-active', 'chant-playing');
  });
  if (!element) return;
  element.classList.add('chant-active');
  element.classList.toggle('chant-playing', playing);
}

function elapsedNow() {
  if (!active) return 0;
  if (!active.playing) return active.elapsed;
  return active.elapsed + (getContext().currentTime - active.startedAt) / QUARTER_SECONDS;
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
}

function scheduleFrom(index) {
  const context = getContext();
  active.playing = true;
  active.startedAt = context.currentTime;
  markElement(active.element, true);

  const step = (from) => {
    let i = from;
    while (i < active.notes.length && itemDuration(active.notes, i) === 0) i += 1;
    if (!active?.playing) return;
    if (i >= active.notes.length) {
      finishPlayback();
      return;
    }
    active.index = i;
    const duration = itemDuration(active.notes, i);
    highlightItem(active.notes[i]);
    const sound = soundDuration(active.notes, i);
    if (sound > 0) {
      playFrequency(pitchToHz(active.notes[i].pitch, active.transpose), sound * QUARTER_SECONDS, context.currentTime);
    }
    active.timer = setTimeout(() => {
      step(i + 1);
    }, duration * QUARTER_SECONDS * 1000);
  };

  step(index);
}

function bindScore(element, startNote) {
  const notes = flattenNotations(element.score.notations);
  const durations = durationList(notes);
  const {starts, total} = cumulativeStarts(durations);
  let index = startNote ? notes.indexOf(startNote) : 0;
  if (index < 0) index = 0;
  active = {
    element,
    notes,
    starts,
    total,
    index,
    transpose: defaultTranspose(notes),
    playing: false,
    elapsed: starts[index] ?? 0,
    startedAt: 0,
    timer: null,
    highlighted: [],
  };
}

export function stopChantPlayback() {
  stopTimer();
  silence();
  clearHighlight();
  markElement(null, false);
  active = null;
}

export function pauseChantPlayback() {
  if (!active?.playing) return;
  active.elapsed = elapsedNow();
  active.playing = false;
  stopTimer();
  silence();
  markElement(active.element, false);
}

export function seekToIndex(index) {
  if (!active) return;
  pauseChantPlayback();
  let i = Math.max(0, Math.min(index, active.notes.length - 1));
  while (i < active.notes.length && itemDuration(active.notes, i) === 0) i += 1;
  if (i >= active.notes.length) i = active.notes.length - 1;
  active.index = i;
  active.elapsed = active.starts[i] ?? 0;
  highlightItem(active.notes[i]);
}

async function resumeOrStart(element, startNote) {
  const context = getContext();
  if (context.state !== 'running') await context.resume();
  if (!isPlaybackEnabled() || context.state !== 'running') return;
  if (active?.element === element && active.playing) return;
  if (active?.element === element && startNote == null) {
    if (active.total === 0) return;
    if (active.elapsed >= active.total) {
      active.index = 0;
      active.elapsed = 0;
    } else {
      active.index = indexAtTime(active.starts, active.total, active.elapsed);
      active.elapsed = active.starts[active.index] ?? 0;
    }
    scheduleFrom(active.index);
    return;
  }
  stopChantPlayback();
  bindScore(element, startNote);
  if (active.total === 0) return;
  scheduleFrom(active.index);
}

export function handleChantClick(element, event) {
  if (!isPlaybackEnabled() || !element.score) return;
  if (active?.element === element && active.playing) {
    pauseChantPlayback();
    return;
  }
  resumeOrStart(element, active?.element === element ? null : noteFromEvent(event));
}

function ensureBound(element) {
  if (active?.element === element) return;
  stopChantPlayback();
  bindScore(element, null);
  markElement(element, false);
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

export function attachChantPointerControls(element) {
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let seeking = false;
  let scrolling = false;

  const reset = () => {
    element.classList.remove('chant-seeking');
    pointerId = null;
    seeking = false;
    scrolling = false;
  };

  element.addEventListener('pointerdown', (event) => {
    if (!isPlaybackEnabled() || !element.score) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    seeking = false;
    scrolling = false;
    getContext().resume();
  });

  element.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointerId) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;
    if (!seeking && !scrolling) {
      if (Math.abs(dx) < DRAG_THRESHOLD && Math.abs(dy) < DRAG_THRESHOLD) return;
      if (Math.abs(dy) >= Math.abs(dx)) {
        scrolling = true;
        return;
      }
      seeking = true;
      element.classList.add('chant-seeking');
      element.setPointerCapture?.(event.pointerId);
      ensureBound(element);
      pauseChantPlayback();
    }
    if (seeking) seekToPointer(element, event);
  });

  element.addEventListener('pointerup', (event) => {
    if (event.pointerId !== pointerId) return;
    if (!seeking && !scrolling) handleChantClick(element, event);
    reset();
  });

  element.addEventListener('pointercancel', (event) => {
    if (event.pointerId !== pointerId) return;
    reset();
  });
}

export function notifyChantRelayout(element) {
  if (active?.element !== element) return;
  const elapsed = active.playing ? elapsedNow() : active.elapsed;
  pauseChantPlayback();
  const notes = flattenNotations(element.score.notations);
  const durations = durationList(notes);
  const {starts, total} = cumulativeStarts(durations);
  active.notes = notes;
  active.starts = starts;
  active.total = total;
  active.index = indexAtTime(starts, total, elapsed);
  active.elapsed = starts[active.index] ?? 0;
  highlightItem(active.notes[active.index]);
}
