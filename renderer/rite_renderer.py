# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.
#
# Python port of frontend/rite-renderer/rite-renderer.js. Ported as a
# stateful class closely mirroring the JS original -- see the "Renderer
# internal design" section of the approved plan for why (porting fidelity
# from a working, tested reference outweighs threading explicit state
# through ~20 call sites for no correctness benefit; this mirrors Python's
# own ast.NodeVisitor pattern for the same recursive-dispatch-with-shared-
# accumulator shape).
#
# Where the JS original mutates its input (element.datum.shift(),
# element.tags.push(...), reassigning element.datum/.cantus, etc.) this port
# works from local, rebound copies instead, per AGENTS.md's "avoid in-place
# mutation of caller-owned collections" -- the composed rite tree this
# consumes will eventually be cached, and in-place mutation would corrupt it
# for later cache hits.
#
# JS truthiness treats empty arrays/dicts as truthy (only None/''/0/False
# are falsy); Python treats empty containers as falsy. _truthy() below
# replicates JS semantics wherever a value that might be a list/dict (not
# just a plain flag or string) is checked in a boolean context.

import json
import re
from typing import Any, Callable, Optional, Union

from renderer.rendering_utils import (
    RiteNode,
    TagSet,
    abbreviate_name,
    date_header,
    rite_title,
    rubric_render,
    string_render,
    tags,
    quaesitum,
    unpack,
    claw,
)
from renderer.chomp import chomp
from renderer.psalmify import format_psalm

# The parallel-translation value threaded alongside an element through
# recurse_rite(): a single string, a list of per-sibling translations
# (recursively, the same shape as the element it accompanies), or absent.
Translation = Union[str, list, None]
Resources = dict[str, Any]

DIVED_ELEMENTS = ['aperi-domine', 'sacrosanctae', 'ritus', 'invitatorium', 'nocturna', 'psalmi', 'preces', 'collecta-primaria', 'antiphona-bmv']
FULLY_PARAGRAPHED_ELEMENTS = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'versiculus', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-dirigere', 'rubricum', 'hymnus', 'lectionis-titulum', 'evangelium-matutini', 'lectio-incipiens', 'lectio-sequens']
PARAGRAPH_CLOSING_ELEMENTS = ['gloria-versorum', 'terminatio']
PARAGRAPH_OPENING_ELEMENTS = ['capitulum', 'absolutio', 'pater-noster-clara-voce', 'pater-noster-semisecreta', 'credo-semisecreta', 'confiteor', 'oratio-sanctae-mariae', 'textus-psalmi-precibus', 'collecta']

_RESPONSORY_PREFIX = re.compile(r'^(?:R\.\sbr\.\s|R\.\s|V\.\s|)(.)')


def _json_default(value: Any) -> Any:
    # element.get('datum') can contain frozensets (this module works from
    # rite_request()'s raw Python objects, not JSON-round-tripped ones), which
    # json.dumps() doesn't know how to serialize on its own -- matches
    # composer/util.py's dump_data() convention of turning a set/frozenset of
    # strings into a plain list.
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def _js_empty_string_equals(value: Any) -> bool:
    # Mirrors JS's `x == ''` loose equality where x came from unpack(): true
    # for a literal empty string, or a list that stringifies to '' via
    # Array.prototype.join(',') -- an empty list, or a single-element list
    # holding only an empty string (JS's Array.join maps None/undefined
    # elements to '' too). None (JS null/undefined) is NOT == '' in JS.
    if isinstance(value, str):
        return value == ''
    if isinstance(value, list):
        return ','.join('' if v is None else v for v in value) == ''
    return False


def _truthy(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return value != ''
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _uppercase_responsory_prefix(line: str) -> str:
    match = _RESPONSORY_PREFIX.match(line)
    pref = match.group(0)
    return line.replace(pref, pref.upper().replace('BR', 'br'), 1)


def _at(seq: Optional[Union[str, list]], idx: int) -> Any:
    # JS array/string indexing returns undefined past the end (or before
    # the start via negative indices going further negative) rather than
    # raising -- relevant here because a lesson's translation array isn't
    # always the same length as the lesson's own segment array.
    if seq is None or not (0 <= idx < len(seq)):
        return None
    return seq[idx]


def _split_outside_brackets(text: str) -> list[str]:
    # Mirrors JS's /(?<!\]|\[[^\]]+?)\// -- a variable-width lookbehind
    # Python's re module can't express directly. Splits on '/' except when
    # immediately after ']' or while inside an unclosed '[...' span.
    parts = []
    current = ''
    in_bracket = False
    prev = ''
    for ch in text:
        if ch == '[':
            in_bracket = True
            current += ch
        elif ch == ']':
            in_bracket = False
            current += ch
        elif ch == '/' and not in_bracket and prev != ']':
            parts.append(current)
            current = ''
        else:
            current += ch
        prev = ch
    parts.append(current)
    return parts


class RiteRenderer:
    def __init__(self, resources: Resources) -> None:
        self.rite: list[str] = []
        self.left_buffer: list[str] = []
        self.right_buffer: list[str] = []
        self.open_divs: list[str] = []
        self.paragraph_open: bool = False
        self.antiphon_mode: Optional[str] = None
        self.antiphon_clef: Optional[str] = None
        self.paragraph_style: str = ''
        self.resources = resources

    def _emit(self, html: str) -> None:
        self.rite.append(html)

    def close_paragraph(self) -> None:
        if self.paragraph_open and len(self.left_buffer) == 0:
            self.paragraph_open = False
        elif self.paragraph_open:
            self.paragraph_open = False
            left_column = '<br>'.join(self.left_buffer)
            right_column = '<br>'.join(self.right_buffer)
            self._emit(f'<div class="rite-text-container {self.paragraph_style}"><p class="rite-text rite-text-latin">{left_column}</p><p class="rite-text rite-text-translation">{right_column}</p></div>')
            self.left_buffer = []
            self.right_buffer = []

    def open_div(self, style: str, name: str) -> None:
        self.close_paragraph()
        self._emit(f'<div class="rite-item {style} {name}">')
        self.open_divs.append(name)

    def close_div(self) -> None:
        self.open_divs.pop()
        self.close_paragraph()
        self._emit('</div>')

    def open_paragraph(self, style: str) -> None:
        self.close_paragraph()
        self.paragraph_open = True
        self.paragraph_style = style

    def make_centered_header(self, header: str, style: str = 'item-header') -> None:
        self.close_paragraph()
        self._emit(f'<h4 class="centered-header {style}">{rubric_render(header)}</h4>')

    def make_heading_annotation(self, annot: str) -> None:
        self.close_paragraph()
        self._emit(f'<p class="rite-text-rubric rite-text-rubric-above-paragraph">{annot}</p>')

    def append_text(self, text: str, translation: Translation = None) -> None:
        if not _truthy(translation):
            translation = ''
        self.left_buffer.append(string_render(text))
        self.right_buffer.append(string_render(translation))

    def render_gabc(
        self,
        replaced: RiteNode,
        quaesitum_tags: TagSet,
        cantus: RiteNode,
        translation: Translation,
        tag_set: TagSet,
    ) -> None:
        self.open_div('', 'gabc-chant-container')
        self.open_div('', 'gabc-chant')
        cantus_unpack = unpack(cantus)
        if not _truthy(translation):
            translation_string = ''
        elif isinstance(translation, str):
            translation_string = translation
        elif isinstance(translation, list):
            translation_string = re.sub(r'\sV\.', " <span class='red'>&#8483;.</span>", ' '.join(translation))
        else:
            translation_string = ''
        self._emit(f'<gabc-chant gabc="{chomp(cantus_unpack, quaesitum_tags, self.resources)}" translated="{translation_string}"><div class="chantelement-text-content">')
        self.open_paragraph(' '.join(tag_set))
        self.recurse_rite(replaced, translation, tag_set)
        self.close_paragraph()
        self._emit('</div></gabc-chant>')
        self.close_div()
        self.close_div()

    def do_headering(self, element: RiteNode, uniquelyhas: Callable[[str], bool]) -> None:
        # Apply headers (added during a superimposition step) where relevant.
        caput = element.get('caput') if isinstance(element, dict) else None
        if _truthy(caput) and any(t not in ('caput', 'sectio', 'annotatio') and uniquelyhas(t) for t in tags(caput)):
            header = unpack(caput)
            if not _truthy(header) or isinstance(header, list):
                return
            caput_tags = tags(caput)
            if 'annotatio' in caput_tags:
                self.make_heading_annotation(abbreviate_name(header))
            elif 'sectio' in caput_tags:
                self.make_centered_header(header, 'section-header')
            else:
                self.make_centered_header(header)

    def try_hymn(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = tags(element)

        def uniquely_has_bottom(tag: str) -> bool:
            return tag in element_tags and tag not in tags(element.get('datum'))

        if not uniquely_has_bottom('hymnus') or 'te-deum' in element_tags:
            return False

        unpacked = unpack(element)
        if isinstance(unpacked, str) and unpacked.startswith('['):
            self.append_text(unpacked)
            return True

        self.open_div('', 'hymnus')

        cantus = element.get('cantus')
        working_element = element
        if _truthy(cantus):
            datum = element['datum']
            self.render_gabc(datum[0], quaesitum(element), cantus, translation, parent_tags | element_tags)
            working_element = {**element, 'datum': datum[1:]}

        for i in unpack(working_element):
            self.open_paragraph('hymnus')
            self.append_text(i)
        self.close_div()
        return True

    def try_responsory(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = tags(element)
        if not (('responsorium' in element_tags or 'responsorium-breve' in element_tags) and isinstance(element.get('datum'), list)):
            return False

        datum = element['datum']

        if isinstance(datum[1], str):
            self.open_paragraph(' '.join(element_tags))
            self.append_text(datum[1].replace(", 'incipit'", ''))
            self.close_paragraph()
            return True

        if _truthy(translation):
            trans = unpack(translation)
            all_defined = True
            for i in range(len(trans)):
                if not _truthy(trans[i]):
                    resp = claw(datum[i])
                    if 'translation' in resp:
                        trans[i] = unpack(resp['translation'])
                    if trans[i] is None:
                        all_defined = False
                        break
            translation = [_uppercase_responsory_prefix(line) for line in ''.join(trans).split('\n')] if all_defined else None

        cantus = element.get('cantus')
        if _truthy(cantus):
            trans = unpack(cantus)
            all_defined = True
            for i in range(len(trans)):
                if trans[i] is None:
                    resp = claw(datum[i])
                    if 'cantus' in resp:
                        trans[i] = unpack(resp['cantus'])
                    if trans[i] is None:
                        all_defined = False
                        break
                else:
                    trans[i] = unpack(trans[i])
            cantus = ''.join(trans) if all_defined else None

        new_datum = [_uppercase_responsory_prefix(line) for line in ''.join(unpack(datum)).split('\n')]

        if _truthy(cantus):
            self.render_gabc(new_datum, quaesitum(element), cantus, translation, parent_tags | element_tags)
            return True

        self.open_paragraph(' '.join(element_tags))
        # We're ok with nested responsories.
        self.recurse_rite(new_datum, translation, parent_tags | element_tags)
        self.close_paragraph()
        return True

    def try_chant(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        if (
            'gabc-chant-container' in self.open_divs
            or not isinstance(element, dict)
            or 'cantus' not in element
            or element.get('cantus') is None
            or (
                not quaesitum(element).isdisjoint({'antiphona', 'hymnus'})
                and '"cantus"' in json.dumps(element.get('datum'), ensure_ascii=False, default=_json_default)
            )
        ):
            return False
        self.render_gabc(element['datum'], quaesitum(element), element['cantus'], translation, parent_tags | tags(element))
        return True

    def try_psalmify(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = element.get('tags') or ()
        if '/psalmi/' not in ' '.join(element_tags):
            return False

        formatted = format_psalm(element['datum'], self.resources, self.antiphon_mode, self.antiphon_clef)
        self.make_heading_annotation(formatted.split('\n')[0][1:-1])
        new_datum = re.sub(r'^\[.+?]\n\d+\s', '', formatted, count=1).split('\n')

        if _truthy(translation):
            translation = re.sub(
                r'\[.+?]\n', '\n',
                re.sub(r'^\[.+?]\n\d+\s', '', format_psalm(unpack(translation)), count=1),
            ).split('\n')

        extra_tag = 'textus-psalmi-precibus' if 'preces' in parent_tags else 'textus-psalmi'
        # Mirrors JS's element.tags.push(extraTag): append, don't reorder.
        new_element = {**element, 'tags': tuple(element_tags) + (extra_tag,)}

        self.recurse_rite(new_datum, translation, parent_tags | tags(new_element))
        return True

    def try_lesson(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = tags(element)

        def uniquely_has_bottom(tag: str) -> bool:
            return tag in element_tags and tag not in tags(element.get('datum'))

        if not uniquely_has_bottom('lectio') or 'commemoratio-matutini' in tags(element.get('datum')):
            return False

        lesson = unpack(element)
        if not _truthy(translation):
            datum = element.get('datum') if isinstance(element, dict) else None
            if isinstance(datum, dict) and 'translation' in datum:
                translation = unpack(datum['translation'])
            elif isinstance(lesson, list):
                translation = [''] * len(lesson)

        element_quaesitum = quaesitum(element)

        # For the Lamentations of the Sacred Triduum.
        if element_quaesitum.issuperset({'sabbatum-sanctum', 'nocturna-i', 'lectio-iii'}):
            self.open_paragraph('lectionis-titulum')
            self.append_text(lesson[0])
            self.close_paragraph()
            self.open_paragraph('lectio-sequens')
            self.recurse_rite(lesson[1] + '/' + lesson[2], None, parent_tags | element_tags | {'lectio-sequens'})
            self.close_paragraph()
            return True
        elif element_quaesitum.issuperset({'triduum', 'nocturna-i'}):
            if 'lectio-i' in element_quaesitum:
                self.open_paragraph(f"lectionis-titulum {' '.join(element.get('tags') or ())}")
                self.append_text(lesson[0])
                self.close_paragraph()
                lesson = lesson[1:]
            annotation = re.match(r'^\[.+?\]/', lesson[0])
            if annotation:
                self.make_heading_annotation(annotation.group(0)[1:-2])
                lesson = [re.sub(r'^\[.+?\]/', '', lesson[0], count=1)] + lesson[1:]
            body = '<br>'.join(
                re.sub(r'^(.)(.+?\.\s)(.)', r'<span class="red">\1</span>\2<span class="red">\3</span>', string_render(i))
                for i in lesson[:-1]
            ) + '<br>' + re.sub(r'^(.)', r'<span class="red">\1</span>', lesson[-1])
            self.open_paragraph('lectio-sequens')
            self.append_text(body)
            self.close_paragraph()
            return True

        datum = element.get('datum')
        if isinstance(datum, list) and all('lectio' in tags(item) for item in datum):
            translation = unpack([item.get('translation') if isinstance(item, dict) and 'translation' in item else None for item in datum])
        else:
            translation = unpack(translation)

        # For the first lesson from a Homily.
        if isinstance(lesson, list) and len(lesson[0]) < 100 and 'Evangélii' in lesson[0]:
            self.open_paragraph('lectionis-titulum')
            self.recurse_rite(lesson[0], _at(translation, 0), parent_tags | element_tags | {'lectionis-titulum'})
            self.close_paragraph()
            self.recurse_rite(lesson[1], _at(translation, 1), TagSet({'evangelium-matutini'}))
            self.open_paragraph('lectionis-titulum')
            self.recurse_rite(lesson[2], _at(translation, 2), parent_tags | element_tags | {'lectionis-titulum'})
            rest = [seg if i == 0 else re.sub(r'\]/', '] ', seg, count=1) for i, seg in enumerate(lesson[3:])]
            rest_translation = ' &para; '.join(translation[3:]) if isinstance(translation, list) and _truthy(translation[3] if len(translation) > 3 else None) else None
            self.recurse_rite(' &para; '.join(rest), rest_translation, TagSet({'lectio-incipiens'}))
        # Cheeky heuristic to guess if the first item is a title or if this lesson is really some conjoined lessons.
        elif isinstance(lesson, list) and len(lesson[0]) < 100:
            self.open_paragraph('lectionis-titulum')
            self.recurse_rite(lesson[0], _at(translation, 0), parent_tags | element_tags | {'lectionis-titulum'})
            self.close_paragraph()
            rest_translation = ' &para; '.join(translation[1:]) if isinstance(translation, list) and len(translation) > 1 and _truthy(translation[1]) else None
            tag = 'lectio-incipiens' if 'lectio-i' in element_tags else 'lectio-sequens'
            self.recurse_rite(' &para; '.join(lesson[1:]), rest_translation, TagSet({tag}))
        # Note that an untitled lesson may still be a first lesson. This is due to the fact that most Saints lives are begun without title.
        else:
            if isinstance(lesson, list):
                joined_translation = None
                if isinstance(translation, list) and _truthy(translation[0] if translation else None):
                    joined_translation = ' &para; '.join(translation)
                lesson = ' &para; '.join(lesson)
                translation = joined_translation
            self.close_paragraph()
            tag = 'lectio-incipiens' if 'lectio-i' in element_tags else 'lectio-sequens'
            self.recurse_rite(lesson, translation, TagSet({tag}))
        return True

    def try_commemorations(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = tags(element)
        if 'commemorationes' not in element_tags:
            return False
        datum = element['datum']
        for i in range(len(datum) - 1):
            self.open_div('', 'formula-commemorationis')
            self.recurse_rite(datum[i], translation, parent_tags | element_tags)
            if i != len(datum) - 2:
                self.close_div()
        self.recurse_rite(datum[-1], translation, parent_tags | element_tags)
        self.close_div()
        return True

    def try_martyrology(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        if 'martyrologium' not in tags(element):
            return False
        datum = element['datum']
        self.open_paragraph('martyrologium')
        self.append_text(unpack(datum[0]) + ' ' + unpack(datum[1]))
        prae = unpack(datum[2])
        if not _js_empty_string_equals(prae):
            self.open_paragraph('martyrologium')
            self.append_text(prae)
        martyrology = unpack(datum[3])
        if isinstance(martyrology, str):
            self.open_paragraph('martyrologium')
            self.append_text(martyrology)
        else:
            for i in unpack(datum[3]):
                self.open_paragraph('martyrologium')
                self.append_text(i)
        self.open_paragraph('martyrologium')
        self.append_text(unpack(datum[4]))
        self.append_text(unpack(datum[5]))
        self.close_paragraph()
        return True

    def try_invitatory(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> bool:
        element_tags = tags(element)
        if 'invitatorium' not in element_tags:
            return False
        self.open_div('', 'invitatorium')
        datum = element['datum']
        # The first instance of the Invitatory antiphon has to be rendered first in order to define antiphonMode.
        self.recurse_rite(datum[0], translation[0] if _truthy(translation) else None, parent_tags | element_tags)
        inv_index = 0
        invitatorium = self.resources.get('invitatoria', {}).get(self.antiphon_mode)
        for i in range(1, len(datum)):
            if isinstance(datum[i], dict):
                self.recurse_rite(datum[i], translation[i] if _truthy(translation) else None, parent_tags | element_tags)
            elif invitatorium:
                self.render_gabc(datum[i], quaesitum(element), invitatorium[inv_index], translation[i] if _truthy(translation) else None, parent_tags)
                inv_index += 1
            else:
                self.recurse_rite(datum[i], translation[i] if _truthy(translation) else None, parent_tags | element_tags)
        self.close_div()
        return True

    def recurse_rite(self, element: RiteNode, translation: Translation, parent_tags: TagSet) -> None:
        # Sometimes an element will have the same kind of thing nested in it recursively. For example, a collecta item may actually be a call to a different day's collecta. In this case, only return true if it's the outer.
        def uniquelyhas(tag: str, tagset: Optional[TagSet] = None) -> bool:
            tagset = tagset if tagset is not None else tags(element)
            return tag in tagset and tag not in parent_tags

        if isinstance(element, dict) and 'translation' in element:
            translation = unpack(element['translation'])

        # Manages splitting up strings that include line breaks so that the translation is divided properly.
        # Splits lines denoted by /, but ignores </ (pre-formatted html indicator) or ]/ (annotation).
        if isinstance(element, str) and re.search(r'(?<!\]|<)/', element):
            element = re.split(r'(?<!\]|<)/', element)
            if _truthy(translation):
                translation = _split_outside_brackets(translation)

        if isinstance(element, list):
            for i in range(len(element)):
                # For some rubric texts, they're whole lines.
                if isinstance(element[i], str) and re.match(r'^\[.+?/\]$', element[i]):
                    self.make_heading_annotation(rubric_render(element[i][1:-2]))
                else:
                    sub_translation = translation[i] if isinstance(translation, list) and len(translation) == len(element) else None
                    self.recurse_rite(element[i], sub_translation, parent_tags)
            return
        elif isinstance(element, str):
            annot = re.match(r'^\[(.+?)\]/', element)
            if annot:
                annot_text = annot.group(1)
                if 'capitulum' in parent_tags:
                    annot_text = 'Capitulum. ' + annot_text
                self.make_heading_annotation(rubric_render(annot_text))
                element = element.replace(annot.group(0), '', 1)
            if not self.paragraph_open:
                self.open_paragraph(' '.join(parent_tags))
            # Idk man
            if isinstance(translation, list):
                translation = None
            self.append_text(element, translation)
            return

        # These checks are done before removing empty items since empty antiphons can still confer tone upon the following Psalms.
        if 'antiphona' in tags(element) and 'cantus' in element and _truthy(element.get('cantus')):
            cantus_unpacked = unpack(element['cantus'])
            mode_match = re.search(r'mode:(.+?)(?:;|\n)', cantus_unpacked)
            clef_match = re.search(r'^\((.+?)\)', cantus_unpacked.replace('%%', '\n%%\n'), re.MULTILINE)
            if mode_match and clef_match and 'repetita' not in quaesitum(element):
                self.antiphon_mode = mode_match.group(1)
                self.antiphon_clef = clef_match.group(1)
            else:
                self.antiphon_mode = None
                self.antiphon_clef = None

        if _js_empty_string_equals(unpack(element)):
            return

        self.do_headering(element, uniquelyhas)
        if self.try_hymn(element, translation, parent_tags):
            return
        if self.try_responsory(element, translation, parent_tags):
            return
        if self.try_commemorations(element, translation, parent_tags):
            return
        if self.try_chant(element, translation, parent_tags):
            return
        if self.try_psalmify(element, translation, parent_tags):
            return
        if self.try_lesson(element, translation, parent_tags):
            return
        if self.try_martyrology(element, translation, parent_tags):
            return
        if self.try_invitatory(element, translation, parent_tags):
            return

        for name in DIVED_ELEMENTS:
            if uniquelyhas(name):
                self.open_div('', name)
                self.recurse_rite(element.get('datum'), translation, parent_tags | tags(element))
                self.close_div()
                return
        for name in FULLY_PARAGRAPHED_ELEMENTS:
            if uniquelyhas(name) and 'dominus-det' not in tags(element):
                self.open_paragraph(' '.join(tags(element) | parent_tags))
                self.recurse_rite(element.get('datum'), translation, parent_tags | tags(element))
                self.close_paragraph()
                return
        for name in PARAGRAPH_CLOSING_ELEMENTS:
            if uniquelyhas(name):
                self.recurse_rite(element.get('datum'), translation, parent_tags | tags(element))
                self.close_paragraph()
                return
        for name in PARAGRAPH_OPENING_ELEMENTS:
            if uniquelyhas(name):
                self.open_paragraph(' '.join(tags(element) | parent_tags))
                self.recurse_rite(element.get('datum'), translation, parent_tags | tags(element))
                return
        self.recurse_rite(element.get('datum'), translation, parent_tags | tags(element))


def render_rite(date: str, rite: dict[str, Any], resources: Resources) -> str:
    # dateHeader() and riteTitle() are never called except immediately
    # before renderRite() (see pray-window.js's getRite()), so that
    # orchestration lives here rather than being left for every caller to
    # repeat.
    renderer = RiteRenderer(resources)
    renderer.recurse_rite(rite['text'], None, TagSet())
    title, title_tags = rite['used-primary']
    return date_header(date) + rite_title(title, title_tags, 'large') + ''.join(renderer.rite)
