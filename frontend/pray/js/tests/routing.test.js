// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { suggestOccasion } from '../routing.js';

test('suggestOccasion follows the hour of the day', () => {
	const expected = [[0, 'matutinum-laudes'], [5, 'matutinum-laudes'], [6, 'prima'], [8, 'tertia'], [11, 'sexta'], [14, 'nona'], [16, 'vesperae'], [20, 'completorium'], [21, 'completorium'], [22, 'matutinum-laudes']];
	for (const [hour, occasion] of expected) {
		assert.equal(suggestOccasion({hour: hour}), occasion, `hour ${hour}`);
	}
});
