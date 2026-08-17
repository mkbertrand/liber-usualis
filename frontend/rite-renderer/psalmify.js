// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import Hypher from 'hypher';
import laPatterns from './la-hypher.js';

function adjustToKey(item, currentKey, endKey) {
  let diff = 2 * (endKey.at(-1) - currentKey.at(-1));
  if (diff == 0) {
    return item;
  } else {
    let newItem = [];
    for (let i = 0; i < item.length; i++) {
      let newItemComp = '';
      for (let j = 0; j < item[i].length; j++) {
        if (item[i][j] >= 'a' && item[i][j] <= 'l') {
          newItemComp += String.fromCharCode(item[i][j].charCodeAt(0) + diff);
        } else {
          newItemComp += item[i][j];
        }
      }
      newItem.push(newItemComp);
    }
    return newItem;
  }
}

export function getPsalmTone(tone, clef, resources) {
  if (!tone) {
    return null;
  } else if (tone == 'T. pereg.') {
    tone = 'p';
  }
  // If there's a middle character to the clef, ignore it for our purposes.
  clef = clef.at(0) + clef.at(-1);

  var mode = resources.psalmTones[tone[0]];
  var possibleVariants = mode.filter((variant) => tone in variant);

  var variant = possibleVariants[0];
  if (possibleVariants.length != 1) {
    for (const possibleVariant of possibleVariants) {
      if (possibleVariant.clavis == clef) {
        variant = possibleVariant;
      }
    }
  }
  if (variant === undefined) {
    return undefined;
  }

  return {
    'initium': adjustToKey(variant.initium, variant.clavis, clef),
    'tenor': adjustToKey(variant.tenor, variant.clavis, clef),
    'flexa': adjustToKey(variant.flexa, variant.clavis, clef),
    'medians': adjustToKey(variant.medians, variant.clavis, clef),
    'terminatio': adjustToKey(variant[tone], variant.clavis, clef)
  };
}

// hyphenateText() is used instead of hyphenate() since hyphenateText() can take whole sections of text.
// The second argument is the minimum character count of the word to be hyphenated; it defaults to four.
const HYPH = new Hypher(laPatterns);

function formatHeader(header) {
  header = header.slice(1, -2).replace(':', '. ') + '.';
  let numeral = header.match(/\s([IVXLC]+)[\s|\.]/);
  if (numeral) {
    numeral = numeral[1];
    const vals = {'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1};
    var number = 0;
    for (var j = 0; j < numeral.length; j++) {
      if (j != numeral.length - 1 && vals[numeral[j]] < vals[numeral[j + 1]]) {
        number += vals[numeral[j + 1]] - vals[numeral[j]];
        j++;
      } else {
        number += vals[numeral[j]];
      }
    }
  }
  return `[${header.replace(numeral, number)}]\n`;
}

// The first value is the number of preparatory syllables and the second value is the number of accents.
function accentationData(blankChant) {
  let acc = 0;
  for (const s of blankChant) {
    if (s.includes('r')) {
      acc ++;
    }
  }
  return [blankChant.length - 3 * acc, acc];
}

const LONGS = ['á', 'é', 'í', 'ó', 'ú', 'ý', 'ǽ', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ý', 'Ǽ'];

function isDactylic(text, position) {
  var monosyllabic = text[position - 1] == ' ';

  // If there are two monosyllabic words next to eachother, then not dactylic.
  if (monosyllabic && text[position - 3] == ' ' || position == 2) {
    return false;
  // If there is a two syllable word after a monosyllabic word, then dactylic.
  } else if (monosyllabic && text[position - 4] == ' ' || position == 3) {
    return true;
  } else if (monosyllabic) {
    return LONGS.some(i => text[position - 3].includes(i));
  } else if (position <= 1){
    return false;
  } else {
    return LONGS.some(i => text[position - 2].includes(i));
  }
}

const PUNCTUATION = [',', '.', ';', ':', '!', '?'];

function hyphenateTextRight(text) {
  let ret = '';
  for (let word of text.split(' ')) {
    let punct = '';
    for (const p of PUNCTUATION) {
      if (word.endsWith(p)) {
        punct = p;
        word = word.slice(0, -1);
        break;
      }
    }
    ret += HYPH.hyphenate(word).join('\u00AD') + punct + ' ';
  }
  return ret.slice(0, -1);
}

function accentMark(syllables, accentationData, cursor) {
  for (let i = 0; i < accentationData[1]; i++) {
    // If the syllable under the cursor is actually a space, move to the previous syllable.
    if (syllables[cursor] == ' ') {
      cursor--;
    }
    var dactylic = isDactylic(syllables, cursor);
    if (syllables[cursor - 1] == ' ') {
      cursor--;
    }
    if (dactylic) {
      cursor -= 2;
    } else {
      cursor--;
    }
    if (syllables[cursor] == ' ') {
      cursor--;
    }
    syllables[cursor] = `<span class="accent-start">${syllables[cursor]}</span>`;
    cursor -= 1;
  }

  for (let i = 0; i < accentationData[0]; i++) {
    if (syllables[cursor] == ' ') {
      cursor--;
    }
    syllables[cursor] = `<span class="preceding-syllable">${syllables[cursor]}</span>`;
    cursor--;
  }
  return syllables;
}

export function formatPsalm(psalm, resources = null, psalmTone = null, clef = null) {

  var tone = getPsalmTone(psalmTone, clef, resources);

  var ret = '';

  for (const p of psalm.split(/(\[.+?\]\n)/).slice(1)) {
    if (p.startsWith('[')) {
      ret += formatHeader(p);
    } else if (tone) {
      for (let line of p.split('\n')) {
        if (line == '') {
          ret += '\n';
          continue;
        }
        var annot = line.match(/\d+\s(?:\[.+?\]\s)?/);
        if (annot) {
          annot = annot[0];
          line = line.replace(annot, '');
        } else {
          annot = '';
        }

        var syllables = hyphenateTextRight(line).split(/(\s)/).map(str => str.split(/\u00AD/)).flat();

        syllables = accentMark(syllables, accentationData(tone.terminatio), syllables.length - 1);
        if (!line.startsWith('Magníficat')) {
          syllables = accentMark(syllables, accentationData(tone.medians), syllables.indexOf('*') - 2);
        }
        if (syllables.indexOf('+') != -1) {
          syllables = accentMark(syllables, accentationData(tone.flexa), syllables.indexOf('+') - 2);
        }
        line = syllables.join('');
        ret += annot + line + '\n';
      }
      
      ret = ret.slice(0, -1);
    } else {
      ret += p;
    }
  }
  return ret;
}
