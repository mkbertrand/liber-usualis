// Copyright 2024-2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Additional credit to Benjamin Bloomfield as this file is a modification of his original (except for chomp())

async function chomp(id, tags) {
	return fetch(id).then(data => data.text()).then(gabc => {
		gabc = gabc.replace('<v>\\greheightstar</v>', '*');
		mode = undefined;
		if (gabc.includes('mode:')) {
			mode = gabc.substring(gabc.indexOf('mode:') + 5, gabc.indexOf('\n', gabc.indexOf('mode:'))).trim();
			if (mode.endsWith(';')) {
				mode = mode.slice(0, -1);
			}
		}

		// Remove commented text falling before content
		gabc = gabc.substring(gabc.search(/\([cf]\d\)/));
		gabc = gabc.replaceAll('<sp>V/</sp>.', '<v>\\Vbar</v>').replaceAll('<sp>R/</sp>.', '<v>\\Rbar</v>').replaceAll(/<.?sc>/g, '').replaceAll(/\[.*?\]/g, '').replaceAll(/(\(.+?)(\|.+?)(\))/g, '$1$3').replaceAll('<sp>*</sp>', '*').replace(/<c>.+?<\/c>/, '');

		gabcdata = '';
		if (mode !== undefined) {
			gabcdata = 'mode:' + mode + ';\n%%\n';
		} else {
			gabcdata = '%%\n';
		}

		// Make sure asterisks are formatted right
		gabc = gabc.replace(/(\([,:;]+?\))\s*?\*\s/, '*$1 ');

		if (tags.includes('deus-in-adjutorium')) {
			return gabcdata + gabc.substring(0, gabc.search(/\(Z\-?\)/));

		} else if (tags.includes('antiphona')) {
			euouae = '';
			if (gabc.includes('<eu>')) {
				euouae = gabc.match(/\s<eu>.+/)[0].replaceAll(/<.?eu>/g, '');
				gabc = gabc.substring(0, gabc.search(/<eu>/));
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
				gabc = gabc.substring(0, gabc.indexOf('*')) + '(::)' + euouae;
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
	});
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
		.replace(/<v>\\greheightstar<\/v>/g,'*');
		
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
			var gabc = this.innerText;
			this.setGabc(gabc);
			this.init();
		} else {
			chomp($(this).attr('id'), $(this).attr('tags')).then(text => {this.setGabc(text); this.init();});
		}
	}
}
window.customElements.define('gabc-chant', ChantElement);
