// Copyright 2023-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import * as Exsurge from 'exsurge';
import {stringRender} from './rite-renderer/rendering-utils.js';

const GABC_CHANT_CONTEXT = new Exsurge.ChantContext(Exsurge.TextMeasuringStrategy.Canvas);

GABC_CHANT_CONTEXT.setFont("'Old Standard TT'", '22');

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
		
  // AI-authored because look how tedious this is.
	chantLayout() {
    if (typeof this.score === 'undefined') return;

    this.score.layoutChantLines(GABC_CHANT_CONTEXT, this.parentElement.parentElement.clientWidth);

    let chantDiv = this.querySelector('.chantelement-chant-content');
    if (!chantDiv) {
      chantDiv = document.createElement('div');
      chantDiv.className = 'chantelement-chant-content';
      this.insertBefore(chantDiv, this.firstChild);
    }
    chantDiv.innerHTML = this.score.createSvg(GABC_CHANT_CONTEXT) + this.translated;

    if (!this.querySelector('.chantelement-text-content')) {
      const textDiv = document.createElement('div');
      textDiv.className = 'chantelement-text-content';
      textDiv.innerHTML = this.plainContent;
      this.appendChild(textDiv);
    }
  }

  renderChant() {
    try {
      var mappings = Exsurge.Gabc.createMappingsFromSource(GABC_CHANT_CONTEXT, this.gabc);
      this.score = new Exsurge.ChantScore(GABC_CHANT_CONTEXT, mappings, !this.gabc.includes('initial-style:0;'));
      if (this.gabc.includes('mode:')) {
        var modeloc = this.gabc.indexOf('mode:');
        this.score.annotation = new Exsurge.Annotation(GABC_CHANT_CONTEXT, this.gabc.substring(modeloc + 5, this.gabc.indexOf(';', modeloc)) + '.');
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
