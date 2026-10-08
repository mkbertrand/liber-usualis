// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { rankName, ordoSummary, ordoRitePath, ordo } from '../pray-ordo.js';

test('rankName prefers the most specific rank tag', () => {
	assert.equal(rankName(['duplex', 'festum', 'duplex-i-classis', 'nativitas']), 'Duplex I. classis');
	assert.equal(rankName(['i-vesperae', 'duplex', 'duplex-majus', 'angeli-custodes']), 'Duplex majus');
	assert.equal(rankName(['confessor-pontifex', 'semiduplex', 'remigius']), 'Semiduplex');
	assert.equal(rankName(['i-vesperae', 'simplex', 'martyr']), 'Simplex');
	assert.equal(rankName(['suffragium', 'maria']), '');
});

test('ordoSummary takes the primary office, its rank, and the commemorations in order, without suffrages', () => {
	// Shape of /api/ordo for 2026-10-01, vesperale
	const response = {
		primary: ['Ss. Angelorum Custodum', ['i-vesperae', 'duplex', 'primarium', 'duplex-majus', 'angeli-custodes']],
		commemorations: [['S. Remigii Episcopi et Confessoris', ['ii-vesperae', 'semiduplex', 'commemoratio']], ['Ss. Placidi et Sociorum Martyrum', ['i-vesperae', 'simplex', 'commemoratio']], ['De Pace', ['suffragium', 'pro-pace', 'commemoratio']]],
		omissions: []
	};
	assert.deepEqual(ordoSummary(response), {
		primarium: 'Ss. Angelorum Custodum',
		rank: 'Duplex majus',
		commemorations: ['S. Remigii Episcopi et Confessoris', 'Ss. Placidi et Sociorum Martyrum']
	});
	assert.deepEqual(ordoSummary({...response, commemorations: [['De S. Maria', ['suffragium', 'maria', 'commemoratio']]]}).commemorations, []);
});

test('ordoRitePath uses the browsed date and votives, keeping only the Little Office from the page', () => {
	// Dates only need to stringify here, so a plain string stands in for Temporal.PlainDate
	const page = {locale: 'en', prayerType: 'officium', date: '2026-10-01', select: 'primarium', occasion: 'vesperae', votives: []};
	assert.equal(ordoRitePath('2026-10-03', ['de-joseph'], page, 'prima'), '/en/officium/2026-10-03/prima?v=de-joseph');
	assert.equal(ordoRitePath('2026-10-03', [], {...page, select: 'officium-parvum-bmv'}, 'vesperae'), '/en/officium/2026-10-03/officium-parvum-bmv/vesperae');
	assert.equal(ordoRitePath('2026-10-03', [], {...page, select: 'officium-defunctorum'}, 'vesperae'), '/en/officium/2026-10-03/vesperae');
	assert.equal(ordoRitePath('2026-10-03', [], {...page, prayerType: 'ritus', occasion: 'itinerarium'}, 'nona'), '/en/officium/2026-10-03/nona');
});

test('ordo fetches each date and time once, and discards everything when the votives change', async () => {
	const requests = [];
	const originalFetch = globalThis.fetch;
	globalThis.fetch = async (url) => {
		requests.push(url);
		return {json: async () => ({url: url})};
	};
	try {
		await ordo('2026-10-01', 'diurnale', []);
		await ordo('2026-10-01', 'diurnale', []);
		await ordo('2026-10-01', 'vesperale', []);
		assert.equal(requests.length, 2);

		await ordo('2026-10-01', 'diurnale', ['de-joseph']);
		assert.equal(requests.length, 3);
		// The earlier votives' responses were discarded, not kept alongside
		await ordo('2026-10-01', 'vesperale', []);
		assert.equal(requests.length, 4);
		assert.match(requests[2], /votives=de-joseph/);
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('ordo does not keep a failed request', async () => {
	let fail = true;
	const originalFetch = globalThis.fetch;
	globalThis.fetch = async () => {
		if (fail) throw new Error('offline');
		return {json: async () => ({})};
	};
	try {
		await assert.rejects(ordo('2026-11-01', 'diurnale', ['de-passione']));
		fail = false;
		assert.deepEqual(await ordo('2026-11-01', 'diurnale', ['de-passione']), {});
	} finally {
		globalThis.fetch = originalFetch;
	}
});
