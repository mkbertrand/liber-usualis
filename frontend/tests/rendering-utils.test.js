// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';

import { dateHeader, riteTitle, abbreviateName, rubricRender, stringRender, tags, quaesitum, unpack, claw } from '../rite-renderer/rendering-utils.js';

test('dateHeader renders a Latin date, one-indexed month intact', () => {
	assert.equal(dateHeader('2001-01-14'), '<h4 class="date-header">Die 14 Januarii 2001.</h4>');
	assert.equal(dateHeader('2001-12-25'), '<h4 class="date-header">Die 25 Decembris 2001.</h4>');
});

test('riteTitle small size ignores rank tags', () => {
	assert.equal(riteTitle('Ad Vesperas', ['duplex-i-classis'], 'small'), '<h1 class="small-title">Ad Vesperas</h1>');
});

test('riteTitle large size derives a rank subtitle and avoids a doubled period', () => {
	const html = riteTitle('In Circumcisione D.N.J.C.', ['duplex-ii-classis']);
	assert.match(html, /<h1 class="large-title">In Circumcisione D\.N\.J\.C\.<\/h1>/);
	assert.match(html, /<h2 class="large-subtitle">Duplex II\. Classis\.<\/h2>/);
});

test('riteTitle appends the m.t.v. marker when present', () => {
	const html = riteTitle('Feria', ['feria', 'mtv']);
	assert.match(html, /Simplex\. \(m\.t\.v\.\)<\/h2>/);
});

test('abbreviateName abbreviates known epithets and collapses a doubled period', () => {
	assert.equal(abbreviateName('S. Felicis Presbyteri et Martyris'), 'S. Felicis Presbyteri et Mart.');
	assert.equal(abbreviateName('S. Priscæ Virginis et Martyris'), 'S. Priscæ Virg. et Mart.');
});

test('rubricRender wraps bracketed rubric text and converts a bare slash to a line break', () => {
	const html = rubricRender('[Orémus]/Fidélium');
	assert.equal(html, '<span class=\'black-rubric\'>Orémus</span><br>Fidélium');
});

test('rubricRender only flattens uppercase accented vowels, not lowercase', () => {
	assert.equal(rubricRender('ÓRÉMUS'), 'OREMUS');
	assert.equal(rubricRender('órémus'), 'órémus');
});

test('rubricRender colors liturgical marks', () => {
	assert.match(rubricRender('R. Amen.'), /<span class='red'>&#8479;\.<\/span>/);
	assert.match(rubricRender('V. Dominus vobiscum'), /^<span class='red'>&#8483;\.<\/span>/);
});

test('stringRender wraps a bracketed rubric span', () => {
	assert.equal(stringRender('[Orémus.]'), '<span class=\'rite-text-rubric\'>Orémus.</span>');
});

test('stringRender marks verse numbers and V./R. line starts', () => {
	const html = stringRender('9 Beáti immaculáti');
	assert.match(html, /<span class="verse-number">9 <\/span>/);
	assert.match(stringRender('V. Dómine, exáudi'), /^<span class="red line-starting-symbol">&#8483;\.<\/span>/);
});

test('tags reads an entry tag list as a Set and treats arrays/primitives as untagged', () => {
	assert.deepEqual(tags({ tags: ['ritus', 'matutinum'], datum: [] }), new Set(['ritus', 'matutinum']));
	assert.deepEqual(tags(['a', 'b']), new Set());
	assert.deepEqual(tags('plain string'), new Set());
});

test('quaesitum prefers an explicit quaesitum field but falls back to tags', () => {
	assert.deepEqual(quaesitum({ tags: ['ritus'], quaesitum: ['ritus', 'nocturna-i'], datum: [] }), new Set(['ritus', 'nocturna-i']));
	assert.deepEqual(quaesitum({ tags: ['ritus', 'matutinum'], datum: [] }), new Set(['ritus', 'matutinum']));
});

test('unpack recursively flattens nested datum objects and arrays down to strings', () => {
	assert.equal(unpack('Amen.'), 'Amen.');
	assert.equal(unpack(null), null);
	assert.deepEqual(unpack([{ datum: 'a' }, { datum: ['b', { datum: 'c' }] }]), ['a', 'b', 'c']);
});

test('claw digs through datum wrappers until it finds a string or array', () => {
	assert.equal(claw({ datum: { datum: { datum: 'Deo grátias.' } } }).datum, 'Deo grátias.');
	const arrayLeaf = { datum: { datum: ['a', 'b'] } };
	assert.equal(claw(arrayLeaf).datum, arrayLeaf.datum.datum);
});
