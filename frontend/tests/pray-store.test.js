// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { nextHourTarget } from '../pray-store.js';

// Hard navigation never consults the clock, so a plain string stands in for the Temporal.PlainDate, and no time is
// given
test('nextHourTarget forbids the next hour in hard navigation', () => {
	let vesperae = {locale: 'en', prayerType: 'officium', date: '2026-10-09', select: 'primarium', occasion: 'vesperae', votives: []};
	assert.deepEqual(nextHourTarget(vesperae, null, null, 'hard'), {
		path: '/en/officium/2026-10-09/completorium',
		occasion: 'completorium',
		allowed: false
	});
});
