// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { defineAmbit } from '../ambit.js';

function riteIds(ambit) {
	return ambit.occasions.map((o) => o.rite);
}

test('omnes ambit is the full seven-hour sequence, requested as primarium/officium', () => {
	const ambit = defineAmbit('omnes');
	assert.deepEqual(riteIds(ambit), ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']);
	assert.equal(ambit.select, 'primarium');
	assert.equal(ambit.type, 'officium');
	assert.equal(ambit.opt, '');
});

test('officium-parvum-bmv ambit keeps the seven-hour sequence but selects the Little Office', () => {
	const ambit = defineAmbit('officium-parvum-bmv');
	assert.deepEqual(riteIds(ambit), ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']);
	assert.equal(ambit.select, 'officium-parvum-bmv');
});

test('semper-cum-opbmv and diei ambits carry their distinguishing opt flag', () => {
	assert.equal(defineAmbit('semper-cum-opbmv').opt, 'cum-opbmv');
	assert.equal(defineAmbit('diei').opt, 'sine-ritibus');
});

test('officium-defunctorum ambit only offers Matins/Lauds and Vespers', () => {
	const ambit = defineAmbit('officium-defunctorum');
	assert.deepEqual(riteIds(ambit), ['matutinum-laudes', 'vesperae']);
	assert.equal(ambit.select, 'officium-defunctorum');
});

test('single-occasion ambits (votive rites) expose exactly one occasion matching the request', () => {
	const graduales = defineAmbit('psalmi-graduales');
	assert.deepEqual(riteIds(graduales), ['psalmi-graduales']);
	assert.equal(graduales.type, 'ritus');
	assert.equal(graduales.select, 'primarium');

	const itinerarium = defineAmbit('itinerarium');
	assert.deepEqual(riteIds(itinerarium), ['itinerarium']);
});

test('sevenHourTemplater suggests an occasion for every hour of the day, in order', () => {
	const ambit = defineAmbit('omnes');
	const expectations = [
		[0, 'matutinum-laudes'], [5, 'matutinum-laudes'],
		[6, 'prima'], [8, 'prima'],
		[9, 'tertia'], [10, 'tertia'],
		[11, 'sexta'], [13, 'sexta'],
		[14, 'nona'], [15, 'nona'],
		[16, 'vesperae'], [19, 'vesperae'],
		[20, 'completorium'], [23, 'completorium'],
	];
	for (const [hour, expectedRite] of expectations) {
		assert.equal(ambit.suggestSelectedOccasion(hour).rite, expectedRite, `hour ${hour}`);
	}
});

test('officium-defunctorum ambit suggests Matins/Lauds before 4pm and Vespers after', () => {
	const ambit = defineAmbit('officium-defunctorum');
	assert.equal(ambit.suggestSelectedOccasion(15).rite, 'matutinum-laudes');
	assert.equal(ambit.suggestSelectedOccasion(16).rite, 'vesperae');
});

test('riteIndex locates an occasion by rite id and reports -1 when absent', () => {
	const ambit = defineAmbit('omnes');
	assert.equal(ambit.riteIndex('sexta'), 3);
	assert.equal(ambit.riteIndex('nonexistent'), -1);
});

test('nextOccasion advances through the sequence and wraps from the last back to the first', () => {
	const ambit = defineAmbit('omnes');
	assert.equal(ambit.nextOccasion('prima').rite, 'tertia');
	assert.equal(ambit.nextOccasion('completorium').rite, 'matutinum-laudes');
});

test('slideAmbitOccasion keeps the same occasion when switching ambits if it exists there', () => {
	const fullAmbit = defineAmbit('omnes');
	const defunct = defineAmbit('officium-defunctorum');
	assert.equal(fullAmbit.slideAmbitOccasion(defunct, 'vesperae'), 'vesperae');
});

test('slideAmbitOccasion falls back to the new ambit\'s first occasion when the current one has no equivalent', () => {
	const fullAmbit = defineAmbit('omnes');
	const defunct = defineAmbit('officium-defunctorum');
	assert.equal(fullAmbit.slideAmbitOccasion(defunct, 'tertia'), 'matutinum-laudes');
});
