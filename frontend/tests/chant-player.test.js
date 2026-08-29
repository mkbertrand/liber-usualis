// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import {
  QUILISMA,
  flattenNotations,
  isNote,
  isSkippedDivider,
  isLongDivider,
  noteDuration,
  itemDuration,
  isApostropha,
  pressusPair,
  soundDuration,
  durationList,
  cumulativeStarts,
  indexAtTime,
  defaultTranspose,
  pitchToHz,
} from '../chant-player.js';

function pitch(step, octave = 4) {
  return {
    step,
    octave,
    toInt() {
      return this.octave * 12 + this.step;
    },
  };
}

function note(opts = {}) {
  const created = {
    pitch: opts.pitch ?? pitch(0),
    morae: opts.morae ?? [],
    episemata: opts.episemata ?? [],
    shape: opts.shape ?? 0,
    ictus: opts.ictus,
    glyphVisualizer: opts.glyphVisualizer,
    neume: opts.neume,
  };
  if (!created.neume) {
    created.neume = {isNeume: true, notes: [created], lyrics: opts.lyrics ?? [{}]};
  }
  return created;
}

test('flattenNotations expands neume notes and drops accidentals', () => {
  const a = note();
  const b = note({pitch: pitch(2)});
  const bar = {isDivider: true, bar: 'half'};
  const accidental = {isAccidental: true};
  const flat = flattenNotations([
    {notes: [a, b]},
    accidental,
    bar,
  ]);
  assert.deepEqual(flat, [a, b, bar]);
});

test('divider classification follows bar type or constructor name', () => {
  assert.equal(isSkippedDivider({isDivider: true, bar: 'quarter'}), true);
  assert.equal(isLongDivider({isDivider: true, bar: 'full'}), true);
  assert.equal(isSkippedDivider({isDivider: true, bar: 'half'}), false);
  assert.equal(isNote({pitch: pitch(0)}), true);
  assert.equal(isNote({isDivider: true, pitch: pitch(0)}), false);
});

test('noteDuration doubles morae and lengthens quilismata and episemata', () => {
  const dotted = note({morae: [{}]});
  const plain = note();
  const quil = note({shape: QUILISMA});
  const episema = note({episemata: [{}]});
  const before = note({episemata: [{}]});
  const after = note({episemata: [{}]});
  assert.equal(noteDuration([dotted], 0), 2);
  assert.equal(noteDuration([plain, quil], 0), 1.8);
  assert.equal(noteDuration([episema], 0), 1.9);
  assert.equal(noteDuration([before, episema, after], 1), 1 + 0.9 / 3);
});

test('itemDuration treats skipped dividers as zero and full bars as two', () => {
  const plain = note();
  const notes = [plain, {isDivider: true, bar: 'quarter'}, {isDivider: true, bar: 'full'}, {isDivider: true, bar: 'half'}];
  assert.equal(itemDuration(notes, 0), 1);
  assert.equal(itemDuration(notes, 1), 0);
  assert.equal(itemDuration(notes, 2), 2);
  assert.equal(itemDuration(notes, 3), 1);
});

test('apostropha and pressus combine sounding duration on the first note only', () => {
  const first = note({pitch: pitch(7), lyrics: [{}]});
  const second = note({pitch: pitch(7)});
  const apostrophaNeume = {isNeume: true, notes: [first, second], lyrics: [{}]};
  first.neume = apostrophaNeume;
  second.neume = apostrophaNeume;
  assert.equal(isApostropha(first), true);
  assert.equal(soundDuration([first, second], 0), 2);
  assert.equal(soundDuration([first, second], 1), 0);

  const a = note({pitch: pitch(4)});
  const b = note({pitch: pitch(4), lyrics: []});
  a.neume = {isNeume: true, notes: [a], lyrics: [{}]};
  b.neume = {isNeume: true, notes: [b], lyrics: []};
  const pair = pressusPair([a, b], 0);
  assert.ok(pair);
  assert.equal(soundDuration([a, b], 0), 2);
  assert.equal(soundDuration([a, b], 1), 0);
});

test('cumulativeStarts and indexAtTime map slider ratios onto notes', () => {
  const notes = [note(), note({morae: [{}]}), {isDivider: true, bar: 'half'}];
  const durations = durationList(notes);
  assert.deepEqual(durations, [1, 2, 1]);
  const {starts, total} = cumulativeStarts(durations);
  assert.deepEqual(starts, [0, 1, 3]);
  assert.equal(total, 4);
  assert.equal(indexAtTime(starts, total, 0), 0);
  assert.equal(indexAtTime(starts, total, 0.5), 0);
  assert.equal(indexAtTime(starts, total, 1), 1);
  assert.equal(indexAtTime(starts, total, 2.9), 1);
  assert.equal(indexAtTime(starts, total, 3), 2);
  assert.equal(indexAtTime(starts, total, 4), 2);
});

test('defaultTranspose centers the chant near G4 and pitchToHz is A440 equal temperament', () => {
  const low = note({pitch: pitch(0, 3)});
  const high = note({pitch: pitch(0, 5)});
  assert.equal(defaultTranspose([low, high]), 55 - Math.floor((36 + 60) / 2));
  assert.equal(pitchToHz(pitch(9, 4)), 440);
  assert.ok(Math.abs(pitchToHz(pitch(0, 4)) - 440 * 2 ** ((48 - 57) / 12)) < 1e-9);
});
