// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import {getPsalmTone} from './psalmify.js';

export function chomp(gabc, tags, resources) {
	gabc = gabc.replace('<v>\\greheightstar</v>', '*');

	let clef;
	let mode = gabc.match(/mode:(.+?)(?:;|\n)/);
	if (mode) {
		mode = mode[1];
	}

	// Remove commented text falling before content
	gabc = gabc.substring(gabc.search(/\n\((.+?)\)/));
	gabc = gabc.replaceAll('<sp>V/</sp>.', '<v>\\Vbar</v>')
		.replaceAll(/<sp>R\/<\/sp>.?/g, '<v>\\Rbar</v>')
		.replaceAll(/<.?sc>/g, '')
		.replaceAll(/\[.*?\]/g, '')
		.replaceAll(/(\(.+?)(\|.+?)(\))/g, '$1$3')
		.replaceAll('<sp>*</sp>', '*')
		.replace(/<c>.+?<\/c>/, '')
		.replaceAll(/<e>(.+?)<\/e>/g, '<i>$1</i>');

	let gabcdata = '';
	if (mode) {
		gabcdata = 'mode:' + mode + ';\n%%\n';
	} else {
		gabcdata = '%%\n';
	}

	// Make sure asterisks are formatted right
	gabc = gabc.replace(/(\([,:;]+?\))\s*?\*\s/, '*$1 ');


  if (tags.has('hymnus') && !tags.has('te-deum')) {
    gabc = gabc.match(/([\s\S]+?)(?:\d\.)?\(::\)/)[1] + '(::)';
  }
	if (tags.has('deus-in-adjutorium')) {
		gabc = gabc.substring(0, gabc.search(/\(Z\-?\)/));

	} else if (tags.has('antiphona')) {
    clef = gabc.match(/(?:^|%)\((.+?)\)/m)
    let euouae = '';
    if (clef) {
      // If clef has a middle letter (very very rare) remove it.
      clef = '' + clef[1][0] + clef[1].at(-1);
      let tone = getPsalmTone(mode, clef, resources);
      if (tone) {
        let ending = tone.terminatio.filter(syl => !syl.includes('r'));
        while (ending.length != 6) {
          ending.unshift(tone.tenor.at(-1));
        }
        euouae = ['E', 'u', 'o', 'u', 'a', 'e.'].map((c, i) => `${c}(${ending[i]})`).join(' ') + ' (::)';
      }
    }

		if (gabc.includes('<i>T. P.</i>')) {
			if (tags.has('in-tempore-paschali')) {
				gabc = gabc.replace('<i>T. P.</i>', '');
			} else {
				gabc = gabc.substring(0, gabc.indexOf('<i>T. P.</i>')).trim();
			}
		}
		if (!tags.has('in-tempore-septuagesimae') && gabc.includes('<i>Post Septuag.</i>')) {
			gabc = gabc.substring(0, gabc.indexOf('<i>Post Septuag.</i>')).trim();
		}
		if (tags.has('intonata')) {
			gabc = gabc.substring(0, gabc.indexOf('*')) + '(::) ' + euouae;
		} else if (tags.has('pars')) {
      gabc = gabc.trim().replace(/^(?:\*\s)?\(.?\)/, '');
      if (clef) {
        gabc = `(${clef}) ` + gabc;
      }
			gabcdata = '%%\n';
		} else if (tags.has('repetita')) {
			gabc = gabc.replace('*', '');
			gabcdata = '%%\n';
		} else if (!(tags.has('commemoratio') || tags.has('suffragium'))) {
			gabc = gabc + euouae;
		}
		
		gabcdata = (tags.has('repetita') || tags.has('pars') ? 'initial-style:0;\n' : 'initial-style:1;\n') + gabcdata;
	} else if (tags.has('invitatorium')) {
    gabcdata = 'initial-style:0;\n' + gabcdata;
  }

  gabc = gabc.replace(/<v>\\([VRA])bar<\/v>/g,function(match,barType) {
    return barType + '/.';
  }).replace(/(<b>[^<]+)<sp>'(?:oe|œ)<\/sp>/g,'$1œ</b>\u0301<b>') // character doesn't work in the bold version of this font.
  .replace(/<b><\/b>/g,'')
  .replace(/<sp>'(?:ae|æ)<\/sp>/g,'ǽ')
  .replace(/<sp>'(?:oe|œ)<\/sp>/g,'œ́')
  .replace(/<v>\\greheightstar<\/v>/g,'*')
  .replace(/<\/?i>/g,'_')
  .replace(/<\/?nlba>/g,'');
  return gabcdata + gabc;
}

