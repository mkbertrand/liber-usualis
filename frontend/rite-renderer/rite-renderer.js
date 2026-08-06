// Copyright 2024-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import {abbreviateName, rubricRender, stringRender, tags, quaesitum, unpack, claw} from './rendering-utils.js';

import {chomp} from './chomp.js';
import {formatPsalm} from './psalmify.js';

const RITE_HEADERS = {
	'matutinum': 'Ad Matutinum.',
	'laudes': 'Ad Laudes.',
	'prima': 'Ad Primam.',
	'tertia': 'Ad Tertiam.',
	'sexta': 'Ad Sextam.',
	'nona': 'Ad Nonam.',
	'vesperae': 'Ad Vesperas.',
	'completorium': 'Ad Completorium.',
	'psalmi-graduales': 'Psalmi Graduales.',
	'psalmi-poenitentiales': 'Septem Psalmi Pœnitentiales [cum Litaniis.]',
	'litaniae-sanctorum': 'Litaniæ Sanctorum.',
	'ordo-commendationis-animae': 'Ordo Commendationis Animæ.',
	'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenarium in Articulo Mortis.',
	'pro-prandio': 'Benedictio Mensæ.',
	'pro-coena': 'Benedictio Mensæ.',
	'itinerarium': 'Itinerarium Clericorum.',
	'officium-capituli': 'Martyrologium.'
};

const DIVED_ELEMENTS = ['aperi-domine', 'sacrosanctae', 'ritus', 'invitatorium', 'nocturna', 'psalmi', 'preces', 'collecta-primaria', 'antiphona-bmv'];
const FULLY_PARAGRAPHED_ELEMENTS = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'versiculus', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-dirigere', 'rubricum', 'hymnus', 'lectionis-titulum', 'evangelium-matutini', 'lectio-incipiens', 'lectio-sequens'];
const PARAGRAPH_CLOSING_ELEMENTS = ['gloria-versorum', 'terminatio'];
const PARAGRAPH_OPENING_ELEMENTS = ['capitulum', 'absolutio', 'pater-noster-clara-voce', 'pater-noster-semisecreta', 'credo-semisecreta', 'confiteor', 'oratio-sanctae-mariae', 'textus-psalmi-precibus', 'collecta'];

const NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'];

class RiteRenderer {
  
  constructor(structuredRite, resources) {
    this.usedCommemorations = structuredRite['used-commemorations'];
    this.matinsCommemoration = structuredRite['commemoratio-matutini'] ? structuredRite['commemoratio-matutini'][0] : null;
    
    this.rite = '';
    this.leftBuffer = [];
    this.rightBuffer = [];
    this.openDivs = [];
    this.paragraphOpen = false;
    this.antiphonMode = null;
    this.antiphonClef = null;
    this.paragraphStyle = '';
    this.resources = resources;
  }

  closeParagraph() {
    if (this.paragraphOpen && this.leftBuffer.length == 0) {
      this.paragraphOpen = false;
    } else if (this.paragraphOpen) {
      this.paragraphOpen = false;
      let leftColumn = this.leftBuffer.join('<br>');
      let rightColumn = this.rightBuffer.join('<br>');
      this.rite += `<div class="rite-text-container ${this.paragraphStyle}"><p class="rite-text rite-text-latin">${leftColumn}</p><p class="rite-text rite-text-translation">${rightColumn}</p></div>`;
      this.leftBuffer = [];
      this.rightBuffer = [];
    }
  }

  openDiv(style, name) {
    this.closeParagraph();
    this.rite += `<div class="rite-item ${style} ${name}">`;
    this.openDivs.push(name);
  }

  closeDiv(name) {
    this.openDivs.pop();
    this.closeParagraph();
    this.rite += '</div>';
  }

  openParagraph(style) {
    this.closeParagraph();
    this.paragraphOpen = true;
    this.paragraphStyle = style;
  }

  makeCenteredHeader(header, style = 'item-header') {
    this.closeParagraph();
    this.rite += `<h4 class="centered-header ${style}">${rubricRender(header)}</h4>`;
  }

  makeHeadingAnnotation(annot) {
    this.closeParagraph();
    this.rite += `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${annot}</p>`;
  }

  appendText(text, translation = null) {
    if (!translation) {
      translation = '';
    }
    this.leftBuffer.push(stringRender(text));
    this.rightBuffer.push(stringRender(translation));
  }

  renderGabc(replaced, quaesitum, cantus, translation = null, tags) {
    this.openDiv('', 'gabc-chant-container');
    this.openDiv('', 'gabc-chant');
    let cantusUnpack = unpack(cantus);
    if (!translation) {
      var translationString = '';
    } else if (typeof translation === 'string') {
      var translationString = translation;
    } else if (Array.isArray(translation)) {
      var translationString = translation.join(' ').replace(/\sV\./g, ' <span class=\'red\'>&#8483;.</span>');
    }
    this.rite += `<gabc-chant gabc="${chomp(cantusUnpack, quaesitum, this.resources)}" translated="${translationString}">`;
    this.openParagraph([...tags].join(' '));
    this.recurseRite(replaced, translation, tags);
    this.closeParagraph();
    this.rite += '</gabc-chant>';
    this.closeDiv('', 'gabc-chant');
    this.closeDiv('gabc-chant-container');
  }

  doHeadering(element, parentTags, uniquelyhas) {
    if (quaesitum(element).isSupersetOf(new Set(['nocturna', 'nocturna-i']))) {
      this.makeCenteredHeader('Nocturnus I.', 'section-header');
    } else if (quaesitum(element).isSupersetOf(new Set(['nocturna', 'nocturna-ii']))) {
      this.makeCenteredHeader('Nocturnus II.', 'section-header');
    } else if (quaesitum(element).isSupersetOf(new Set(['nocturna', 'nocturna-iii']))) {
      this.makeCenteredHeader('Nocturnus III.', 'section-header');
    } else if (tags(element).has('nocturna')) {
        this.makeCenteredHeader('Nocturnus.', 'section-header');
    } else if (tags(element).isSupersetOf(new Set(['ritus', 'antiphona-bmv']))) {
        this.makeCenteredHeader('Antiphona B.M.V.');
    } else if (tags(element).has('ritus')) {
      for (let header in RITE_HEADERS) {
        if (uniquelyhas(header)) {
          this.makeCenteredHeader(RITE_HEADERS[header], 'section-header');
        }
      }
    } else if (uniquelyhas('psalmi')) {
      this.makeCenteredHeader('Psalmi.');
    } else if (uniquelyhas('collecta-primaria')) {
      this.makeCenteredHeader('Collecta.');
    } else if (uniquelyhas('invitatorium')) {
      this.makeCenteredHeader('Invitatorium.');
    } else if (uniquelyhas('haec-dies')) {
      this.makeCenteredHeader('Antiphona.');
    } else if (uniquelyhas('commemorationes')) {
      this.makeCenteredHeader('Commemorationes.');
    } else if (tags(element).isSupersetOf(new Set(['benedictio-mensae', 'ante-prandium']))) {
      this.makeCenteredHeader('[Ante Prandium.]');
    } else if (tags(element).isSupersetOf(new Set(['benedictio-mensae', 'post-prandium']))) {
      this.makeCenteredHeader('[Post Prandium.]');
    } else if (tags(element).isSupersetOf(new Set(['benedictio-mensae', 'ante-coenam']))) {
      this.makeCenteredHeader('[Ante Cœnam.]');
    } else if (tags(element).isSupersetOf(new Set(['benedictio-mensae', 'post-coenam']))) {
      this.makeCenteredHeader('[Post Cœnam.]');
    } else if (tags(element).isSupersetOf(new Set(['te-deum', 'hymnus']))) {
      this.makeCenteredHeader('Hymnus [Te Deum.]');
    } else if (uniquelyhas('capitulum') && !quaesitum(element).has('pascha')) {
      if (!parentTags.isDisjointFrom(new Set(['vesperae', 'laudes']))) {
        this.makeCenteredHeader('Capitulum, Hymnus & Versiculus.');
      } else if (quaesitum(element).has('officium-parvum-bmv')) {
        this.makeCenteredHeader('Capitulum & Versiculus.');
      } else {
        this.makeCenteredHeader('Capitulum, Responsorium Breve & Versiculus.');
      }
    } else if (uniquelyhas('versiculus') && !tags(element).isDisjointFrom(new Set(['officium-defunctorum', 'coena-domini', 'parasceve', 'sabbatum-sanctum']))) {
      this.makeCenteredHeader('Versiculus.');
    } else if (uniquelyhas('versiculus') && parentTags.isDisjointFrom(new Set(['commemorationes', 'antiphona-bmv']))) {
      this.makeHeadingAnnotation('Versiculus.');
    } else if (uniquelyhas('absolutio')) {
      this.makeHeadingAnnotation('Absolutio.');
    } else if (uniquelyhas('preces') && !parentTags.has('officium-capituli')) {
      this.makeCenteredHeader('Preces.');
    } else if (uniquelyhas('hymnus')) {
      if (!parentTags.isDisjointFrom(new Set(['vesperae', 'laudes']))) {
        this.makeHeadingAnnotation('Hymnus.');
      } else {
        this.makeCenteredHeader('Hymnus.');
      }
    } else if (uniquelyhas('confiteor') && parentTags.has('completorium')) {
      this.makeCenteredHeader('Confessio.');
    } else if (uniquelyhas('responsorium-breve')) {
      this.makeHeadingAnnotation('Responsorium Breve.');
    } else if (uniquelyhas('responsorium') && uniquelyhas('formula')) {
      let nn = 1;
      if (quaesitum(element).has('nocturna-ii')) {
        nn = 2
      } else if (quaesitum(element).has('nocturna-iii')) {
        nn = 3
      }
      let respPosition = 1;
      if (quaesitum(element).has('responsorium-ii')) {
        respPosition = 2;
      } else if (quaesitum(element).has('responsorium-iii')) {
        respPosition = 3;
      }
      this.makeHeadingAnnotation(`Responsorium ${NUMERALS[3 * nn + respPosition - 4]}.`);
      } else if (uniquelyhas('formula-lectionis')) {
        if (quaesitum(element).has('lectio-brevis')) {
          this.makeCenteredHeader('Lectio Brevis.');
        } else {
          let nn = 1;
          if (quaesitum(element).has('nocturna-ii')) {
            nn = 2;
          } else if (quaesitum(element).has('nocturna-iii')) {
            nn = 3;
          }

          let lessonPosition = 1;
          if (quaesitum(element).has('lectio-ii')) {
            lessonPosition = 2;
          } else if (quaesitum(element).has('lectio-iii')) {
            lessonPosition = 3;
          }
          this.makeCenteredHeader(`Lectio ${NUMERALS[3 * nn + lessonPosition - 4]}.`);
        }
    } else if (!quaesitum(element).has('repetita') && !parentTags.has('commemorationes')) {
      if (uniquelyhas('antiphona-magnificat') && !parentTags.has('antiphona-nunc-dimittis') && !parentTags.has('antiphona-benedictus')) {
        this.makeCenteredHeader('Canticum B. Mariæ Virg.');
      } else if ((uniquelyhas('antiphona-nunc-dimittis') && !quaesitum(element).has('triduum')) || (uniquelyhas('nunc-dimittis') && (quaesitum(element).has('triduum') || quaesitum(element).has('pascha') && !quaesitum(element).has('i-vesperae')))) {
        this.makeCenteredHeader('Canticum Simeonis.');
      } else if (uniquelyhas('antiphona-prior-benedictus') && !parentTags.has('antiphona-magnificat') && !parentTags.has('antiphona-nunc-dimittis')) {
        this.makeCenteredHeader('Canticum Zachariæ.');
      }
    }
  }

  tryHymn(element, translation, parentTags) {
    function uniquelyhasbottom(tag, tagset = tags(element)) {
      return tagset.has(tag) && !tags(element.datum).has(tag);
    }

    // Ignore nested hymns and Te Deum.
    if (!uniquelyhasbottom('hymnus') || tags(element).has('te-deum')) {
      return false;
    }

    if (typeof unpack(element) === 'string' && unpack(element).startsWith('[')) {
      this.appendText(unpack(element));
      return true;
    }
    this.openDiv('', 'hymnus');

    if (element.cantus) {
      this.renderGabc(element.datum[0], quaesitum(element), element.cantus, translation, parentTags.union(tags(element)));
      element.datum.shift();
    }

    for (let i of unpack(element)) {
      this.openParagraph('hymnus');
      this.appendText(i);
    }
    this.closeDiv('hymnus');
    return true;
  }

  tryResponsory(element, translation, parentTags) {
    // Handle Responsories and Short Responsories.
    // If data.datum is an array, that means that the responsory isn't actually nested down another layer.
    if (!tags(element).has('responsorium') && !tags(element).has('responsorium-breve') || !Array.isArray(element.datum)) {
      return false;
    }
    
    // This is a string if no responsory was found
    if (typeof element.datum[1] === 'string') {
      this.openParagraph([...tags(element)].join(' '));
      this.appendText(element.datum[1].replace(", 'incipit'",''));
      this.closeParagraph();
      return true;
    }
    if (translation) {
      let trans = unpack(translation);
      let allDefined = true;
      for (var i = 0; i < unpack(translation).length; i++) {
        if (!trans[i]) {
          let resp = claw(element.datum[i]);
          if ('translation' in resp) {
            trans[i] = unpack(resp.translation);
          }
          if (trans[i] == undefined) {
            allDefined = false;
            break;
          }
        }
      }
      if (allDefined) {
        translation = trans.join('').split('\n').map((line) => {
          let pref = line.match(/^(?:R\.\sbr\.\s|R\.\s|V\.\s|)(.)/)[0];
          return line.replace(pref, pref.toUpperCase().replace('BR', 'br'));
        });
      } else {
        translation = null;
      }
    }
    if (element.cantus) {
      let trans = unpack(element.cantus);
      let allDefined = true;
      for (var i = 0; i < unpack(element.cantus).length; i++) {
        if (trans[i] === null) {
          let resp = claw(element.datum[i]);
          if ('cantus' in resp) {
            trans[i] = unpack(resp.cantus);
          }
          if (trans[i] == undefined) {
            allDefined = false;
            break;
          }
        } else {
          trans[i] = unpack(trans[i]);
        }
      }
      element.cantus = allDefined ? trans.join('') : null;
    }
    element.datum = unpack(element).join('').split('\n').map((line) => {
      let pref = line.match(/^(?:R\.\sbr\.\s|R\.\s|V\.\s|)(.)/)[0];
      return line.replace(pref, pref.toUpperCase().replace('BR', 'br'));
    });
    if (element.cantus) {
      this.renderGabc(element.datum, quaesitum(element), element.cantus, translation, parentTags.union(tags(element)));
      return true;
    }
    this.openParagraph([...tags(element)].join(' '));
    // We're ok with nested responsories.
    this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
    this.closeParagraph();
    return true;
  }

  tryChant(element, translation, parentTags) {
    if (this.openDivs.includes('gabc-chant-container') || typeof element !== 'object' || !('cantus' in element) || element['cantus'] === undefined || (!quaesitum(element).isDisjointFrom(new Set(['antiphona', 'hymnus'])) && JSON.stringify(element.datum).includes('"cantus"'))) {
      return false;
    }
    this.renderGabc(element.datum, quaesitum(element), element.cantus, translation, parentTags.union(tags(element)));
    return true;
  }

  tryPsalmify(element, translation, parentTags) {
    if (!element.tags.join(' ').includes('/psalmi/')) {
      return false;
    }
    element.datum = formatPsalm(element.datum, this.resources, this.antiphonMode, this.antiphonClef);

    this.makeHeadingAnnotation(element.datum.split('\n')[0].slice(1, -1));
    // Removes the header from the actual text and removes the numbering from the first line of the Psalm so that the initial letter is done on the word rather than the number.
    element.datum = element.datum.replace(/^\[.+?]\n\d+\s/, '').split('\n');
    if (translation) {
      translation = formatPsalm(unpack(translation)).replace(/^\[.+?]\n\d+\s/, '').replaceAll(/\[.+?]\n/g, '\n').split('\n');
    }
    if (parentTags.has('preces')) {
      element.tags.push('textus-psalmi-precibus');
    } else {
      element.tags.push('textus-psalmi');
    }
    this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
    return true;
  }

  tryLesson(element, translation, parentTags) {
    function uniquelyhasbottom(tag, tagset = tags(element)) {
      return tagset.has(tag) && !tags(element.datum).has(tag);
    }

    if (!uniquelyhasbottom('lectio') || tags(element.datum).has('commemoratio-matutini')) {
      return false;
    }

    // Adds extra line of annotation noting that the lesson is a commemoration (i.e. not a continuation of the previous lessons).
    if (tags(element).has('lectio-commemorationis') || tags(element.datum).has('lectio-commemorationis')) {
      this.makeHeadingAnnotation(abbreviateName(this.matinsCommemoration));
    }

    let lesson = unpack(element);
    if (!translation) {
      if (typeof element === 'object' && 'datum' in element && typeof element.datum === 'object' && 'translation' in element.datum) {
        translation = unpack(element.datum.translation);
      } else if (Array.isArray(lesson)) {
        translation = Array(lesson.length).fill('', 0);
      }
    }

    // For the Lamentations of the Sacred Triduum.
    if (quaesitum(element).isSupersetOf(new Set(['sabbatum-sanctum', 'nocturna-i', 'lectio-iii']))) {
      this.openParagraph('lectionis-titulum');
      this.appendText(lesson[0]);
      this.closeParagraph();
      this.openParagraph('lectio-sequens');
      this.recurseRite(lesson[1] + '/' + lesson[2], null, parentTags.union(tags(element)).union(new Set(['lectio-sequens'])));
      closeParagraph();
      return true;
    } else if (quaesitum(element).isSupersetOf(new Set(['triduum', 'nocturna-i']))) {
      if (quaesitum(element).has('lectio-i')) {
        this.openParagraph(`lectionis-titulum ${element.tags.join(' ')}`);
        this.appendText(lesson[0]);
        this.closeParagraph();
        lesson = lesson.slice(1);
      }
      let annotation = lesson[0].match(/^\[.+?\]\//g);
      if (annotation) {
        this.makeHeadingAnnotation(annotation[0].slice(1, -2));
        lesson[0] = lesson[0].replace(/^\[.+?\]\//g,'');
      }
      let body = lesson.slice(0, -1).map((i) => stringRender(i).replace(/^(.)(.+?\.\s)(.)/, '<span class="red">\$1</span>\$2<span class="red">\$3</span>')).join('<br>') + '<br>' + lesson[lesson.length - 1].replace(/^(.)/, '<span class="red">\$1</span>');
      this.openParagraph('lectio-sequens');
      this.appendText(body);
      this.closeParagraph();
      return true;
    }
    if (Array.isArray(element.datum) && element.datum.every(item => tags(item).has('lectio'))) {
      translation = element.datum.map(item => 'translation' in item ? unpack(item.translation) : null);
    } else {
      translation = unpack(translation);
    }
    // For the first lesson from a Homily.
    if (Array.isArray(lesson) && lesson[0].length < 100 && lesson[0].includes('Evangélii')) {
      this.openParagraph('lectionis-titulum');
      this.recurseRite(lesson[0], translation[0], parentTags.union(tags(element)).union(new Set(['lectionis-titulum'])));
      this.closeParagraph();
      this.recurseRite(lesson[1], translation[1], new Set(['evangelium-matutini']));
      this.openParagraph('lectionis-titulum');
      this.recurseRite(lesson[2], translation[2], parentTags.union(tags(element)).union(new Set(['lectionis-titulum'])));
      this.recurseRite(lesson.slice(3).map((re, i) => i == 0 ? re : re.replace(/\]\//, '] ')).join(' &para; '), translation[3] ? translation.slice(3).join(' &para; ') : null, new Set(['lectio-incipiens']));
    // Cheeky heuristic to guess if the first item is a title or if this lesson is really some conjoined lessons.
    } else if (Array.isArray(lesson) && lesson[0].length < 100) {
      this.openParagraph('lectionis-titulum');
      this.recurseRite(lesson[0], translation[0], parentTags.union(tags(element)).union(new Set(['lectionis-titulum'])));
      this.closeParagraph();
      this.recurseRite(lesson.slice(1).join(' &para; '), translation[1] && Array.isArray(translation) ? translation.slice(1).join(' &para; ') : null, new Set([tags(element).has('lectio-i') ? 'lectio-incipiens' : 'lectio-sequens']));
    // Note that an untitled lesson may still be a first lesson. This is due to the fact that most Saints lives are begun without title.
    } else {
      if (Array.isArray(lesson)) {
        lesson = lesson.join(' &para; ');
        translation = translation[0] && Array.isArray(translation) ? translation.join(' &para; ') : null;
      };
      this.closeParagraph();
      this.recurseRite(lesson, translation, new Set([tags(element).has('lectio-i') ? 'lectio-incipiens' : 'lectio-sequens']));
    }
    return true;
  }

  tryCommemorations(element, translation, parentTags) {
    if (!tags(element).has('commemorationes')) {
      return false;
    }
    for (var i = 0; i < element.datum.length - 1; i++) {
      this.openDiv('', 'formula-commemorationis');
      this.makeHeadingAnnotation(abbreviateName(this.usedCommemorations[i][0]));
      this.recurseRite(element.datum[i], translation, parentTags.union(tags(element)));
      if (i != element.datum.length - 2) { this.closeDiv('formula-commemorationis'); }
    }
    this.recurseRite(element.datum.at(-1), translation, parentTags.union(tags(element)));
    this.closeDiv('formula-commemorationis');
    return true;
  }

  tryMartyrology(element, translation, parentTags) {
    if (!tags(element).has('martyrologium')) {
      return false;
    }
    this.openParagraph('martyrologium');
    this.appendText(unpack(element.datum[0]) + ' ' + unpack(element.datum[1]));
    let prae = unpack(element.datum[2]);
    if (prae != '') {
      this.openParagraph('martyrologium');
      this.appendText(prae);
    }
    let martyrology = unpack(element.datum[3]);
    if (typeof martyrology === 'string') {
      this.openParagraph('martyrologium');
      this.appendText(martyrology);
    } else {
      for (let i of unpack(element.datum[3])) {
        this.openParagraph('martyrologium');
        this.appendText(i);
      }
    }
    this.openParagraph('martyrologium');
    this.appendText(unpack(element.datum[4]));
    this.appendText(unpack(element.datum[5]));
    this.closeParagraph();
    return true;
  }

  tryInvitatory(element, translation, parentTags) {
    if (!tags(element).has('invitatorium')) {
      return false;
    }
    this.openDiv('', 'invitatorium');
    // The first instance of the Invitatory antiphon has to be rendered first in order to define antiphonMode.
    this.recurseRite(element.datum[0], translation ? translation[0] : null, parentTags.union(tags(element)));
    let invIndex = 0;
    let invitatorium = this.resources.invitatoria[this.antiphonMode];
    for (let i = 1; i < element.datum.length; i++) {
      if (typeof element.datum[i] == 'object') {
        this.recurseRite(element.datum[i], translation ? translation[i] : null, parentTags.union(tags(element)));
      } else if (invitatorium) {
        this.renderGabc(element.datum[i], quaesitum(element), invitatorium[invIndex++], translation ? translation[i] : null, parentTags);
      } else {
        this.recurseRite(element.datum[i], translation ? translation[i] : null, parentTags.union(tags(element)));
      }
    }
    this.closeDiv('', 'invitatorium');
    return true;
  }

  recurseRite(element, translation, parentTags) {
    // Sometimes an element will have the same kind of thing nested in it recursively. For example, a collecta item may actually be a call to a different day's collecta. In this case, only return true if it's the outer.
    function uniquelyhas(tag, tagset = tags(element)) {
      return tagset.has(tag) && !parentTags.has(tag);
    }

    if (typeof element === 'object' && 'translation' in element) {
      translation = JSON.parse(JSON.stringify(unpack(element.translation)));
    }

    // Manages splitting up strings that include line breaks so that the translation is divided properly.
    // Splits lines denoted by /, but ignores </ (pre-formatted html indicator) or ]/ (annotation).
    if (typeof element === 'string' && element.match(/(?<!\]|\<)\//)) {
      element = element.split(/(?<!\]|\<)\//);
      if (translation) {
        translation = translation.split(/(?<!\]|\[[^\]]+?)\//);
      }
    }
    if (typeof element === 'object' && Array.isArray(element)) {
      for (let i = 0; i < element.length; i++) {
        // For some rubric texts, they're whole lines.
        if (typeof element[i] === 'string' && element[i].match(/^\[.+?\/\]$/)) {
          this.makeHeadingAnnotation(rubricRender(element[i].slice(1, -2)));
        } else {
          this.recurseRite(element[i], Array.isArray(translation) && translation.length == element.length ? translation[i] : null, parentTags);
        }
      }
      return;
    } else if (typeof element === 'string') {
      let annot = element.match(/^\[(.+?)\]\//)
      if (annot) {
        if (parentTags.has('capitulum')) {
          annot[1] = 'Capitulum. ' + annot[1];
        }
        this.makeHeadingAnnotation(rubricRender(annot[1]));
        element = element.replace(annot[0], '');
      }
      if (!this.paragraphOpen) {
        this.openParagraph([...parentTags].join(' '));
      }
      // Idk man
      if (Array.isArray(translation)) {
        translation = null;
      }
      this.appendText(element, translation);
      return;
    }

    // These checks are done before removing empty items since empty antiphons can still confer tone upon the following Psalms.
    if (tags(element).has('antiphona') && 'cantus' in element && element.cantus) {
      let mode = unpack(element.cantus).match(/mode:(.+?)(?:;|\n)/);
      let clef = unpack(element.cantus).replace('%%', '\n%%\n').match(/^\((.+?)\)/m);
      if (mode && clef && !quaesitum(element).has('repetita')) {
        this.antiphonMode = mode[1];
        this.antiphonClef = clef[1];
      } else {
        this.antiphonMode = null;
        this.antiphonClef = null;
      }
    }
    if (unpack(element) == '') {
      return;
    }
    
    this.doHeadering(element, parentTags, uniquelyhas);
    if (this.tryHymn(element, translation, parentTags)) return;
    if (this.tryResponsory(element, translation, parentTags)) return;
    if (this.tryCommemorations(element, translation, parentTags)) return;
    if (this.tryChant(element, translation, parentTags)) return;
    if (this.tryPsalmify(element, translation, parentTags)) return;
    if (this.tryLesson(element, translation, parentTags)) return;
    if (this.tryMartyrology(element, translation, parentTags)) return;
    if (this.tryInvitatory(element, translation, parentTags)) return;

    for (let name of DIVED_ELEMENTS) {
      if (uniquelyhas(name)) {
        this.openDiv('', name);
        this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
        this.closeDiv(name);
        return;
      }
    }
    for (let name of FULLY_PARAGRAPHED_ELEMENTS) {
      if (uniquelyhas(name) && !tags(element).has('dominus-det')) {
        this.openParagraph([...tags(element).union(parentTags)].join(' '));
        this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
        this.closeParagraph();
        return;
      }
    }
    for (let name of PARAGRAPH_CLOSING_ELEMENTS) {
      if (uniquelyhas(name)) {
        this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
        this.closeParagraph();
        return;
      }
    }
    for (let name of PARAGRAPH_OPENING_ELEMENTS) {
      if (uniquelyhas(name)) {
        this.openParagraph([...tags(element).union(parentTags)].join(' '));
        this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
        return;
      }
    }
    this.recurseRite(element.datum, translation, parentTags.union(tags(element)));
  }
}

export function renderRite(rite, resources) {
  let renderer = new RiteRenderer(rite, resources);
  renderer.recurseRite(rite.rite, null, new Set());
  return renderer.rite;
}
