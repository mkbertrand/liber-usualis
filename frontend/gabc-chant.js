// Copyright 2023-2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.
// Additional credit to Benjamin Bloomfield as this file is a modification of his original (except for chomp())

import * as Exsurge from 'exsurge';
import {stringRender} from './rite-renderer/rendering-utils.js';

const GABC_CHANT_CONTEXT = new Exsurge.ChantContext(Exsurge.TextMeasuringStrategy.Canvas);

GABC_CHANT_CONTEXT.setFont("'Old Standard TT'", 22);

GABC_CHANT_CONTEXT.textStyles.dropCap.color = 'red';
GABC_CHANT_CONTEXT.textStyles.dropCap.size = '80';

GABC_CHANT_CONTEXT.textStyles.annotation.color = 'red';
GABC_CHANT_CONTEXT.textStyles.annotation.font = GABC_CHANT_CONTEXT.textStyles.al.font;

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

euouaes = {};
fetch('/chant/liber-usualis-chant/untagged/euouae.json').then(data => data.json()).then(json => euouaes = json);

function chomp(gabc, tags) {
	gabc = gabc.replace('<v>\\greheightstar</v>', '*');

	mode = gabc.match(/mode:(.+?)(?:;|\n)/);
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
      gabc = `(${clef})` + gabc.trim().replace(/^.+\*\(.?\)/, '');
			gabcdata = '%%\n';
		} else if (tags.includes('repetita')) {
			gabc = gabc.replace('*', '');
			gabcdata = '%%\n';
		} else if (!(tags.includes('commemoratio') || tags.includes('suffragium'))) {
			gabc = gabc + euouae;
		}
		
		gabcdata = (tags.includes('repetita') || tags.includes('pars') ? 'initial-style:0;\n' : 'initial-style:1;\n') + gabcdata;
	} else if (tags.includes('invitatorium')) {
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

renderQueue = []
var processing = false;

function scheduleTask(task) {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(task, {timeout: 200});
  } else {
    setTimeout(task, 0);
  }
}

function processRenderQueue() {
  if (renderQueue.length == 0) {
    processing = false;
    return;
  }
  processing = true;
  task = renderQueue.shift();
  scheduleTask(() => {
    task();
    processRenderQueue();
  });
}

function queueRenderTask(renderTask) {
  renderQueue.push(renderTask);
  if (!processing) {
    processRenderQueue();
  }
}

const CHANT_VISIBILITY_OBSERVER = new IntersectionObserver((entries) => {
  for (entry of entries) {
    if (entry.isIntersecting) {
      CHANT_VISIBILITY_OBSERVER.unobserve(entry.target);
      entry.target.onVisible();
    }
  }
}, {rootMargin: '400px'});

class ChantElement extends HTMLElement {
		
	chantLayout() {
		if (typeof this.score !== 'undefined') {
			this.score.layoutChantLines(GABC_CHANT_CONTEXT, this.parentElement.parentElement.clientWidth);
			this.innerHTML = `<div class="chantelement-chant-content">${this.score.createSvg(GABC_CHANT_CONTEXT) + this.translated}</div><div class="chantelement-text-content">${this.plainContent}</div>`;
		}
	}
	
  renderChant() {
    try {
      var gabc = chomp(this.gabc, this.tags);
      var mappings = Exsurge.Gabc.createMappingsFromSource(GABC_CHANT_CONTEXT, gabc);
      this.score = new Exsurge.ChantScore(GABC_CHANT_CONTEXT, mappings, !gabc.includes('initial-style:0;'));
      if (gabc.includes('mode:')) {
        var modeloc = gabc.indexOf('mode:');
        this.score.annotation = new Exsurge.Annotation(GABC_CHANT_CONTEXT, gabc.substring(modeloc + 5, gabc.indexOf(';', modeloc)) + '.');
      }
      this.score.performLayout(GABC_CHANT_CONTEXT);
      this.chantLayout();

      if (this.translated) {
        this.translated = `<span class="rite-text chant-translation">${stringRender(this.translated)}</span`;
      } else {
        this.translated = '';
      }
    } catch(err) {
      console.log(err);
    }
  }

  connectedCallback() {
    CHANT_VISIBILITY_OBSERVER.observe(this);
  }

  disconnectedCallback() {
    CHANT_VISIBILITY_OBSERVER.unobserve(this);
  }
  onVisible() {
    queueRenderTask(() => this.renderChant());
  }

	constructor() {
		super();

    this.translated = this.getAttribute('translated');
    this.gabc = this.getAttribute('gabc');
    this.tags = this.getAttribute('tags').split('+');
    this.plainContent = this.innerHTML.toString();
	}
}

export function initChantElement() {
  customElements.define('gabc-chant', ChantElement);
  const resize = () => {
    document.querySelectorAll('gabc-chant').forEach(elem => elem.chantLayout());
  };

  const resizeObserver = new ResizeObserver(resize);

  const startObserve = () => {
    resizeObserver.observe(document.getElementById('site-wrapper'));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserve);
  } else {
    startObserve();
  }
}
