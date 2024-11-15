// Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Additional credit to Benjamin Bloomfield as this file is a modification of his original

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
		this.ctxt.lyricTextFont = "'Times'";
		this.ctxt.setFont("'Times'", 36);
		this.ctxt.dropCapTextFont = this.ctxt.lyricTextFont;
		this.ctxt.annotationTextFont = this.ctxt.lyricTextFont;
		this.ctxt.condenseLineAmount = 1;
		this.ctxt.setGlyphScaling(1/8);
		this.ctxt.dropCapTextFont = this.ctxt.lyricTextFont;
		this.ctxt.annotationTextFont = this.ctxt.lyricTextFont;
		this.ctxt.minLyricWordSpacing *= 1;
		this.ctxt.accidentalSpaceMultiplier = 1.5;
		this.ctxt.annotationTextColor = '#d00';

		this.ctxt.specialCharProperties['font-family'] = "'Versiculum'";
		this.ctxt.specialCharProperties['font-variant'] = 'normal';
		this.ctxt.specialCharProperties['font-size'] = (this.ctxt.lyricTextSize * 1.2) + 'px';
		this.ctxt.specialCharProperties['font-weight'] = '400';
		this.ctxt.specialCharText = function(char) {
			return char.toLowerCase();
		};
		this.ctxt.setRubricColor('#d00');
		this.ctxt.annotationTextFont = this.ctxt.lyricTextFont;
		this.ctxt.intraNeumeSpacing = 5.5;
		ChantElement.gabc = "";

		if (this.innerText != "") {
			var gabc = this.innerText;
			this.setGabc(gabc);
			this.init();
		} else {
			var src = $(this).attr('src');
			$.get(src).then(data => {this.setGabc(data);this.init();});
		}
	}
}
window.customElements.define('gabc-chant', ChantElement);
