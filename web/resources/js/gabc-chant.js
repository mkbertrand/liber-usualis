// Copyright 2023-2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Additional credit to Benjamin Bloomfield as this file is a modification of his original (except for chomp())

const GABC_CHANT_CONTEXT = new exsurge.ChantContext(exsurge.TextMeasuringStrategy.Canvas);

GABC_CHANT_CONTEXT.setFont("'Old Standard TT'", 22);

GABC_CHANT_CONTEXT.dropCapTextColor = 'red';
GABC_CHANT_CONTEXT.dropCapTextSize = '80';

GABC_CHANT_CONTEXT.annotationTextColor = 'red';
GABC_CHANT_CONTEXT.annotationTextFont = GABC_CHANT_CONTEXT.lyricTextFont;

GABC_CHANT_CONTEXT.rubricColor = 'red';
GABC_CHANT_CONTEXT.staffLineColor = 'red';

GABC_CHANT_CONTEXT.condenseLineAmount = 1;
// For some reason, setting the property directly doesn't work for glyph scaling specifically :D
GABC_CHANT_CONTEXT.setGlyphScaling(1/12);
GABC_CHANT_CONTEXT.minLyricWordSpacing *= 1;
GABC_CHANT_CONTEXT.accidentalSpaceMultiplier = 1.5;
GABC_CHANT_CONTEXT.intraNeumeSpacing = 5;

GABC_CHANT_CONTEXT.specialCharProperties['font-family'] = "'Versiculum'";
GABC_CHANT_CONTEXT.specialCharProperties['font-variant'] = 'normal';
GABC_CHANT_CONTEXT.specialCharProperties['font-size'] = (GABC_CHANT_CONTEXT.lyricTextSize * 1.2) + 'px';
GABC_CHANT_CONTEXT.specialCharProperties['font-weight'] = '400';
GABC_CHANT_CONTEXT.specialCharText = function(char) {
  return char.toLowerCase();
};

euouaes = {
  '1 a c4': 'E(h) u(h) o(g) u(f) a(g) e.(h.) (::)',
  '1 a2 c4': 'E(h) u(h) o(g) u(f) a(g) e.(gh..) (::)',
  '1 a3 c4': 'E(h) u(h) o(g) u(f) a(gh) e.(gh..) (::)',
  '1 D c4': 'E(h) u(h) o(g) u(f) a(gh) e.(gFED.) (::)',
  '1 D2 c4': 'E(h) u(h) o(g) u(f) a(gf) e.(d.) (::)',
  '1 f c4': 'E(h) u(h) o(g) u(f) a(gh) e.(gf..) (::)',
  '1 g c4': 'E(h) u(h) o(g) u(f) a(gh) e.(g.) (::)',
  '1 g2 c4': 'E(h) u(h) o(g) u(f) a(g) e.(ghg.) (::)',
  '1 g3 c4': 'E(h) u(h) o(g) u(f) a(g) e.(g.) (::)',
  '2 A c3': 'E(h) u(h) o(h) u(g) a(e) e.(f.) (::)',
  '2 D f3': 'E(h) u(h) o(h) u(g) a(e) e.(f.) (::)',
  '3 a c3': 'E(h) u(h) o(h) u(f) a(h) e.(gf..) (::)',
  '3 a c4': 'E(j) u(j) o(j) u(h) a(j) e.(ih..) (::)',
  '3 a2 c4': 'E(j) u(j) o(ji) u(hi) a(h) e.(gh..) (::)',
  '3 b c4': 'E(j) u(j) o(j) u(h) a(j) e.(i.) (::)',
  '3 g c4': 'E(j) u(j) o(ji) u(hi) a(h) e.(g.) (::)',
  '3 g2 c4': 'E(j) u(h) o(j) u(i) a(h) e.(g.) (::)',
  '4 A c3': 'E(i) u(h) o(i) u(j) a(h) e.(f.) (::)',
  '4 A c4': 'E(k) u(j) o(k) u(l) a(j) e.(h.) (::)',
  '4 A* c3': 'E(i) u(h) o(i) u(j) a(h) e.(f.) (::)',
  '4 c c3': 'E(i) u(i) o(i) u(i) a(i) e.(h.) (::)',
  '4 E c4': 'E(h) u(g) o(h) u(ih) a(gf) e.(e.) (::)',
  '4 g c4': 'E(h) u(h) o(h) u(h) a(h) e.(g.) (::)',
  '5 a c3': 'E(h) u(h) o(i) u(g) a(h) e.(f.) (::)',
  '5 a c4': 'E(j) u(j) o(k) u(i) a(j) e.(h.) (::)',
  '6 C c2': 'E(h) u(h) o(f) u(gh) a(g) e.(f.) (::)',
  '6 F c4': 'E(h) u(h) o(f) u(gh) a(g) e.(f.) (::)',
  '7 a c2': 'E(g) u(g) o(h) u(g) a(f) e.(ed..) (::)',
  '7 a c3': 'E(i) u(i) o(j) u(i) a(h) e.(gf..) (::)',
  '7 b c3': 'E(i) u(i) o(j) u(i) a(h) e.(g.) (::)',
  '7 c c2': 'E(g) u(g) o(h) u(g) a(f) e.(ef..) (::)',
  '7 c c3': 'E(i) u(i) o(j) u(i) a(h) e.(gh..) (::)',
  '7 c2 c3': 'E(i) u(i) o(j) u(i) a(h) e.(ih..) (::)',
  '7 d c2': 'E(g) u(g) o(h) u(g) a(f) e.(eg..) (::)',
  '7 d c3': 'E(i) u(i) o(j) u(i) a(h) e.(gi..) (::)',
  '8 c c3': 'E(h) u(h) o(f) u(h) a(i) e.(h.) (::)',
  '8 c c4': 'E(j) u(j) o(h) u(j) a(k) e.(j.) (::)',
  '8 G c3': 'E(h) u(h) o(g) u(h) a(f) e.(e.) (::)',
  '8 G c4': 'E(j) u(j) o(i) u(j) a(h) e.(g.) (::)',
  '8 G* c3': 'E(h) u(h) o(g) u(h) a(f) e.(e.) (::)',
  '8 G* c4': 'E(j) u(j) o(i) u(j) a(h) e.(g.) (::)',
  'T. pereg. c4': 'E(g) u(g) o(g) u(d) a(f) e.(ed..) (::)'
};

function chomp(gabc, tags) {
	gabc = gabc.replace('<v>\\greheightstar</v>', '*');

	mode = gabc.match(/mode:(.+?)(?:;|\n)/);
	if (mode) {
		mode = mode[1];
	}

	// Remove commented text falling before content
	gabc = gabc.substring(gabc.search(/\n\((.+?)\)/));
	gabc = gabc.replaceAll('<sp>V/</sp>.', '<v>\\Vbar</v>')
		.replaceAll('<sp>R/</sp>.', '<v>\\Rbar</v>')
		.replaceAll(/<.?sc>/g, '')
		.replaceAll(/\[.*?\]/g, '')
		.replaceAll(/(\(.+?)(\|.+?)(\))/g, '$1$3')
		.replaceAll('<sp>*</sp>', '*')
		.replace(/<c>.+?<\/c>/, '')
		.replaceAll(/<e>(.+?)<\/e>\(.\)/g, '<i>$1</i>()');

	gabcdata = '';
	if (mode) {
		gabcdata = 'mode:' + mode + ';\n%%\n';
	} else {
		gabcdata = '%%\n';
	}

	// Make sure asterisks are formatted right
	gabc = gabc.replace(/(\([,:;]+?\))\s*?\*\s/, '*$1 ');


  if (tags.includes('hymnus') && !tags.includes('te-deum')) {
    gabc = gabc.match(/([\s\S]+?)(?:\d\.)?\(::\)/)[1] + '(::)';
  }
	if (tags.includes('deus-in-adjutorium')) {
		this.gabc = gabc.substring(0, gabc.search(/\(Z\-?\)/));

	} else if (tags.includes('antiphona')) {
    clef = gabc.match(/^\((.+?)\)/m)
    let euouae = '';
    if (clef) {
      // If clef has a middle letter (very very rare) remove it.
      clef = '' + clef[1][0] + clef[1].at(-1);
      ending = mode + ' ' + clef;
      euouae = ending in euouaes ? euouaes[ending] : '';
    }

		if (gabc.includes('<i>T. P.</i>')) {
			if (tags.includes('in-tempore-paschali')) {
				gabc = gabc.replace('<i>T. P.</i>', '');
			} else {
				gabc = gabc.substring(0, gabc.indexOf('<i>T. P.</i>')).trim();
			}
		}
		if (!tags.includes('in-tempore-septuagesimae') && gabc.includes('<i>Post Septuag.</i>')) {
			gabc = gabc.substring(0, gabc.indexOf('<i>Post Septuag.</i>')).trim();
		}
		if (tags.includes('intonata')) {
			gabc = gabc.substring(0, gabc.indexOf('*')) + '(::) ' + euouae;
		} else if (tags.includes('pars')) {
			gabc = gabc.replace(/^(\(..\)\s).+?\*(\(.*?\))?\s?/, '$1');
			gabcdata = '%%\n';
		} else if (tags.includes('repetita')) {
			gabc = gabc.replace('*', '');
			gabcdata = '%%\n';
			firstsyllable = gabc.match(/[\wáǽœÆŒéíóúý]+\(/)[0];
			gabc = gabc.replace(firstsyllable, firstsyllable.charAt(0).toUpperCase() + firstsyllable.slice(1).toLowerCase());
		} else if (!(tags.includes('commemoratio') || tags.includes('suffragium'))) {
			gabc = gabc + euouae;
		}
		
		gabcdata = (tags.includes('repetita') ? 'initial-style:0;\n' : 'initial-style:1;\n') + gabcdata;
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

var chantPromises = new Map();

function getChantPromise(src) {
  var promise = chantPromises.get(src);
  if (!promise) {
    promise = fetch(src);
    chantPromises.set(promise);
  }
  return promise;
}

class ChantElement extends HTMLElement {
		
	chantLayout() {
		if (typeof this.score !== 'undefined') {
			this.score.layoutChantLines(GABC_CHANT_CONTEXT, $(this).parent().parent().width());
			$(this).html(this.score.createSvg(GABC_CHANT_CONTEXT) + this.translated);
		}
	}
	
  async connectedCallback() {
    try {
      if (!this.gabc) {
        this.gabc = await getChantPromise(this.src).then(data => data.text());
      }
      var gabc = chomp(this.gabc, this.tags);
      var mappings = exsurge.Gabc.createMappingsFromSource(GABC_CHANT_CONTEXT, gabc);
      this.score = new exsurge.ChantScore(GABC_CHANT_CONTEXT, mappings, !gabc.includes('initial-style:0;'));
      if (gabc.includes('mode:')) {
        var modeloc = gabc.indexOf('mode:');
        this.score.annotation = new exsurge.Annotation(GABC_CHANT_CONTEXT, gabc.substring(modeloc + 5, gabc.indexOf(';', modeloc)) + '.');
      }
      this.score.performLayout(GABC_CHANT_CONTEXT);
      this.chantLayout();

      if (this.translated) {
        this.translated = `<p class="rite-text rite-text-translation line-by-line">${this.translated}</p>`;
      } else {
        this.translated = '';
      }
    } catch(err) {
      console.log(err);
    }
  }

	constructor() {
		super();

    this.translated = $(this).attr('translated');
    console.log(this.translated);

    if ($(this).attr('gabc')) {
      this.gabc = $(this).attr('gabc');
		} else {
      this.src = $(this).attr('src');
    }

    this.tags = $(this).attr('tags').split('+');
	}
}
window.customElements.define('gabc-chant', ChantElement);

$(document).ready(function() {
	const resizeObserver = new ResizeObserver(() =>{
		$('gabc-chant').each((index, elem) =>
			Promise.resolve(new Promise(((resolve, reject) => elem.chantLayout()))))});
	resizeObserver.observe(document.getElementById('site-wrapper'));
});
