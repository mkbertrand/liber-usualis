// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import * as Exsurge from 'exsurge';
import { initChantElement, stopChantPlayback } from './gabc-chant.js';
import { defineAmbit } from './ambit.js';
export { defineAmbit, stopChantPlayback };
initChantElement();

export function abbreviateName(name) {
	name = name.replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.') + '.';
	name = name.replaceAll(/\.\.$/g, '.');
	return name;
}

export function lineByLine(rite) {
  let riteSplit = rite.split(/(<div class="rite-text-container.+?>.+?<\/div>)/);
  let riteRet = [];
  for (let i = 0; i < riteSplit.length; i++) {
    if (i % 2 == 0) {
      riteRet.push(riteSplit[i]);
    } else {
      let style = riteSplit[i].match(/"rite-text-container (.*?)"/)[1];
      let latinColumn = riteSplit[i].match(/<p class="rite-text rite-text-latin.+?>(.*?)<\/p>/)[1];
      let transColumn = riteSplit[i].match(/<p class="rite-text rite-text-translation.+?>(.*?)<\/p>/)[1];
      let latinColumnLines = latinColumn.split('<br>');
      let transColumnLines = transColumn.split('<br>');
      let para = `<div class="rite-text-container ${style}"><p class="rite-text">`;
      for (let j = 0; j < latinColumnLines.length; j++) {
        para += latinColumnLines[j];
        if (transColumnLines[j]) {
          para += `<br><span class="rite-text-translation">${transColumnLines[j]}</span>`;
        }
        if (j != latinColumnLines.length - 1) {
          para += '<br>';
        }
      }
      para += '</p></div>';
      riteRet.push(para);
    }
  }
  return riteRet.join('');
}
