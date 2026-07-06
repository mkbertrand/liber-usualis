// Copyright 2024-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

function riteTitle(title, tags, size = 'large') {
	if (size == 'small') {
		return `<h1 class="small-title">${title}</h1>`;
	} else {
		var subtitle = '';
		if (tags.includes('duplex-i-classis')) {
			subtitle = 'Duplex I. Classis.';
		} else if (tags.includes('duplex-ii-classis')) {
			subtitle = 'Duplex II. Classis.';
		} else if (tags.includes('duplex-majus')) {
			subtitle = 'Duplex Majus.';
		} else if (tags.includes('duplex-minus')) {
			subtitle = 'Duplex Minus.';
		} else if (tags.includes('semiduplex')) {
			subtitle = 'Semiduplex.';
		} else if (tags.includes('simplex') || tags.includes('feria')) {
			subtitle = 'Simplex.'
		}

		if (tags.includes('mtv')) {
			subtitle += ' (m.t.v.)'
		}
		return `<h1 class="large-title">${(title + '.').replaceAll(/\.\.$/g, '.')}</h1><h2 class="large-subtitle">${subtitle}</h2>`;
	}
}

function abbreviateName(name) {
	name = name.replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.') + '.';
	name = name.replaceAll(/\.\.$/g, '.');
	return name;
}

// It can be readily observed that this is just an extremely primitive version of render()
function unpack(data) {
	if (typeof data === 'string') {
		return data;
	} else if (typeof data === 'object') {
		return Array.isArray(data) ? data.map((d) => unpack(d)).flat() : unpack(data.datum);
	}
};

// Digs out nested data recursively (useful for translation)
function claw(data) {
	if (typeof data.datum === 'string' || Array.isArray(data.datum)) {
		return data;
	} else {
		return claw(data.datum);
	}
}

function rubricRender(data) {
	data = data.replaceAll(/\[(.+?)\]/g, '<span class=\'black-rubric\'>\$1</span>');
	data = data.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
		.replaceAll('É', 'E').replaceAll('Í', 'I')
		.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
		.replaceAll('Ý', 'Y');
	data = data.replaceAll(/(?<!<)\//g, '<br>');
	data = data.replace(/\n/g, '<br>')
		.replace(/&para;/g, '<span class=\'red\'>&para;</span>')
		.replace(/N\./g, '<span class=\'red\'>N.</span>')
		.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
		.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
		.replace(/^V\./g, '<span class=\'red\'>&#8483;.</span>')
		.replace(/>V\./g, '<br><span class=\'red\'>&#8483;.</span>')
		.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
		.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
		.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
		.replace(/\*/g, '<span class=\'red\'>&ast;</span>');
	return data;
}

const RITE_HEADERS = {
	'matutinum': 'Ad Matutinum.',
	'laudes': 'Ad Laudes.',
	'prima': 'Ad Primam.',
	'tertia': 'Ad Tertiam.',
	'sexta': 'Ad Sextam.',
	'nona': 'Ad Nonam.',
	'vesperae': 'Ad Vesperas.',
	'completorium': 'Ad Completorium.',
	'psalmi-graduales': 'Psalmi Graduales.',
	'psalmi-poenitentiales': 'Septem Psalmi Pœnitentiales [cum Litaniis.]',
	'litaniae-sanctorum': 'Litaniæ Sanctorum.',
	'ordo-commendationis-animae': 'Ordo Commendationis Animæ.',
	'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenarium in Articulo Mortis.',
	'pro-prandio': 'Benedictio Mensæ.',
	'pro-coena': 'Benedictio Mensæ.',
	'itinerarium': 'Itinerarium Clericorum.',
	'officium-capituli': 'Martyrologium.'
};

const GENERAL_HEADERS = {
	'psalmi': 'Psalmi.',
	'collecta-primaria': 'Collecta.',
	'invitatorium': 'Invitatorium.',
	'haec-dies': 'Antiphona.'
};

const NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'];
const DIVED_ELEMENTS = ['aperi-domine', 'sacrosanctae', 'ritus', 'invitatorium', 'nocturna', 'psalmi', 'preces', 'collecta-primaria', 'antiphona-bmv'];
const FULLY_PARAGRAPHED_ELEMENTS = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'responsorium', 'responsorium-breve', 'versiculus', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-dirigere', 'rubricum', 'hymnus', 'lectionis-titulum', 'evangelium-matutini', 'lectio-incipiens', 'lectio-sequens'];
const PARAGRAPH_CLOSING_ELEMENTS = ['gloria-versorum', 'terminatio'];
const PARAGRAPH_OPENING_ELEMENTS = ['capitulum', 'absolutio', 'pater-noster-clara-voce', 'pater-noster-semisecreta', 'credo-semisecreta', 'confiteor', 'oratio-sanctae-mariae', 'textus-psalmi-precibus', 'collecta'];

const TRIVIAL_CHANTS = ['deus-in-adjutorium'];

function renderRite(data, options) {

	function stringRender(text, translation = false) {
		if (text.match(/^\[.+?\]$/)) {
			return `<span class='rite-text-rubric'>${rubricRender(text.slice(1, -1))}</span>`;
		}
		if (translation && !options['side-by-side']) {
			text = text.replaceAll(/^(V\.\s|R\.\sbr.\s|R\.\s|\d+)/g, '');
		}
		text = text.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
			.replaceAll('É', 'E').replaceAll('Í', 'I')
			.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
			.replaceAll('Ý', 'Y');
		text = text.replaceAll(/(?<!<)\//g, '<br>');

		text = text.replaceAll(/([0-9]+)\s/g, '<span class="verse-number">$1 </span>');
		text = text.replace(/\n/g, '<br>')
			.replace(/&para;/g, '<span class=\'red\'>&para;</span>')
			.replace(/N\./g, '<span class=\'red\'>N.</span>')
			.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
			.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
			.replace(/^V\./g, '<span class=\'red\'>&#8483;.</span>')
			.replace(/<br>V\./g, '<br><span class=\'red\'>&#8483;.</span>')
			.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
			.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
			.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
			.replace(/\*/g, '<span class=\'red\'>&ast;</span>')
			.replace(/\[\((.+?)\)\]\s/g, '<span class=\'rite-text-rubric small-rubric\'>(\$1) </span>')
			.replace(/\[(.+?)\]/g, '<span class=\'rite-text-rubric\'>\$1</span>');
		return text;
	};

	usedCommemorations = data['used-commemorations'];
	matinsCommemoration = data['commemoratio-matutini'] ? data['commemoratio-matutini'][0] : null;
	translationcssclass = options['side-by-side'] ? 'rite-text-translation side-by-side' : 'rite-text-translation line-by-line';

	rite = '';

	openDivs = [];
	paragraphOpen = false;
	function openDiv(style, name) {
		rite += `<div class="rite-item ${style} ${name}">`;
		openDivs.push(name);
	}

	function closeDiv(name) {
		openDivs.pop();
		closeParagraph();
		rite += '</div>';
	}

	function openParagraph(style) {
		closeParagraph();
		paragraphOpen = true;
		rite += `<p class="rite-text ${style}">`;
	}

	function closeParagraph() {
		if (paragraphOpen) {
			paragraphOpen = false;
			rite += '</p>';
		}
	}

	function makeCenteredHeader(header, style = 'item-header') {
		closeParagraph();
		rite += `<h4 class="centered-header ${style}">${rubricRender(header)}</h4>`;
	}

	function makeHeadingAnnotation(annot) {
		closeParagraph();
		rite += `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${annot}</p>`;
	}

	function appendText(text) {
		rite += text;
	}

	function renderInner(data, translated = null, parentTags) {
		// Sometimes an element will have the same kind of thing nested in it recursively. For example, a collecta item may actually be a call to a different day's collecta. In this case, only return true if it's the outer.
		function uniquelyhas(tag, list = data.tags) {
			return list.includes(tag) && !parentTags.includes(tag);
		}

		// Same as above, but only for the bottom of the recursion.
		function uniquelyhasbottom(tag, list = data.tags) {
			return list.includes(tag) && (!(typeof data.datum === 'object') || !('tags' in data.datum) || !data.datum.tags.includes(tag));
		}

		try {

			if (typeof data === 'object' && 'translation' in data) {
				translated = JSON.parse(JSON.stringify(data.translation.datum));
			}

			// Manages splitting up strings that include line breaks so that the translation is divided properly.
			if (typeof data === 'string' && data.match(/(?<!\]|\[[^\]]+?)\//)) {
				data = data.split(/(?<!\]|\[[^\]]+?)\//);
				if (translated) {
					translated = translated.split(/(?<!\]|\[[^\]]+?)\//);
				}
			}

			if (typeof data === 'object' && Array.isArray(data)) {
				for (let i = 0; i < data.length; i++) {
					// For some rubric texts, they're whole lines.
					if (typeof data[i] === 'string' && data[i].match(/^\[.+?\/\]$/)) {
						makeHeadingAnnotation(rubricRender(data[i].slice(1, -2)));
					} else {
						renderInner(data[i], Array.isArray(translated) && translated.length == data.length ? translated[i] : null, parentTags);
					}
				}

			} else if (typeof data === 'string') {
				annot = data.match(/^\[(.+?)\]\//)
				if (annot) {
					if (parentTags.includes('capitulum')) {
						annot[1] = 'Capitulum. ' + annot[1];
					}
					makeHeadingAnnotation(rubricRender(annot[1]));
					data = data.replace(annot[0], '');
				}
				if (!paragraphOpen) {
					openParagraph(parentTags.join(' '));
				}
				appendText(stringRender(data) + (translated ? `<br><span class="${translationcssclass} ${parentTags.join(' ')}">${stringRender(translated, true)}</span><br>` : '<br>'));

			} else if (typeof data === 'object' && 'tags' in data) {
				if (unpack(data) == '') {
					return;
				}

				// Handle most things related to adding headers.
				if (data.tags.includes('nocturna')) {
					if (data.quaesitum.includes('nocturna-i')) {
						makeCenteredHeader('Nocturnus I.', 'section-header');
					} else if (data.quaesitum.includes('nocturna-ii')) {
						makeCenteredHeader('Nocturnus II.', 'section-header');
					} else if (data.quaesitum.includes('nocturna-iii')) {
						makeCenteredHeader('Nocturnus III.', 'section-header');
					} else {
						makeCenteredHeader('Nocturnus.', 'section-header');
					}
				} else if (data.tags.includes('ritus')) {
					if (data.tags.includes('antiphona-bmv')) {
						makeCenteredHeader('Antiphona B.M.V.');
					} else {
						for (let i of data.tags) {
							if (i in RITE_HEADERS && !parentTags.includes(i)) {
								makeCenteredHeader(RITE_HEADERS[i], 'section-header');
							}
						}
					}
				} else {
					for (let i of data.tags) {
						if (!('quaesitum' in data)) {
							data.quaesitum = [];
						}
						if (i in GENERAL_HEADERS && !parentTags.includes(i) && data.datum != '') {
							makeCenteredHeader(GENERAL_HEADERS[i]);
						}
					}
					if (data.tags.includes('benedictio-mensae')) {
						if (data.tags.includes('ante-prandium')) {
							makeCenteredHeader('[Ante Prandium.]');
						} else if (data.tags.includes('post-prandium')) {
							makeCenteredHeader('[Post Prandium.]');
						} else if (data.tags.includes('ante-coenam')) {
							makeCenteredHeader('[Ante Cœnam.]');
						} else if (data.tags.includes('post-coenam')) {
							makeCenteredHeader('[Post Cœnam.]');
						}
					} else if (data.tags.includes('te-deum') && data.tags.includes('hymnus')) {
						makeCenteredHeader('Hymnus [Te Deum.]');
					} else if (uniquelyhas('capitulum') && !data.tags.includes('pascha')) {
						if (data.quaesitum.includes('officium-parvum-bmv') && !['vesperae', 'laudes'].some(tag => parentTags.includes(tag))) {
							makeCenteredHeader('Capitulum & Versiculus.');
						} else if (['vesperae', 'laudes'].some(tag => parentTags.includes(tag))) {
							makeCenteredHeader('Capitulum, Hymnus & Versiculus.');
						} else {
							makeCenteredHeader('Capitulum, Responsorium Breve & Versiculus.');
						}
					} else if (uniquelyhas('versiculus') && ['officium-defunctorum', 'coena-domini', 'parasceve', 'sabbatum-sanctum'].some(tag => data.tags.includes(tag))) {
						makeCenteredHeader('Versiculus.');
					} else if (uniquelyhas('versiculus') && !parentTags.includes('commemorationes') && !parentTags.includes('antiphona-bmv')) {
						makeHeadingAnnotation('Versiculus.');
					} else if (uniquelyhas('absolutio')) {
						makeHeadingAnnotation('Absolutio.');
					} else if (uniquelyhas('preces') && !parentTags.includes('officium-capituli')) {
						makeCenteredHeader('Preces.');
					} else if (uniquelyhas('hymnus')) {
						if (['vesperae', 'laudes'].some(tag => parentTags.includes(tag))) {
							makeHeadingAnnotation('Hymnus.');
						} else {
							makeCenteredHeader('Hymnus.');
						}
					} else if (uniquelyhas('confiteor') && parentTags.includes('completorium')) {
						makeCenteredHeader('Confessio.');
					} else if (!data.quaesitum.includes('repetita') && !parentTags.includes('commemorationes')) {
						if (uniquelyhas('antiphona-magnificat') && !parentTags.includes('antiphona-nunc-dimittis') && !parentTags.includes('antiphona-benedictus')) {
							makeCenteredHeader('Canticum B. Mariæ Virg.');
						} else if ((uniquelyhas('antiphona-nunc-dimittis') && !data.quaesitum.includes('triduum')) || (uniquelyhas('nunc-dimittis') && (data.quaesitum.includes('triduum') || data.quaesitum.includes('pascha') && !data.quaesitum.includes('i-vesperae')))) {
							makeCenteredHeader('Canticum Simeonis.');
						} else if (uniquelyhas('antiphona-prior-benedictus') && !parentTags.includes('antiphona-magnificat') && !parentTags.includes('antiphona-nunc-dimittis')) {
							makeCenteredHeader('Canticum Zachariæ.');
						}
					}
				}

				// Handle hymns (excluding the Te Deum which just gets rendered like normal.)
				if (uniquelyhasbottom('hymnus') && !data.tags.includes('te-deum')) {
					if (unpack(data.datum) == '') {
						return;
					}
					else if (typeof unpack(data.datum) === 'string' && unpack(data.datum).startsWith('[')) {
						appendText(stringRender(unpack(data.datum)));
						return;
					}
					openDiv('', 'hymnus');

          if (options.chant && data.cantus) {
            openDiv('', 'gabc-chant');
            let cantusUnpack = unpack(data.cantus);
            if (typeof cantusUnpack === 'string' && cantusUnpack.startsWith('/')) {
              rite += `<gabc-chant id="/chant${cantusUnpack}" tags="${data.tags.concat(parentTags).join('+')}"></gabc-chant>`;
            } else {
              rite += `<gabc-chant tags="${data.tags.concat(parentTags).join('+')}">${cantusUnpack}</gabc-chant>`;
            }
            closeDiv('', 'gabc-chant');
            data.datum.shift();
          }

					for (let i of unpack(data.datum)) {
						openParagraph('hymnus');
						appendText(stringRender(i));
						closeParagraph();

					}
					closeDiv('hymnus');
					return;
        }

				if (!openDivs.includes('gabc-chant-container') && typeof data === 'object' && options['chant'] && 'cantus' in data && data['cantus'] != undefined && (options['display-trivial-chant'] || !data.tags.some(tag => TRIVIAL_CHANTS.includes(tag)))) {
					openDiv('', 'gabc-chant-container');
					openDiv('', 'gabc-chant');
          let cantusUnpack = unpack(data.cantus);
          if (typeof cantusUnpack === 'string' && cantusUnpack.startsWith('/')) {
            rite += `<gabc-chant id="/chant${cantusUnpack}" tags="${data.tags.concat(parentTags).join('+')}"></gabc-chant>`;
          } else {
            rite += `<gabc-chant tags="${data.tags.concat(parentTags).join('+')}">${cantusUnpack}</gabc-chant>`;
          }
					closeDiv('', 'gabc-chant');
					openDiv('', 'gabc-chant-replaced-text');
					renderInner(data, translated, parentTags);
					closeDiv('gabc-chant-replaced-text');
					closeDiv('gabc-chant-container');
					return;

				// Handle objects that have chant.
				} else if (!openDivs.includes('gabc-chant-container') && typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && (options['display-trivial-chant'] || !data.tags.some(tag => TRIVIAL_CHANTS.includes(tag)))) {
					openDiv('', 'gabc-chant-container');
					openDiv('', 'gabc-chant');
					rite += `<gabc-chant id="/chant/${data['src']}" tags="${data.tags.concat(parentTags).join('+')}"></gabc-chant>`;
					closeDiv('', 'gabc-chant');
					openDiv('', 'gabc-chant-replaced-text');
					renderInner(data, translated, parentTags);
					closeDiv('gabc-chant-replaced-text');
					closeDiv('gabc-chant-container');
					return;

				// Handle Responsories and Short Responsories.
				// If data.datum is an array, that means that the responsory isn't actually nested down another layer.
				} if ((data.tags.includes('responsorium') || data.tags.includes('responsorium-breve')) && Array.isArray(data.datum)) {
					// This is a string if no responsory was found
					if (typeof data.datum[1] === 'string') {
						appendText(stringRender(data.datum[1].replace(", 'incipit'",'')));
					}
					if (data.quaesitum.includes('responsorium-breve')) {
						makeHeadingAnnotation('Responsorium Breve.');
					} else {
						nn = 1;
						if (data.quaesitum.includes('nocturna-ii')) {
							nn = 2
						} else if (data.quaesitum.includes('nocturna-iii')) {
							nn = 3
						}
						respPosition = 1;
						if (data.quaesitum.includes('responsorium-ii')) {
							respPosition = 2;
						} else if (data.quaesitum.includes('responsorium-iii')) {
							respPosition = 3;
						}
						makeHeadingAnnotation(`Responsorium ${NUMERALS[3 * nn + respPosition - 4]}.`);
					}
					if (translated) {
						var trans = translated;
						var allDefined = true;
						for (var i = 0; i < translated.length; i++) {
							if (!trans[i]) {
								resp = claw(data.datum[i]);
								if ('translation' in resp) {
									trans[i] = unpack(resp.translation);
								}
								if (trans[i] == undefined) {
									allDefined = false;
									break;
								}
							}
						}
						if (allDefined) {
							translated = trans.join('').split('\n').map((line) => {
								pref = line.match(/^(?:R\.\sbr\.\s|R\.\s|V\.\s|)(.)/)[0];
								return line.replace(pref, pref.toUpperCase().replace('BR', 'br'));
							});
						} else {
							translated = null;
						}
					}
					data.datum = unpack(data.datum).join('').split('\n').map((line) => {
						pref = line.match(/^(?:R\.\sbr\.\s|R\.\s|V\.\s|)(.)/)[0];
						return line.replace(pref, pref.toUpperCase().replace('BR', 'br'));
					});

					// We're ok with nested responsories.
					parentTags = parentTags.filter(tag => tag != 'responsorium');

				// Handle headers for Lessons.
				} else if (data.tags.includes('formula-lectionis') && data.datum != '' && !(typeof data.datum !== 'string' && 'tags' in data.datum && data.datum.tags.includes('formula-lectionis'))) {
					if (data.quaesitum.includes('lectio-brevis')) {
						makeCenteredHeader('Lectio Brevis.');
					} else {
						nn = 1;
						if (data.quaesitum.includes('nocturna-ii')) {
							nn = 2
						} else if (data.quaesitum.includes('nocturna-iii')) {
							nn = 3
						}

						lessonPosition = 1;
						if (data.quaesitum.includes('lectio-ii')) {
							lessonPosition = 2;
						} else if (data.quaesitum.includes('lectio-iii')) {
							lessonPosition = 3;
						}
						makeCenteredHeader(`Lectio ${NUMERALS[3 * nn + lessonPosition - 4]}.`);
					}

				// Handle Psalms.
				} else if (data.tags.join(' ').includes('/psalmi/')) {
					function doPsalmHeadering(psalmBlock) {
						headers = psalmBlock.match(/\[.+?\]\n/g);
						for (let i of headers) {
							newHeader = i.slice(1, -2).replace(':', '. ') + '.';
							numeral = newHeader.match(/\s([IVXLC]+)[\s|\.]/);
							if (numeral) {
								numeral = numeral[1];
								vals = {'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1};
								number = 0;
								for (var j = 0; j < numeral.length; j++) {
									if (j != numeral.length - 1 && vals[numeral[j]] < vals[numeral[j + 1]]) {
										number += vals[numeral[j + 1]] - vals[numeral[j]];
										j++;
									} else {
										number += vals[numeral[j]];
									}
								}
								newHeader = newHeader.replace(numeral, number);
							}
							psalmBlock = psalmBlock.replace(i, '[' + newHeader + ']\n');
						}
						return psalmBlock;
					}
					data.datum = doPsalmHeadering(data.datum);

					header = makeHeadingAnnotation(data.datum.split('\n')[0].slice(1, -1));
					// Removes the header from the actual text and removes the numbering from the first line of the Psalm so that the initial letter is done on the word rather than the number.
					data.datum = data.datum.replace(/^\[.+?]\n\d+\s/, '').split('\n');
					if (translated) {
						if (options['side-by-side']) {
							translated = doPsalmHeadering(translated).replace(/^\[.+?]\n\d+\s/, '').split('\n');
						} else {
							translated = translated.replaceAll(/\[.+?]/g, '').split('\n').slice(1);
						}
					}
					if (parentTags.includes('preces')) {
						data.tags.push('textus-psalmi-precibus');
					} else {
						data.tags.push('textus-psalmi');
					}

				// Handle Lessons.
				} else if (data.tags.includes('lectio') && !(typeof data.datum === 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('commemoratio-matutini'))) {
					// Adds extra line of annotation noting that the lesson is a commemoration (i.e. not a continuation of the previous lessons).
					if (data.tags.includes('lectio-commemorationis') || typeof data.datum == 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('lectio-commemorationis')) {
						makeHeadingAnnotation(abbreviateName(matinsCommemoration));
					}

					lesson = unpack(data);
					if (!translated) {
						if (typeof data === 'object' && 'datum' in data && typeof data.datum === 'object' && 'translation' in data.datum) {
							translated = unpack(data.datum.translation);
						} else if (Array.isArray(lesson)) {
							translated = Array(lesson.length).fill('', 0);
						}
					}

					// For the Lamentations of the Sacred Triduum.
					if (data.quaesitum.includes('sabbatum-sanctum') && data.quaesitum.includes('nocturna-i') && data.quaesitum.includes('lectio-iii')) {
						lesson = [lesson[0], lesson[1] + '<br>' + lesson[2].replace(/^(.)/, '<span class="red">\$1</span>')];
					} else if (data.quaesitum.includes('triduum') && data.quaesitum.includes('nocturna-i')) {
						if (data.quaesitum.includes('lectio-i')) {
							rite += `<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${stringRender(lesson[0])}</p>`;
							lesson = lesson.slice(1);
						}
						annotation = lesson[0].match(/^\[.+?\]\//g);
						if (annotation) {
							makeHeadingAnnotation(annotation[0].slice(1, -2));
							lesson[0] = lesson[0].replace(/^\[.+?\]\//g,'');
						}
						body = lesson.slice(0, -1).map((i) => stringRender(i).replace(/^(.)(.+?\.\s)(.)/, '<span class="red">\$1</span>\$2<span class="red">\$3</span>')).join('<br>') + '<br>' + lesson[lesson.length - 1].replace(/^(.)/, '<span class="red">\$1</span>');
						rite += `<p class="rite-text lectio-sequens">${body}</p>`;
						return;
					}

					// For the first lesson from a Homily.
					if (Array.isArray(lesson) && lesson[0].length < 100 && lesson[0].includes('Evangélii')) {
						openParagraph('lectionis-titulum');
						renderInner(lesson[0], translated[0], [...data.tags, ...parentTags, 'lectionis-titulum']);
						closeParagraph();
						renderInner(lesson[1], translated[1], ['evangelium-matutini']);
						openParagraph('lectionis-titulum');
						renderInner(lesson[2], translated[2], [...data.tags, ...parentTags, 'lectionis-titulum']);
						renderInner(lesson.slice(3).map((re, i) => i == 0 ? re : re.replace(/\]\//, '] ')).join(' &para; '), translated[3] ? translated.slice(3).join(' &para; ') : null, ['lectio-incipiens']);
					// Cheeky heuristic to guess if the first item is a title or if this lesson is really some conjoined lessons.
					} else if (Array.isArray(lesson) && lesson[0].length < 100) {
						openParagraph('lectionis-titulum');
						renderInner(lesson[0], translated[0], [...data.tags, ...parentTags, 'lectionis-titulum']);
						closeParagraph();
						renderInner(lesson.slice(1).join(' &para; '), translated[1] ? translated.slice(1).join(' &para; ') : null, [data.quaesitum.includes('lectio-i') ? 'lectio-incipiens' : 'lectio-sequens']);
					// Note that an untitled lesson may still be a first lesson. This is due to the fact that most Saints lives are begun without title.
					} else {
						if (Array.isArray(lesson)) {
							lesson = lesson.join(' &para; ');
							translated = translated[0] ? translated.join(' &para; ') : null;
						};
						closeParagraph();
						renderInner(lesson, translated, [data.quaesitum.includes('lectio-i') ? 'lectio-incipiens' : 'lectio-sequens']);
					}
					return;

				// Handle Commemorations.
				// This will not be reached if there are no Commemorations since the empty string in data.datum would cause renderInner() to stop.
				} else if (data.tags.includes('commemorationes')) {

					makeCenteredHeader('Commemorationes.');

					// Last two items in the data.datum array are the final Commemoration and the Termination of that Commemoration's collect.
					for (var i = 0; i < data.datum.length - 1; i++) {
						openDiv('', 'formula-commemorationis');
						makeHeadingAnnotation(abbreviateName(usedCommemorations[i][0]));
						renderInner(data.datum[i], translated, data.tags.concat(parentTags));
						if (i != data.datum.length - 2) { closeDiv('formula-commemorationis'); }
					}
					renderInner(data.datum.at(-1), translated, data.tags.concat(parentTags));
					closeDiv('formula-commemorationis');
					return;

				// Handle the Martyrology proper.
				} else if (data.tags.includes('martyrologium')) {
					openParagraph('martyrologium');
					appendText(stringRender(unpack(data.datum[0])) + ' ' + stringRender(unpack(data.datum[1])));
					prae = unpack(data.datum[2]);
					if (prae != '') {
						openParagraph('martyrologium');
						appendText(stringRender(prae));
					}
					martyrology = unpack(data.datum[3]);
					if (typeof martyrology === 'string') {
						openParagraph('martyrologium');
						appendText(stringRender(martyrology));
					} else {
						for (let i of unpack(data.datum[3])) {
							openParagraph('martyrologium');
							appendText(stringRender(i));
						}
					}
					openParagraph('martyrologium');
					appendText(stringRender(unpack(data.datum[4])) + '<br>' + stringRender(unpack(data.datum[5])));
					closeParagraph();
					return;
				}

				for (let name of DIVED_ELEMENTS) {
					if (uniquelyhas(name)) {
						openDiv('', name);
						renderInner(data.datum, translated, data.tags.concat(parentTags));
						closeDiv(name);
						return;
					}
				}
				for (let name of FULLY_PARAGRAPHED_ELEMENTS) {
					if (uniquelyhas(name) && !data.tags.includes('dominus-det')) {
						openParagraph(data.tags.concat(parentTags).join(' '));
						renderInner(data.datum, translated, data.tags.concat(parentTags));
						closeParagraph();
						return;
					}
				}
				for (let name of PARAGRAPH_CLOSING_ELEMENTS) {
					if (uniquelyhas(name)) {
						renderInner(data.datum, translated, data.tags.concat(parentTags));
						closeParagraph();
						return;
					}
				}
				for (let name of PARAGRAPH_OPENING_ELEMENTS) {
					if (uniquelyhas(name)) {
						openParagraph(data.tags.concat(parentTags).join(' '));
						renderInner(data.datum, translated, data.tags.concat(parentTags));
						return;
					}
				}
				renderInner(data.datum, translated, parentTags);
			}
		} catch(err) {
			console.log(err);
			console.log(data);
			console.log("Some objects failed to render correctly.");
		}
	}

	renderInner(data['rite'], null, []);

	if (options['translation'] && options['side-by-side']) {
		pat1 = /(<\/?div.*?>|(?:<h4.+?<\/h4>))/;
		split = rite.split(pat1);
		rite = '';
		for (i of split) {
			if (i == '' || pat1.test(i)) {
				rite += i;
			} else {
				for (pa of i.split(/<\/p>/)) {
					if (pa == '') {
						continue;
					}
					rite += '<div class="side-by-side-column-container">';
					leftColumn = '<div class="left-column-latin">';
					rightColumn = '<div class="right-column-vernacular rite-text-translation side-by-side">' + pa.match(/^<p.+?>/);
					translations = pa.match(/<span class="rite-text-translation.+?<\/span><br>/g);
					if (translations) {
						for (j of translations) {
							rightColumn += j.replaceAll('rite-text-translation', 'rite-text');
						}

						leftColumn += pa.replaceAll(/<span class="rite-text-translation.+?<\/span><br>/g, '');
					} else {
						leftColumn += pa;
					}
					leftColumn += '</p></div>';
					rightColumn += '</p></div>';
					rite += leftColumn + rightColumn + '</div>';
				}
			}
		}
	}
	return rite;
};
