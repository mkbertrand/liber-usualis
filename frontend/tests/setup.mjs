// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

// The frontend targets browsers with the 2024 Set methods (Set.prototype.union,
// isSupersetOf, isDisjointFrom, etc.), which are newer than the Node.js version
// available in this repository's dev environment. This preload polyfills only
// the handful of methods rite-renderer.js actually calls, and only when the
// running Node lacks them, so tests can exercise the real frontend source
// without shipping a polyfill to the browser bundle.
if (!Set.prototype.union) {
	Set.prototype.union = function (other) {
		return new Set([...this, ...other]);
	};
}
if (!Set.prototype.isDisjointFrom) {
	Set.prototype.isDisjointFrom = function (other) {
		for (const item of this) {
			if (other.has(item)) return false;
		}
		return true;
	};
}
if (!Set.prototype.isSupersetOf) {
	Set.prototype.isSupersetOf = function (other) {
		for (const item of other) {
			if (!this.has(item)) return false;
		}
		return true;
	};
}
