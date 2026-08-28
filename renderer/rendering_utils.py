# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

# Python port of frontend/rite-renderer/rendering-utils.js. Behavior (including
# the small quirks noted inline) is kept identical to the JS original rather
# than "corrected", since this is a faithful port being verified against the
# existing JS renderer's golden output.

import re
from typing import Any, Union

# A composed rite tree node: a literal string leaf, a list of sibling nodes,
# a dict node ({'tags', 'datum', 'quaesitum'?, 'cantus'?, 'caput'?,
# 'translation'?}), or absent/None.
RiteNode = Union[str, list, dict, None]


# TEMPORARY, for testing: stands in for plain frozenset as the TagSet
# representation. A plain frozenset's iteration order is CPython's internal
# hash-bucket order, unrelated to insertion order; the JS original combines
# tags with a `Set`, whose `.union()` (see the ES2024 polyfill in
# frontend/tests/setup.mjs) deterministically preserves the receiver's
# existing order followed by the argument's new-only elements in the
# argument's order. Since several places in rite_renderer.py join a TagSet
# directly into a `class="..."` HTML attribute, the hash-order mismatch was
# producing systematically different (though functionally inert) class
# token order from the JS renderer on every rendered rite. TagSet replicates
# frozenset's interface (membership, isdisjoint, issuperset, union via `|`)
# while preserving JS Set.union's ordering semantics, so `class="..."`
# output can be verified byte-for-byte against the JS renderer.
class TagSet:
    __slots__ = ('_order', '_members')

    def __init__(self, iterable: Any = ()) -> None:
        order: list[str] = []
        members: set = set()
        for item in iterable:
            if item not in members:
                members.add(item)
                order.append(item)
        self._order: tuple = tuple(order)
        self._members: frozenset = frozenset(members)

    def __iter__(self):
        return iter(self._order)

    def __contains__(self, item: Any) -> bool:
        return item in self._members

    def __len__(self) -> int:
        return len(self._order)

    def __bool__(self) -> bool:
        return bool(self._order)

    def __or__(self, other: Any) -> 'TagSet':
        return TagSet(self._order + tuple(other))

    def __ror__(self, other: Any) -> 'TagSet':
        return TagSet(tuple(other) + self._order)

    def isdisjoint(self, other: Any) -> bool:
        return self._members.isdisjoint(other)

    def issuperset(self, other: Any) -> bool:
        return self._members.issuperset(other)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TagSet):
            return self._members == other._members
        try:
            return self._members == frozenset(other)
        except TypeError:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self._members)

    def __repr__(self) -> str:
        return f'TagSet({self._order!r})'

MONTHS = ['Januarii', 'Februarii', 'Martii', 'Aprilis', 'Maji', 'Junii', 'Julii', 'Augusti', 'Septembris', 'Octobris', 'Novembris', 'Decembris']


def date_header(date: str) -> str:
    year, month, day = date.split('-')
    return f'<h4 class="date-header">Die {int(day)} {MONTHS[(int(month) - 1) % 12]} {year}.</h4>'


def rite_title(title: str, tagset: TagSet, size: str = 'large') -> str:
    if size == 'small':
        return f'<h1 class="small-title">{title}</h1>'

    if 'duplex-i-classis' in tagset:
        subtitle = 'Duplex I. Classis.'
    elif 'duplex-ii-classis' in tagset:
        subtitle = 'Duplex II. Classis.'
    elif 'duplex-majus' in tagset:
        subtitle = 'Duplex Majus.'
    elif 'duplex-minus' in tagset:
        subtitle = 'Duplex Minus.'
    elif 'semiduplex' in tagset:
        subtitle = 'Semiduplex.'
    elif 'simplex' in tagset or 'feria' in tagset:
        subtitle = 'Simplex.'
    else:
        subtitle = ''

    if 'mtv' in tagset:
        subtitle += ' (m.t.v.)'

    title_text = re.sub(r'\.\.$', '.', title + '.')
    return f'<h1 class="large-title">{title_text}</h1><h2 class="large-subtitle">{subtitle}</h2>'


_ABBREVIATIONS = (
    ('Martyris', 'Mart.'),
    ('Martyrum', 'Mm.'),
    ('Confessoris', 'Conf.'),
    ('Episcopi', 'Ep.'),
    ('Pontificum', 'Pont.'),
    ('Ecclesiæ Doctoris', 'Eccl. Doct.'),
    ('Virginis', 'Virg.'),
    ('Viduæ', 'Vid.'),
    ('Sociorum', 'Soc.'),
)


def abbreviate_name(name: str) -> str:
    for full, short in _ABBREVIATIONS:
        name = name.replace(full, short)
    name = name + '.'
    name = re.sub(r'\.\.$', '.', name)
    return name


_ACCENT_FLATTEN = (('Á', 'A'), ('Ǽ', 'Æ'), ('É', 'E'), ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U'), ('Ý', 'Y'))


def _flatten_uppercase_accents(text: str) -> str:
    for accented, plain in _ACCENT_FLATTEN:
        text = text.replace(accented, plain)
    return text


def rubric_render(data: str) -> str:
    data = re.sub(r'\[(.+?)\]', r"<span class='black-rubric'>\1</span>", data)
    data = _flatten_uppercase_accents(data)
    data = re.sub(r'(?<!<)/', '<br>', data)
    data = re.sub(r'\n', '<br>', data)
    data = re.sub(r'&para;', "<span class='red'>&para;</span>", data)
    data = re.sub(r'N\.', "<span class='red'>N.</span>", data)
    # Trailing "." here is an unescaped regex wildcard in the JS original
    # (matches "R. br" + any one character), not a literal period -- kept
    # as-is for faithful parity rather than "fixed".
    data = re.sub(r'R\. br.', "<span class='red'>&#8479;. br.</span>", data)
    data = re.sub(r'R\.', "<span class='red'>&#8479;.</span>", data)
    data = re.sub(r'^V\.', "<span class='red'>&#8483;.</span>", data)
    data = re.sub(r'>V\.', "<br><span class='red'>&#8483;.</span>", data)
    data = data.replace('✠', "<span class='red'>&malt;</span>")
    data = data.replace('✙', "<span class='red'>&#10009;</span>")
    data = data.replace('+', "<span class='red'>&dagger;</span>")
    data = data.replace('*', "<span class='red'>&ast;</span>")
    return data


def string_render(text: str) -> str:
    if re.fullmatch(r'\[.+?\]', text):
        return f"<span class='rite-text-rubric'>{rubric_render(text[1:-1])}</span>"

    text = _flatten_uppercase_accents(text)
    text = re.sub(r'(?<!<)/', '<br>', text)
    text = re.sub(r'([0-9]+)\s', r'<span class="verse-number">\1 </span>', text)
    text = re.sub(r'\n', '<br>', text)
    text = re.sub(r'^V\.', '<span class="red line-starting-symbol">&#8483;.</span>', text)
    # See rubric_render: trailing "." is an unescaped wildcard, kept for parity.
    text = re.sub(r'^R\. br.', '<span class="red line-starting-symbol">&#8479;. br.</span>', text)
    text = re.sub(r'^R\.', '<span class="red line-starting-symbol">&#8479;.</span>', text)
    text = re.sub(r'&para;', "<span class='red'>&para;</span>", text)
    text = re.sub(r'N\.', "<span class='red'>N.</span>", text)
    text = re.sub(r'R\.', "<span class='red'>&#8479;.</span>", text)
    text = re.sub(r'<br>V\.', "<br><span class='red'>&#8483;.</span>", text)
    text = text.replace('✠', "<span class='red'>&malt;</span>")
    text = text.replace('✙', "<span class='red'>&#10009;</span>")
    text = text.replace('+', "<span class='red'>&dagger;</span>")
    text = text.replace('*', "<span class='red'>&ast;</span>")
    text = re.sub(r'\[\((.+?)\)\]\s', r"<span class='rite-text-rubric small-rubric'>(\1) </span>", text)
    text = re.sub(r'\[(.+?)\]', r"<span class='rite-text-rubric'>\1</span>", text)
    return text


def tags(element: RiteNode) -> TagSet:
    if isinstance(element, dict):
        return TagSet(element.get('tags') or ())
    return TagSet()


def quaesitum(element: RiteNode) -> TagSet:
    if isinstance(element, dict) and 'quaesitum' in element:
        return TagSet(element['quaesitum'])
    return tags(element)


# It can be readily observed that this is just an extremely primitive version of render_rite().
def unpack(data: RiteNode) -> Union[str, list, None]:
    if isinstance(data, str):
        return data
    if data is None:
        return None
    if isinstance(data, list):
        result: list[Any] = []
        for item in data:
            unpacked = unpack(item)
            if isinstance(unpacked, list):
                result.extend(unpacked)
            else:
                result.append(unpacked)
        return result
    if isinstance(data, dict):
        return unpack(data.get('datum'))
    return None


# Digs out nested data recursively (useful for translation).
def claw(data: dict) -> dict:
    datum = data.get('datum')
    if isinstance(datum, str) or isinstance(datum, list):
        return data
    return claw(datum)
