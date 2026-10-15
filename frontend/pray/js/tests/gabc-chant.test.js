// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import exsurge from 'exsurge';
import { bindScoreToContext } from '../chant-context.js';

const Exsurge = exsurge.default ?? exsurge;

function makeScore(ctxt, gabc) {
	const mappings = Exsurge.Gabc.createMappingsFromSource(ctxt, gabc);
	const score = new Exsurge.ChantScore(ctxt, mappings, false);
	score.performLayout(ctxt);
	return score;
}

function firstNeumeStaffPosition(score, startIndex) {
	for (let i = startIndex; i < score.notations.length; i++) {
		if (score.notations[i].isNeume) return score.notations[i].notes[0].staffPosition;
	}
	return null;
}

test('chantLayout rebinds the shared context before laying out lines', () => {
	const src = readFileSync(fileURLToPath(new URL('../gabc-chant.js', import.meta.url)), 'utf8');
	assert.match(src, /bindScoreToContext\(GABC_CHANT_CONTEXT, this\.score\)/);
});

test('rebind keeps auto-custos on the first note of the next line after another score uses the context', () => {
	const ctxt = new Exsurge.ChantContext();
	const scoreA = makeScore(ctxt, '(c4) A(g)men.(h) (z) B(d)men.(e) (::)');
	const scoreB = makeScore(ctxt, '(c4) A(c)men.(c) (z) B(k)men.(k) (::)');

	scoreB.layoutChantLines(ctxt, 400);

	scoreA.layoutChantLines(ctxt, 400);
	const stale = scoreA.lines[0].custos.staffPosition;

	bindScoreToContext(ctxt, scoreA);
	scoreA.layoutChantLines(ctxt, 400);
	const rebound = scoreA.lines[0].custos.staffPosition;
	const nextLineStart = firstNeumeStaffPosition(scoreA, scoreA.lines[1].notationsStartIndex);

	assert.equal(rebound, nextLineStart);
	assert.notEqual(stale, rebound);
});
