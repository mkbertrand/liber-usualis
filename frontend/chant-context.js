// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

export function bindScoreToContext(ctxt, score) {
  ctxt.notations = score.notations;
  ctxt.staffLineCount = score.staffLineCount;
}
