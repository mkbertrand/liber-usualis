# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.
#
# Python port of the Liang/TeX hyphenation pattern-matching algorithm used by
# the `hypher` npm package (https://github.com/bramstein/hypher), ported
# directly from its source rather than swapped for a different Python
# hyphenation library, so it consumes the exact same custom Latin pattern
# data (see la_hypher.py) this project already has tuned. Only the
# `hyphenate(word)` method is ported -- psalmify.js's hyphenateTextRight()
# does its own word splitting and never calls hypher's hyphenateText().

from typing import Any

# A node in the pattern trie: single-character keys map to child TrieNodes;
# the special key '_points' (when present) holds that node's hyphenation
# weights. Recursive, so typed loosely as dict[str, Any] rather than a
# self-referential TypedDict.
TrieNode = dict[str, Any]
Patterns = dict[str, str]

_DIGITS = frozenset('0123456789')
SOFT_HYPHEN = '­'


class Hyphenator:
    def __init__(self, patterns: Patterns, leftmin: int, rightmin: int) -> None:
        self.trie: TrieNode = _create_trie(patterns)
        self.left_min = leftmin
        self.right_min = rightmin

    def hyphenate(self, word: str) -> list[str]:
        if SOFT_HYPHEN in word:
            return [word]

        padded = '_' + word + '_'
        characters = list(padded.lower())
        original_characters = list(padded)
        word_length = len(characters)

        points = [0] * word_length

        for i in range(word_length):
            node: TrieNode | None = self.trie
            for j in range(i, word_length):
                node = node.get(characters[j])
                if node is None:
                    break
                node_points = node.get('_points')
                if node_points:
                    for k, value in enumerate(node_points):
                        # JS arrays auto-grow on out-of-bounds assignment and
                        # such entries are never read by the final loop below
                        # (which only visits indices up to word_length - 2),
                        # so skipping here matches that behavior exactly.
                        if i + k < word_length:
                            points[i + k] = max(points[i + k], value)

        result = ['']
        for i in range(1, word_length - 1):
            if self.left_min < i < (word_length - self.right_min) and points[i] % 2:
                result.append(original_characters[i])
            else:
                result[-1] += original_characters[i]
        return result


def _create_trie(pattern_object: Patterns) -> TrieNode:
    tree: TrieNode = {'_points': []}
    for size_key, blob in pattern_object.items():
        size = int(size_key)
        patterns = [blob[i:i + size] for i in range(0, len(blob), size)]
        for pattern in patterns:
            chars = [c for c in pattern if c not in _DIGITS]
            points = _split_on_nondigits(pattern)
            node = tree
            for char in chars:
                node = node.setdefault(char, {})
            node['_points'] = [int(p) if p else 0 for p in points]
    return tree


def _split_on_nondigits(pattern: str) -> list[str]:
    # Mirrors JS String.prototype.split(/\D/): splits at every non-digit
    # character, producing one segment per digit *slot* -- before the first
    # letter, between each pair of letters, and after the last.
    segments = []
    current = ''
    for ch in pattern:
        if ch in _DIGITS:
            current += ch
        else:
            segments.append(current)
            current = ''
    segments.append(current)
    return segments
