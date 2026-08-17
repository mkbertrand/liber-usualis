// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

import { renderRite } from '../rite-renderer/rite-renderer.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturesDir = path.join(here, 'fixtures');

function loadFixture(name) {
	return JSON.parse(readFileSync(path.join(fixturesDir, `${name}.json`), 'utf8'));
}

const resources = {
	invitatoria: JSON.parse(readFileSync(path.join(fixturesDir, 'resources', 'invitatoria.json'), 'utf8')),
	psalmTones: JSON.parse(readFileSync(path.join(fixturesDir, 'resources', 'toni-psalmorum.json'), 'utf8')),
};

const fixtureNames = readdirSync(fixturesDir)
	.filter((f) => f.endsWith('.json'))
	.map((f) => f.slice(0, -'.json'.length));

test('every fixture rite renders to well-formed, non-empty markup with no leaked placeholders', () => {
	for (const name of fixtureNames) {
		const html = renderRite(loadFixture(name), resources);
		assert.ok(html.length > 0, `${name}: rendered nothing`);

		const opens = (html.match(/<div\b/g) || []).length;
		const closes = (html.match(/<\/div>/g) || []).length;
		assert.equal(opens, closes, `${name}: unbalanced <div> tags`);

		assert.doesNotMatch(html, /undefined|\[object Object\]|NaN/, `${name}: leaked a raw JS artifact into rendered output`);
	}
});

test('a combined Matins & Lauds occasion renders both hour headers in order', () => {
	const html = renderRite(loadFixture('matutinum-laudes-circumcisio'), resources);
	assert.ok(html.indexOf('Ad Matutinum.') < html.indexOf('Ad Laudes.'), 'expected Matins heading before Lauds heading');
});

test('a rite with resolved commemorations renders a Commemorationes section and parallel translation text', () => {
	const html = renderRite(loadFixture('matutinum-laudes-commemorations-english'), resources);
	assert.match(html, /Commemorationes\./);
	assert.match(html, /class="rite-text-container[^"]*"><p class="rite-text rite-text-latin">[^<]+<\/p><p class="rite-text rite-text-translation">[^<]+<\/p>/);
});

test('a votive rite with no commemorations renders no Commemorationes section', () => {
	const html = renderRite(loadFixture('psalmi-graduales'), resources);
	assert.doesNotMatch(html, /Commemorationes\./);
});

test('Vespers renders its own header and, with a translation requested, parallel German text', () => {
	const html = renderRite(loadFixture('vesperae-deutsch'), resources);
	assert.match(html, /Ad Vesperas\./);
	assert.match(html, /rite-text-translation">[^<]*[äöüÄÖÜß]/);
});

test('GABC chant items are rendered as gabc-chant elements carrying real, non-empty chant data', () => {
	const html = renderRite(loadFixture('matutinum-laudes-circumcisio'), resources);
	const chants = html.match(/<gabc-chant gabc="([^"]*)"/g) || [];
	assert.ok(chants.length > 0, 'expected at least one gabc-chant element');
	for (const chant of chants) {
		assert.doesNotMatch(chant, /gabc=""/, 'a gabc-chant element was rendered with empty chant data');
	}
});

test('the opening Deus in adjutorium chant is trimmed at its (Z) marker, dropping the Septuagesima alternate ending', () => {
	const html = renderRite(loadFixture('matutinum-laudes-circumcisio'), resources);
	const idx = html.indexOf('deus-in-adjutorium');
	assert.ok(idx !== -1, 'fixture is expected to contain a deus-in-adjutorium chant');
	const chantStart = html.lastIndexOf('<gabc-chant', idx);
	const chantEnd = html.indexOf('"', html.indexOf('gabc="', chantStart) + 'gabc="'.length);
	const gabc = html.slice(chantStart, chantEnd);
	assert.match(gabc, /Al\(h\)le\(i\)lú\(hg~\)ja/);
	assert.doesNotMatch(gabc, /\(Z-?\)/, 'the (Z) marker itself should have been trimmed off');
	assert.doesNotMatch(gabc, /Laus\(h\) ti\(h\)bi\(h\) Dó\(h\)mi\(h\)ne/, 'Septuagesima alternate ending should have been trimmed off');
});
