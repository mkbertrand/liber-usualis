// Copyright 2023-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import * as Exsurge from 'exsurge';

function stringRender(text) {
		if (text.match(/^\[.+?\]$/)) {
			return `<span class='rite-text-rubric'>${rubricRender(text.slice(1, -1))}</span>`;
		}
		text = text.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
			.replaceAll('É', 'E').replaceAll('Í', 'I')
			.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
			.replaceAll('Ý', 'Y');
		text = text.replaceAll(/(?<!<)\//g, '<br>');

		text = text.replaceAll(/([0-9]+)\s/g, '<span class="verse-number">$1 </span>');
		text = text
      .replace(/\n/g, '<br>')
			.replace(/^V\./g, '<span class="red line-starting-symbol">&#8483;.</span>')
			.replace(/^R\. br./g, '<span class="red line-starting-symbol">&#8479;. br.</span>')
			.replace(/^R\./g, '<span class="red line-starting-symbol">&#8479;.</span>')
			.replace(/&para;/g, '<span class=\'red\'>&para;</span>')
			.replace(/N\./g, '<span class=\'red\'>N.</span>')
			.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
			.replace(/<br>V\./g, '<br><span class=\'red\'>&#8483;.</span>')
			.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
			.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
			.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
			.replace(/\*/g, '<span class=\'red\'>&ast;</span>')
			.replace(/\[\((.+?)\)\]\s/g, '<span class=\'rite-text-rubric small-rubric\'>(\$1) </span>')
			.replace(/\[(.+?)\]/g, '<span class=\'rite-text-rubric\'>\$1</span>');
		return text;
}

import {
  attachChantPointerControls,
  notifyChantRelayout,
  stopChantPlayback,
} from './chant-player.js';
import {bindScoreToContext} from './chant-context.js';

export {stopChantPlayback};

const GABC_CHANT_CONTEXT = new Exsurge.ChantContext(Exsurge.TextMeasuringStrategy.Canvas);

// Exsurge writes these as SVG presentation attributes on live DOM nodes (via
// createSvgNode()), so CSS custom properties resolve here exactly as they
// would in a stylesheet, including re-resolving on a theme change.
GABC_CHANT_CONTEXT.textColor = 'var(--content-text-color)';
GABC_CHANT_CONTEXT.neumeLineColor = 'var(--content-text-color)';

GABC_CHANT_CONTEXT.setFont("'Old Standard TT'", '22');

GABC_CHANT_CONTEXT.textStyles.dropCap.color = 'var(--rubric)';
GABC_CHANT_CONTEXT.textStyles.dropCap.size = '80';

GABC_CHANT_CONTEXT.textStyles.annotation.color = 'var(--rubric)';
GABC_CHANT_CONTEXT.textStyles.annotation.font = GABC_CHANT_CONTEXT.textStyles.al.font;

GABC_CHANT_CONTEXT.rubricColor = 'var(--rubric)';
GABC_CHANT_CONTEXT.staffLineColor = 'var(--rubric)';

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
		
	chantLayout() {
    if (typeof this.score === 'undefined') return;

    bindScoreToContext(GABC_CHANT_CONTEXT, this.score);
    this.score.layoutChantLines(GABC_CHANT_CONTEXT, this.parentElement.parentElement.clientWidth);

    let chantDiv = this.querySelector('.chantelement-chant-content');
    if (!chantDiv) {
      chantDiv = document.createElement('div');
      chantDiv.className = 'chantelement-chant-content';
      this.insertBefore(chantDiv, this.firstChild);
    }

    const svg = this.score.createSvgNode(GABC_CHANT_CONTEXT);
    const children = [svg];
    if (this.translatedNode) children.push(this.translatedNode);
    chantDiv.replaceChildren(...children);

    if (!this.querySelector('.chantelement-text-content')) {
      const textDiv = document.createElement('div');
      textDiv.className = 'chantelement-text-content';
      textDiv.innerHTML = this.plainContent;
      this.appendChild(textDiv);
    }

    notifyChantRelayout(this);
  }

  renderChant() {
    if (typeof this.score !== 'undefined') {
      this.chantLayout();
      return;
    }

    try {
      var mappings = Exsurge.Gabc.createMappingsFromSource(GABC_CHANT_CONTEXT, this.gabc);
      this.score = new Exsurge.ChantScore(GABC_CHANT_CONTEXT, mappings, !this.gabc.includes('initial-style:0;'));
      if (this.gabc.includes('mode:')) {
        var modeloc = this.gabc.indexOf('mode:');
        this.score.annotation = new Exsurge.Annotation(GABC_CHANT_CONTEXT, this.gabc.substring(modeloc + 5, this.gabc.indexOf(';', modeloc)) + '.');
      }
      this.score.performLayout(GABC_CHANT_CONTEXT);

      if (this.translatedText) {
        this.translatedNode = document.createElement('span');
        this.translatedNode.className = 'rite-text chant-translation';
        this.translatedNode.innerHTML = stringRender(this.translatedText);
      }

      this.chantLayout();
    } catch(err) {
      console.log(err);
    }
  }

  connectedCallback() {
    CHANT_VISIBILITY_OBSERVER.observe(this);
  }

  disconnectedCallback() {
    CHANT_VISIBILITY_OBSERVER.unobserve(this);
    if (this.classList.contains('chant-active')) stopChantPlayback();
  }

  onVisible() {
    queueRenderTask(() => this.renderChant());
  }

	constructor() {
		super();

    this.translatedText = this.getAttribute('translated');
    this.gabc = this.getAttribute('gabc');
    this.plainContent = this.innerHTML.toString();
    attachChantPointerControls(this);
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

  window.addEventListener('beforeprint', () => {
    stopChantPlayback();
    document.querySelectorAll('gabc-chant').forEach(elem => {
      elem.renderChant();
    });

    // called to flush layout change - otherwise the final chant wouldn't render properly.
    void document.body.offsetHeight;
  });
}
