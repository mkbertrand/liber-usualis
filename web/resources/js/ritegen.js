// Copyright 2024-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

function riteTitle(data, size = 'large') {
	if (data.rite.tags.includes('sacrosanctae') || data.rite.tags.includes('antiphona-bmv') || data.rite.tags.includes('officium-capituli')) {
		return '';
	}
	var title = data['used-primary'][0];
	if (size == 'small') {
		return `<h1 class="small-title">${title}</h1>`;
	} else {
		var subtitle = '';
		if (data['used-primary'][1].includes('duplex-i-classis')) {
			subtitle = 'Duplex I Classis.';
		} else if (data['used-primary'][1].includes('duplex-ii-classis')) {
			subtitle = 'Duplex II Classis.';
		} else if (data['used-primary'][1].includes('duplex-majus')) {
			subtitle = 'Duplex Majus.';
		} else if (data['used-primary'][1].includes('duplex-minus')) {
			subtitle = 'Duplex Minus.';
		} else if (data['used-primary'][1].includes('semiduplex')) {
			subtitle = 'Semiduplex.';
		} else if (data['used-primary'][1].includes('simplex') || data['used-primary'][1].includes('feria')) {
			subtitle = 'Simplex.';
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
	'benedictio-mensae': 'Benedictio Mensæ.',
	'itinerarium': 'Itinerarium Clericorum.',
	'officium-capituli': 'Martyrologium.'
};

const GENERAL_HEADERS = {
	'psalmi': 'Psalmi.',
	'collecta-primaria': 'Collecta.',
	'invitatorium': 'Invitatorium.',
	'haec-dies': 'Antiphona.',
	'ante-prandium': 'Ante Prandium.',
	'post-prandium': 'Post Prandium.',
	'ante-coenam': 'Ante Cœnam.',
	'post-coenam': 'Post Cœnam.'
};

const NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'];
const DIVED_ELEMENTS = ['aperi-domine', 'sacrosanctae', 'ritus', 'invitatorium', 'nocturna', 'psalmi', 'preces', 'collecta-primaria']
const FULLY_PARAGRAPHED_ELEMENTS = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'responsorium', 'responsorium-breve', 'versiculus', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-dirigere', 'rubricum', 'hymnus'];
const PARAGRAPH_CLOSING_ELEMENTS = ['gloria-versorum', 'terminatio'];
const PARAGRAPH_OPENING_ELEMENTS = ['capitulum', 'absolutio', 'pater-noster-clara-voce', 'pater-noster-semisecreta', 'credo-semisecreta', 'confiteor', 'oratio-sanctae-mariae', 'textus-psalmi-precibus', 'collecta', 'capitulum'];

const TRIVIAL_CHANTS = ['deus-in-adjutorium'];

function renderRite(data, options) {

	function stringRender(data, translation = false) {
		if (data.match(/^\[.+?\]$/)) {
			return `<span class='rite-text-rubric'>${rubricRender(data.slice(1, -1))}</span>`;
		}
		if (translation && !options['side-by-side']) {
			data = data.replaceAll(/^(V\.\s|R\.\sbr.\s|R\.\s|\d+)/g, '');
		}
		data = data.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
			.replaceAll('É', 'E').replaceAll('Í', 'I')
			.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
			.replaceAll('Ý', 'Y');
		data = data.replaceAll(/(?<!<)\//g, '<br>');

		data = data.replaceAll(/([0-9]+)\s/g, '<span class="verse-number">$1 </span>');
		data = data.replace(/\n/g, '<br>')
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
		return data;
	};

	usedCommemorations = data['used-commemorations'];
	commmat = data['commemoratio-matutini'] ? data['commemoratio-matutini'][0] : null;
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

	function renderInner(data, translated = null, parenttags) {
		// Sometimes an element will have the same kind of thing nested in it recursively. For example, a collecta item may actually be a call to a different day's collecta. In this case, only return true if it's the outer.
		function uniquelyhas(tag, list = data.tags) {
			return list.includes(tag) && !parenttags.includes(tag);
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
			if (typeof data === 'string' && data.match(/[^\]]\//)) {
				data = data.split(/[^\]]\//);
				if (translated) {
					translated = translated.split(/[^\]]\//);
				}
			}

			if (typeof data === 'object' && Array.isArray(data)) {
				for (let i = 0; i < data.length; i++) {
					// For some rubric texts, they're whole lines.
					if (typeof data[i] === 'string' && data[i].match(/^\[.+?\/\]$/)) {
						makeHeadingAnnotation(data[i].slice(1, -2));
					} else {
						renderInner(data[i], Array.isArray(translated) && translated.length == data.length ? translated[i] : null, parenttags);
					}
				}

			} else if (typeof data === 'string') {
				if (!paragraphOpen) {
					openParagraph(parenttags.join(' '));
				}
				rite += stringRender(data) + (translated ? `<br><span class="${translationcssclass} ${parenttags.join(' ')}">${stringRender(translated, true)}</span><br>` : '<br>');

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
							if (i in RITE_HEADERS && !parenttags.includes(i)) {
								makeCenteredHeader(RITE_HEADERS[i], 'section-header');
							}
						}
					}
				} else {
					for (let i of data.tags) {
						if (!('quaesitum' in data)) {
							data.quaesitum = [];
						}
						if (i in GENERAL_HEADERS && !parenttags.includes(i) && data.datum != '') {
							makeCenteredHeader(GENERAL_HEADERS[i]);
						}
					}
					if (data.tags.includes('te-deum') && data.tags.includes('hymnus')) {
						makeCenteredHeader('Hymnus [Te Deum.]');
					} else if (uniquelyhas('capitulum') && !data.tags.includes('pascha')) {
						if (data.quaesitum.includes('officium-parvum-bmv') && !['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							makeCenteredHeader('Capitulum & Versiculus.');
						} else if (['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							makeCenteredHeader('Capitulum, Hymnus & Versiculus.');
						} else {
							makeCenteredHeader('Capitulum, Responsorium Breve & Versiculus.');
						}
					} else if (uniquelyhas('versiculus') && ['officium-defunctorum', 'coena-domini', 'parasceve', 'sabbatum-sanctum'].some(tag => data.tags.includes(tag))) {
						makeCenteredHeader('Versiculus.');
					} else if (uniquelyhas('versiculus') && !parenttags.includes('commemorationes') && !parenttags.includes('antiphona-bmv')) {
						makeHeadingAnnotation('Versiculus.');
					} else if (uniquelyhas('absolutio')) {
						makeHeadingAnnotation('Absolutio.');
					} else if (uniquelyhas('preces') && !parenttags.includes('officium-capituli')) {
						makeCenteredHeader('Preces.');
					} else if (uniquelyhas('hymnus')) {
						if (['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							makeHeadingAnnotation('Hymnus.');
						} else {
							makeCenteredHeader('Hymnus.');
						}
					} else if (uniquelyhas('confiteor') && parenttags.includes('completorium')) {
						makeCenteredHeader('Confessio.');
					} else if (!data.quaesitum.includes('repetita') && !parenttags.includes('commemorationes')) {
						if (uniquelyhas('antiphona-magnificat') && !parenttags.includes('antiphona-nunc-dimittis')) {
							makeCenteredHeader('Canticum B. Mariæ Virg.');
						} else if ((uniquelyhas('antiphona-nunc-dimittis') && !data.quaesitum.includes('triduum')) || (uniquelyhas('nunc-dimittis') && (data.quaesitum.includes('triduum') || data.quaesitum.includes('pascha') && !data.quaesitum.includes('i-vesperae')))) {
							makeCenteredHeader('Canticum Simeonis.');
						} else if (uniquelyhas('antiphona-prior-benedictus') && !parenttags.includes('antiphona-magnificat') && !parenttags.includes('antiphona-nunc-dimittis')) {
							makeCenteredHeader('Canticum Zachariæ.');
						}
					}
				}

				// Handle objects that have chant.
				if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disable-trivial-chant'] && data.tags.some(tag => TRIVIAL_CHANTS.includes(tag)))) {
					closeParagraph();
					rite += `<gabc-chant id="/chant/${data['src']}" tags="${data.tags.concat(parenttags).join('+')}"></gabc-chant>`;
					return;

				// Handle Responsories and Short Responsories.
				// If data.datum is an array, that means that the responsory isn't actually nested down another layer.
				} if ((data.tags.includes('responsorium') || data.tags.includes('responsorium-breve')) && Array.isArray(data.datum)) {
					// This is a string if no responsory was found
					if (typeof data.datum[1] === 'string') {
						rite += stringRender(data.datum[1].replace(", 'incipit'",''));
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
						var alldefined = true;
						for (var i = 0; i < translated.length; i++) {
							if (!trans[i]) {
								resp = claw(data.datum[i]);
								if ('translation' in resp) {
									trans[i] = unpack(resp.translation);
								}
								if (trans[i] == undefined) {
									alldefined = false;
									break;
								}
							}
						}
						if (alldefined) {
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
					parenttags = parenttags.filter(tag => tag != 'responsorium');

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
					function doPsalmHeadering(psalmblock) {
						headers = psalmblock.match(/\[.+?\]\n/g);
						for (let i of headers) {
							newheader = i.slice(1, -2).replace(':', '. ') + '.';
							numeral = newheader.match(/\s([IVXLC]+)[\s|\.]/);
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
								newheader = newheader.replace(numeral, number);
							}
							psalmblock = psalmblock.replace(i, '[' + newheader + ']\n');
						}
						return psalmblock;
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
					if (parenttags.includes('preces')) {
						data.tags.push('textus-psalmi-precibus');
					} else {
						data.tags.push('textus-psalmi');
					}

				// Handle Lessons.
				} else if (data.tags.includes('lectio') && !(typeof data.datum === 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('commemoratio-matutini'))) {
					// Adds extra line of annotation noting that the reading is a commemoration (i.e. not a continuation of the previous readings).
					if (data.tags.includes('lectio-commemorationis') || typeof data.datum == 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('lectio-commemorationis')) {
						makeHeadingAnnotation(abbreviateName(commmat));
					}

					reading = unpack(data);
					if (!translated) {
						if (typeof data === 'object' && 'datum' in data && typeof data.datum === 'object' && 'translation' in data.datum) {
							translated = unpack(data.datum.translation);
						} else if (Array.isArray(reading)) {
							translated = Array(reading.length).fill('', 0);
						}
					}

					// Readings have initial letters, but the first-letter pseudoclass is applied to the first letter of a paragraph. Therefore the reading's annotation needs to be in a separate paragraph.
					function annotate(reading, translated, cssclasses) {
						annotation = reading.match(/^\[.+?\]\//g);
						if (annotation) {
							reading = reading.replace(/^\[.+?\]\//g,'');
							makeHeadingAnnotation(annotation[0].slice(1, -2))
						}
						openParagraph(cssclasses);
						renderInner(reading, translated, []);
					}

					// For the Lamentations of the Sacred Triduum.
					if (data.quaesitum.includes('sabbatum-sanctum') && data.quaesitum.includes('nocturna-i') && data.quaesitum.includes('lectio-iii')) {
						reading = [reading[0], reading[1] + '<br>' + reading[2].replace(/^(.)/, '<span class="red">\$1</span>')];
					} else if (data.quaesitum.includes('triduum') && data.quaesitum.includes('nocturna-i')) {
						if (data.quaesitum.includes('lectio-i')) {
							rite += `<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${stringRender(reading[0])}</p>`;
							reading = reading.slice(1);
						}
						annotation = reading[0].match(/^\[.+?\]\//g);
						if (annotation) {
							makeHeadingAnnotation(annotation[0].slice(1, -2));
							reading[0] = reading[0].replace(/^\[.+?\]\//g,'');
						}
						body = reading.slice(0, -1).map((i) => stringRender(i).replace(/^(.)(.+?\.\s)(.)/, '<span class="red">\$1</span>\$2<span class="red">\$3</span>')).join('<br>') + '<br>' + reading[reading.length - 1].replace(/^(.)/, '<span class="red">\$1</span>');
						rite += `<p class="rite-text lectio-sequens">${body}</p>`;
						return;
					}

					// For the first reading from a Homily.
					if (Array.isArray(reading) && reading[0].length < 100 && reading[0].includes('Evangélii')) {
						openParagraph('lectionis-titulum');
						renderInner(reading[0], translated[0], parenttags);
						annotate(reading[1], translated[1], 'evangelium-matutini ' + data.tags.join(' '));
						openParagraph('lectionis-titulum');
						renderInner(reading[2], translated[2], parenttags);
						annotate(reading.slice(3).map((re, i) => i == 0 ? re : re.replace(/\]\//, '] ')).join(' &para; '), translated[3] ? translated.slice(3).join(' &para; ') : null, 'lectio-incipiens ' + data.tags.join(' '));
					// Cheeky heuristic to guess if the first item is a title or if this reading is really some conjoined readings.
					} else if (Array.isArray(reading) && reading[0].length < 100) {
						openParagraph('lectionis-titulum');
						renderInner(reading[0], translated[0], parenttags);
						annotate(reading.slice(1).join(' &para; '), translated[1] ? translated.slice(1).join(' &para; ') : null, (data.quaesitum.includes('lectio-i') ? 'lectio-incipiens ' : 'lectio-sequens ') + data.tags.join(' '));
					// Note that an untitled reading may still be a first reading. This is due to the fact that most Saints lives are begun without title.
					} else {
						if (Array.isArray(reading)) {
							reading = reading.join(' &para; ');
							translated = translated[0] ? translated.join(' &para; ') : null;
						};
						annotate(reading, translated, (data.quaesitum.includes('lectio-i') ? 'lectio-incipiens ' : 'lectio-sequens ') + data.tags.join(' '));
					}
					return;

				// Handle hymns (excluding the Te Deum which just gets rendered like normal.)
				} else if (uniquelyhas('hymnus') && !data.tags.includes('te-deum')) {
					if (unpack(data.datum) == '') {
						return;
					}
					else if (typeof unpack(data.datum) === 'string' && unpack(data.datum).startsWith('[')) {
						rite += stringRender(unpack(data.datum));
						return;
					}
					openDiv('', 'hymnus');
					for (let i of unpack(data.datum)) {
						openParagraph('hymnus');
						rite += stringRender(i);
						closeParagraph();

					}
					closeDiv('hymnus');
					return;

				// Handle Commemorations.
				// This will not be reached if there are no Commemorations since the empty string in data.datum would cause renderInner() to stop.
				} else if (data.tags.includes('commemorationes')) {

					makeCenteredHeader('Commemorationes.');

					// Last two items in the data.datum array are the final Commemoration and the Termination of that Commemoration's collect.
					for (var i = 0; i < data.datum.length - 1; i++) {
						openDiv('', 'formula-commemorationis');
						makeHeadingAnnotation(abbreviateName(usedCommemorations[i][0]));
						renderInner(data.datum[i], translated, data.tags.concat(parenttags));
						if (i != data.datum.length - 2) { closeDiv('formula-commemorationis'); }
					}
					renderInner(data.datum.at(-1), translated, data.tags.concat(parenttags));
					closeDiv('formula-commemorationis');
					return;

				// Handle the Martyrology proper.
				} else if (data.tags.includes('martyrologium')) {
					openParagraph('martyrologium');
					rite += stringRender(unpack(data.datum[0])) + ' ' + stringRender(unpack(data.datum[1]));
					prae = unpack(data.datum[2]);
					if (prae != '') {
						openParagraph('martyrologium');
						rite += stringRender(prae);
					}
					martyrology = unpack(data.datum[3]);
					if (typeof martyrology === 'string') {
						openParagraph('martyrologium');
						rite += stringRender(martyrology);
					} else {
						for (let i of unpack(data.datum[3])) {
							openParagraph('martyrologium');
							rite += `<p class="rite-text martyrologium">${stringRender(i)}</p>`;
						}
					}
					openParagraph('martyrologium');
					rite += stringRender(unpack(data.datum[4])) + '<br>' + stringRender(unpack(data.datum[5]));
					closeParagraph();
					return;

				// Handle Chapters.
				} else if (uniquelyhasbottom('capitulum') && !data.tags.includes('pascha')) {
					annotationsearch = /^\[(.+?)\]\//;
					annotation = 'Capitulum.' + (annotationsearch.test(data.datum) ? ' ' + data.datum.match(annotationsearch)[1] : '');
					makeHeadingAnnotation(annotation);
					data.datum = data.datum.replace(annotationsearch, '');

				}

				for (let name of DIVED_ELEMENTS) {
					if (uniquelyhas(name)) {
						openDiv('', name);
						renderInner(data.datum, translated, data.tags.concat(parenttags));
						closeDiv(name);
						return;
					}
				}
				for (let name of FULLY_PARAGRAPHED_ELEMENTS) {
					if (uniquelyhas(name)) {
						openParagraph(data.tags.concat(parenttags).join(' '));
						renderInner(data.datum, translated, data.tags.concat(parenttags));
						closeParagraph();
						return;
					}
				}
				for (let name of PARAGRAPH_CLOSING_ELEMENTS) {
					if (uniquelyhas(name)) {
						renderInner(data.datum, translated, data.tags.concat(parenttags));
						closeParagraph();
						return;
					}
				}
				for (let name of PARAGRAPH_OPENING_ELEMENTS) {
					if (uniquelyhas(name)) {
						openParagraph(data.tags.concat(parenttags).join(' '));
						renderInner(data.datum, translated, data.tags.concat(parenttags));
						return;
					}
				}
				renderInner(data.datum, translated, parenttags);
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
