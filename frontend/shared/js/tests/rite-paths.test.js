// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { makePath, officeHourPath } from '../rite-paths.js';

// Dates only need to stringify here, so plain strings stand in for Temporal.PlainDate
const vesperae = {locale: 'en', prayerType: 'officium', date: '2026-10-01', select: 'primarium', occasion: 'vesperae', votives: []};

test('makePath omits the primary select and empty votives', () => {
	assert.equal(makePath(vesperae), '/en/officium/2026-10-01/vesperae');
	assert.equal(makePath({...vesperae, select: 'officium-parvum-bmv', votives: ['de-joseph', 'de-passione']}), '/en/officium/2026-10-01/officium-parvum-bmv/vesperae?v=de-joseph+de-passione');
});

test('officeHourPath keeps only the Little Office from the select, with the given date and the params votives', () => {
	assert.equal(officeHourPath({...vesperae, votives: ['de-joseph']}, '2026-10-02', 'matutinum-laudes'), '/en/officium/2026-10-02/matutinum-laudes?v=de-joseph');
	assert.equal(officeHourPath({...vesperae, select: 'officium-parvum-bmv'}, '2026-10-01', 'prima'), '/en/officium/2026-10-01/officium-parvum-bmv/prima');
	assert.equal(officeHourPath({...vesperae, select: 'officium-defunctorum'}, '2026-10-01', 'prima'), '/en/officium/2026-10-01/prima');
	assert.equal(officeHourPath({...vesperae, prayerType: 'ritus', occasion: 'itinerarium'}, '2026-10-01', 'nona'), '/en/officium/2026-10-01/nona');
});
