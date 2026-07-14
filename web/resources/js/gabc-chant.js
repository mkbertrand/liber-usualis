// Copyright 2024-2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Additional credit to Benjamin Bloomfield as this file is a modification of his original (except for chomp())

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
	gabc = gabc.substring(gabc.search(/\([cf]\d\)/));
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
		return gabcdata + gabc.substring(0, gabc.search(/\(Z\-?\)/));

	} else if (tags.includes('antiphona')) {
    clef = gabc.match(/^\((.+?)\)/)
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
		} else if (!(tags.includes('formula-commemorationis') || tags.includes('suffragium'))) {
			gabc = gabc + euouae;
		}
		
		gabcdata = (tags.includes('repetita') ? 'initial-style:0;\n' : 'initial-style:1;\n') + gabcdata;
		return gabcdata + gabc;

	} else {
		return gabcdata + gabc;
	}
}

$(document).ready(function() {
	const resizeObserver = new ResizeObserver(() =>{
		$('gabc-chant').each((index, elem) =>
			Promise.resolve(new Promise(((resolve, reject) => elem.chantLayout()))))});
	resizeObserver.observe(document.getElementById('site-wrapper'));
});
	
class ChantElement extends HTMLElement {
		
	getGabc() {
		return this.gabc;
	}
	
	chantLayout() {
		if (typeof this.score !== 'undefined') {
			this.score.layoutChantLines(this.ctxt, $(this).parent().parent().width());
			$(this).html(this.score.createSvg(this.ctxt));
		}
	}
	
	setGabc(gabc) {
		this.gabc = gabc;
		var gabc = this.gabc;
		gabc = gabc.replace(/<v>\\([VRA])bar<\/v>/g,function(match,barType) {
			return barType + '/.';
		}).replace(/(<b>[^<]+)<sp>'(?:oe|œ)<\/sp>/g,'$1œ</b>\u0301<b>') // character doesn't work in the bold version of this font.
		.replace(/<b><\/b>/g,'')
		.replace(/<sp>'(?:ae|æ)<\/sp>/g,'ǽ')
		.replace(/<sp>'(?:oe|œ)<\/sp>/g,'œ́')
		.replace(/<v>\\greheightstar<\/v>/g,'*')
		.replace(/<\/?i>/g,'_')
		.replace(/<\/?nlba>/g,'');

		var mappings = exsurge.Gabc.createMappingsFromSource(this.ctxt, gabc);
		this.score = new exsurge.ChantScore(this.ctxt, mappings, !gabc.includes('initial-style:0;'));
		if (gabc.includes('mode:')) {
			var modeloc = gabc.indexOf('mode:');
			this.score.annotation = new exsurge.Annotation(this.ctxt, gabc.substring(modeloc + 5, gabc.indexOf(';', modeloc)) + '.');
		}
		this.score.performLayout(this.ctxt);
		this.chantLayout();
	}
	
	init() {
	}
	
	constructor() {
		super();
		
		this.ctxt = new exsurge.ChantContext(exsurge.TextMeasuringStrategy.Canvas);

		this.ctxt.setFont("'Old Standard TT'", 22);

		this.ctxt.dropCapTextColor = 'red';
		this.ctxt.dropCapTextSize = '80';

		this.ctxt.annotationTextColor = 'red';
		this.ctxt.annotationTextFont = this.ctxt.lyricTextFont;

		this.ctxt.rubricColor = 'red';
		this.ctxt.staffLineColor = 'red';

		this.ctxt.condenseLineAmount = 1;
		// For some reason, setting the property directly doesn't work for glyph scaling specifically :D
		this.ctxt.setGlyphScaling(1/12);
		this.ctxt.minLyricWordSpacing *= 1;
		this.ctxt.accidentalSpaceMultiplier = 1.5;
		this.ctxt.intraNeumeSpacing = 5;

		this.ctxt.specialCharProperties['font-family'] = "'Versiculum'";
		this.ctxt.specialCharProperties['font-variant'] = 'normal';
		this.ctxt.specialCharProperties['font-size'] = (this.ctxt.lyricTextSize * 1.2) + 'px';
		this.ctxt.specialCharProperties['font-weight'] = '400';
		this.ctxt.specialCharText = function(char) {
			return char.toLowerCase();
		};
		ChantElement.gabc = "";

		if (this.innerText != "") {
			var gabc = chomp(this.innerText, $(this).attr('tags'));
			this.setGabc(gabc);
			this.init();
		} else {
			fetch($(this).attr('id'))
        .then(grabError)
        .catch(err => this.innerText = '')
				.then(data => data.text())
				.then(resp => chomp(resp, $(this).attr('tags')))
				.then(text => {this.setGabc(text); this.init();});
		}
	}
}
window.customElements.define('gabc-chant', ChantElement);
