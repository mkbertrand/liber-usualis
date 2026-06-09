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

trivialchants = ['deus-in-adjutorium'];
function stringrender(data, translation = false) {
	if (data.match(/^\[.+?\]$/)) {
		return `<span class='rite-text-rubric'>${rubricrender(data.slice(1, -1))}</span>`;
	}
	if (translation) {
		data = data.replaceAll(/^(V\.\s|R\.\sbr.\s|R\.\s)/g, '');
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

function rubricrender(data) {
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

// Obvious
function paragraphclosed(string) {
	// Less than or equal because both equal implies value of -1 which implies no paragraphs at all
	return string.lastIndexOf('</p') >= string.lastIndexOf('<p');
}

riteheaders = {
	'matutinum': 'Ad Matutinum.',
	'laudes': 'Ad Laudes.',
	'prima': 'Ad Primam.',
	'tertia': 'Ad Tertiam.',
	'sexta': 'Ad Sextam.',
	'nona': 'Ad Nonam.',
	'vesperae': 'Ad Vesperas.',
	'completorium': 'Ad Completorium.',
	'psalmi-graduales': 'Psalmi Graduales.',
	'psalmi-poenitentiales': 'Septem Psalmi Pœnitentiales cum Litaniis.',
	'litaniae-sanctorum': 'Litaniæ Sanctorum.',
	'officium-capituli': 'Martyrologium.'
};

function render(data, chant) {
	options = {chant: chant, disabletrivialchant: true};
	usedcommemorations = data['used-commemorations'];
	commmat = data['commemoratio-matutini'] ? data['commemoratio-matutini'][0] : null;

	function renderinner(data, translated = null, parenttags) {
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
				var tags = data.tags;
				tags.sort();
				translated = JSON.parse(JSON.stringify(data.translation.datum));
			}

			if (typeof data === 'object' && Array.isArray(data)) {
				let ret = '';
				for (let i = 0, count = data.length; i < count; i++) {
					plus = renderinner(data[i], Array.isArray(translated) && translated.length == count ? translated[i] : null, parenttags);
					// Obvious function but the reason is that the start of a paragraph may be specified without saying where it should end (intended functionality)
					if (plus.startsWith('<p') && !paragraphclosed(ret)) {
						ret += '</p>';
					}
					// The exclusions in the second condition prevent nested paragraphs - especially important for making sure rubrics above paragraphs are handled right.
					if (paragraphclosed(ret) && !(plus.startsWith('<div') || plus.startsWith('<p') || plus.startsWith('<h'))) {
						if (typeof data[i] === 'string' && data[i].match(/^\[.+?\/\]$/)) {
							ret += `<p class="rite-text ${parenttags.join(' ')} rite-text-rubric rite-text-rubric-above-paragraph">`;
							plus = rubricrender(data[i].slice(1, -2));
						// This condition determines whethere there is any paragraph structure in ret before inserting paragraphs.
						} else if (ret.includes('<p')) {
							ret += `<p class="rite-text ${parenttags.join(' ')}">`;
						}
					}
					ret += plus;
				};
				return ret;
			} else if (typeof data === 'string') {
				if (data == '') {
					return '';
				}
				if (translated != null && typeof translated === 'string' && translated != '') {
					translated = translated.replaceAll(/\[.+?\]/g, '').trim().replaceAll(/([0-9]+)\s/g, '');
					rendered = stringrender(data);
					if (rendered.includes('<br>')) {
						ret = '';
						renderedsplit = rendered.split('<br>');
						translationsplit = stringrender(translated, true).split('<br>');
						// Lines corresponding only to annotations are not accounted for in the translation, so there is an offset
						annotationoffset = 0;
						for (var i = 0; i < renderedsplit.length; i++) {
							if (renderedsplit[i].match(/^<span\sclass='rite-text-rubric'>(.+?)<\/span>/)) {
								ret += renderedsplit[i] + '<br>';
								annotationoffset++;
							} else {
								ret += renderedsplit[i] + (translationsplit[i - annotationoffset] == '' ? '' : `<br><span class="rite-text-translation ${parenttags.join(' ')}">${translationsplit[i - annotationoffset]}</span><br>`);
							}
						}
						return ret;
					}
					return stringrender(data) + (translated == '' ? '<br>' : `<br><span class="rite-text-translation ${parenttags.join(' ')}">${stringrender(translated, true)}</span><br>`);
				} else {
					return stringrender(data) + '<br>';
				}

			} else if (typeof data === 'object' && 'tags' in data) {

				ret = '';
				function makeheader(header, style = 'item-header') {
					return `<h4 class="${style}">${rubricrender(header)}</h4>`;
				}
				function makeheadingannotation(annot) {
					return `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${annot}</p>`;
				}
				var header = '';

				for (i of data.tags) {
					// Additional condition checks if the outside is a wrapper for an inside object of the same label. EG if the object is a hymnus, but the inside object is also a hymnus (which would happen if the outside object had referenced some other day's hymn) it only allows the header of Hymnus to be displayed once
					headers = {
						'psalmi': 'Psalmi.',
						'collecta-primaria': 'Collecta.',
						'invitatorium': 'Invitatorium.',
						'haec-dies': 'Antiphona.'
					};

					if (!('quaesitum' in data)) {
						data.quaesitum = [];
					}
					if (i in headers && !parenttags.includes(i) && data.datum != '') {
						header = makeheader(headers[i]);
					}
					if (data.tags.includes('te-deum') && data.tags.includes('hymnus')) {
						header = makeheader('Hymnus [Te Deum.]');
					} else if (uniquelyhas('capitulum') && !data.tags.includes('pascha')) {
						if (data.quaesitum.includes('officium-parvum-bmv') && !['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							header = makeheader('Capitulum & Versiculus.');
						} else if (['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							header = makeheader('Capitulum, Hymnus & Versiculus.');
						} else {
							header = makeheader('Capitulum, Responsorium Breve & Versiculus.');
						}
					} else if (uniquelyhas('versiculus') && ['officium-defunctorum', 'coena-domini', 'parasceve', 'sabbatum-sanctum'].some(tag => data.tags.includes(tag))) {
						header = makeheader('Versiculus.');
					} else if (uniquelyhas('versiculus') && !parenttags.includes('commemorationes') && !parenttags.includes('antiphona-bmv')) {
						header = makeheadingannotation('Versiculus.');
					} else if (uniquelyhas('absolutio')) {
						header = makeheadingannotation('Absolutio.');
					} else if (uniquelyhas('preces') && !parenttags.includes('officium-capituli')) {
						header = makeheader('Preces.');
					} else if (uniquelyhas('hymnus')) {
						if (['vesperae', 'laudes'].some(tag => parenttags.includes(tag))) {
							header = makeheadingannotation('Hymnus.');
						} else {
							header = makeheader('Hymnus.');
						}
					} else if (uniquelyhas('antiphona-magnificat') && !data.quaesitum.includes('repetita') && !parenttags.includes('commemorationes') && !parenttags.includes('antiphona-nunc-dimittis')) {
						header = makeheader('Canticum B. Mariæ Virg.');
					} else if (uniquelyhas('antiphona-nunc-dimittis') && !data.quaesitum.includes('repetita') && !data.quaesitum.includes('triduum')) {
						header = makeheader('Canticum Simeonis.');
					} else if (uniquelyhas('nunc-dimittis') && (data.quaesitum.includes('triduum') || data.quaesitum.includes('pascha') && !data.quaesitum.includes('i-vesperae'))) {
						header = makeheader('Canticum Simeonis.');
					} else if (uniquelyhas('antiphona-prior-benedictus') && !data.quaesitum.includes('repetita') && !parenttags.includes('commemorationes') && !parenttags.includes('antiphona-magnificat') && !parenttags.includes('antiphona-nunc-dimittis')) {
						header = makeheader('Canticum Zachariæ.');
					} else if (uniquelyhas('confiteor') && parenttags.includes('completorium')) {
						header = makeheader('Confessio.');
					} else if (uniquelyhas('psalmi') && data.quaesitum.includes('matutinum')) {
						header = '';
					}
				}
				// If data.datum is an array, that means that the responsory isn't actually nested down another layer.
				if ((data.tags.includes('responsorium') || data.tags.includes('responsorium-breve')) && Array.isArray(data.datum)) {
					// This is a string if no responsory was found
					if (typeof data.datum[1] === 'string') {
						return stringrender(data.datum[1].replace(", 'incipit'",''));
					}
					if (data.quaesitum.includes('responsorium-breve')) {
						header = makeheadingannotation('Responsorium Breve.');
					} else {
						nn = 1;
						if (data.quaesitum.includes('nocturna-ii')) {
							nn = 2
						} else if (data.quaesitum.includes('nocturna-iii')) {
							nn = 3
						}
						if (data.quaesitum.includes('responsorium-i')) {
							header = makeheadingannotation(`Responsorium ${['I', 'IV', 'VII'][nn - 1]}.`);
						} else if (data.quaesitum.includes('responsorium-ii')) {
							header = makeheadingannotation(`Responsorium ${['II', 'V', 'VIII'][nn - 1]}.`);
						} else if (data.quaesitum.includes('responsorium-iii')) {
							header = makeheadingannotation(`Responsorium ${['III', 'VI', 'IX'][nn - 1]}.`);
						}
					}
					if (translated != null) {
						var trans = translated;
						var alldefined = true;
						for (var i = 0; i < translated.length; i++) {
							if (trans[i] == '') {
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

				} else if (['epiphania', 'festum', 'nocturna-iii', 'psalmus-i'].every(i => data.tags.includes(i))) {
					header = makeheadingannotation('Psalmus XCIV.');
					antiphon = `<p class="rite-text antiphona ${data.tags}">${unpack(data.datum[2], null, null, parenttags)}</p>`;
					return `${header}<p class="rite-text epiphania-venite epiphania-venite-incipit">${stringrender(data.datum[0])}<br>${stringrender(data.datum[1])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[3])}<br>${stringrender(data.datum[4])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[6])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[8])}<br>${stringrender(data.datum[9])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[11])}<br>${stringrender(data.datum[12])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[14].datum)}</p>`

				} else if (data.tags.includes('formula-lectionis') && data.datum != '' && !(typeof data.datum !== 'string' && 'tags' in data.datum && data.datum.tags.includes('formula-lectionis'))) {
					if (data.quaesitum.includes('lectio-brevis')) {
						header = makeheader('Lectio Brevis.');
					} else {
						nn = 1;
						if (data.quaesitum.includes('nocturna-ii')) {
							nn = 2
						} else if (data.quaesitum.includes('nocturna-iii')) {
							nn = 3
						}
						if (data.quaesitum.includes('lectio-i')) {
							header = makeheader(`Lectio ${['I', 'IV', 'VII'][nn - 1]}.`);
						} else if (data.quaesitum.includes('lectio-ii')) {
							header = makeheader(`Lectio ${['II', 'V', 'VIII'][nn - 1]}.`);
						} else if (data.quaesitum.includes('lectio-iii')) {
							header = makeheader(`Lectio ${['III', 'VI', 'IX'][nn - 1]}.`);
						}
					}

				} else if (data.tags.includes('lectio')) {
					// Adds extra line of annotation noting that the reading is a commemoration (i.e. not a continuation of the previous readings).
					annotation = '';
					if (data.tags.includes('lectio-commemorationis') || typeof data.datum == 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('lectio-commemorationis')) {
						annotation = `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${abbreviateName(commmat)}</p>`;
					}

					reading = unpack(data);
					if (!(typeof data.datum === 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('commemoratio-matutini'))) {
						if (!translated) {
							if (typeof data === 'object' && 'datum' in data && typeof data.datum === 'object' && 'translation' in data.datum) {
								translated = unpack(data.datum.translation);
							} else {
								translated = Array(reading.length).fill('', 0);
							}
						}

						// Readings have initial letters, but the first-letter pseudoclass is applied to the first letter of a paragraph. Therefore the reading's annotation needs to be in a separate paragraph.
						function annotate(reading, translated, cssclasses) {
							annotation = reading.match(/^\[.+?\]\//g);
							if (annotation) {
								reading = reading.replace(/^\[.+?\]\//g,'');
								annotation = annotation[0].slice(1, -2);
								return `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${rubricrender(annotation)}</p><p class="rite-text ${cssclasses}">${renderinner(reading, translated, [])}`
							}
							return `<p class="rite-text ${cssclasses}">${renderinner(reading, translated, [])}`
						}

						// For the Lamentations of the Sacred Triduum.
						if (data.quaesitum.includes('sabbatum-sanctum') && data.quaesitum.includes('nocturna-i') && data.quaesitum.includes('lectio-iii')) {
							reading = [reading[0], reading[1] + '<br>' + reading[2].replace(/^(.)/, '<span class="red">\$1</span>')];
						} else if (data.quaesitum.includes('triduum') && data.quaesitum.includes('nocturna-i')) {
							title = '';
							if (data.quaesitum.includes('lectio-i')) {
								title = `<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${stringrender(reading[0])}</p>`;
								reading = reading.slice(1);
							}
							annotation = reading[0].match(/^\[.+?\]\//g);
							if (annotation) {
								reading[0] = reading[0].replace(/^\[.+?\]\//g,'');
								annotation = `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${rubricrender(annotation[0].slice(1, -2))}</p>`;
							} else {
								annotation = '';
							}
							body = reading.slice(0, -1).map((i) => stringrender(i).replace(/^(.)(.+?\.\s)(.)/, '<span class="red">\$1</span>\$2<span class="red">\$3</span>')).join('<br>') + '<br>' + reading[reading.length - 1].replace(/^(.)/, '<span class="red">\$1</span>');
							return title + annotation + `<p class="rite-text lectio-sequens">${body}</p>`;
						}

						// For the first reading from a Homily.
						if (Array.isArray(reading) && reading[0].length < 100 && reading[0].includes('Evangélii')) {
							return `${annotation}<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${renderinner(reading[0], translated[0], [])}</p>${annotate(reading[1], translated[1], 'evangelium-matutini ' + data.tags.join(' '))}</p><p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${renderinner(reading[2], translated[2], [])}</p>${annotate(reading.slice(3).map((re, i) => i == 0 ? re : re.replace(/\]\//, '] ')).join(' &para; '), translated[3] != '' ? translated.slice(3).join(' &para; ') : '', 'lectio-incipiens ' + data.tags.join(' '))}`
						// Cheeky heuristic to guess if the first item is a title or if this reading is really some conjoined readings.
						} else if (Array.isArray(reading) && reading[0].length < 100) {
							return `${annotation}<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${renderinner(reading[0], translated[0], [])}</p>${annotate(reading.slice(1).join(' &para; '), translated[1] != '' ? translated.slice(1).join(' &para; ') : '', (data.quaesitum.includes('lectio-i') ? 'lectio-incipiens ' : 'lectio-sequens ') + data.tags.join(' '))}`
						// Note that an untitled reading may still be a first reading. This is due to the fact that most Saints lives are begun without title.
						} else {
							if (Array.isArray(reading)) { reading = reading.join(' &para; '); translated = translated[0] != '' ? translated.join(' &para; ') : '';};
							return annotation + annotate(reading, translated, (data.quaesitum.includes('lectio-i') ? 'lectio-incipiens ' : 'lectio-sequens ') + data.tags.join(' '));
						}
					}

				} else if (data.tags.includes('commemorationes')) {

					// If there are no Commemorations. data.datum.length will never equal 1 since even if there is only a single Commemoration, its Collect's Termination will be present as a separate element.
					if (data.datum.length == 0) {
						return '';
					}

					var ret = makeheader('Commemorationes.');

					// Last two items in the data.datum array are the final Commemoration and the Termination of that Commemoration's collect.
					for (var i = 0; i < data.datum.length - 2; i++) {
						// Regex statement adds heading annotation inside of the commemoration's div rather than before it.
						ret += renderinner(data.datum[i], translated, data.tags.concat(parenttags)).replace(/(<div.+?>)(.+)/, `$1${makeheadingannotation(abbreviateName(usedcommemorations[i][0]))}$2`);
					}
					data.datum.at(-2).tags = data.datum.at(-2).tags.map((tag) => tag == 'formula-commemorationis' ? 'commemoratio-finalis' : tag);
					ret += `<div class="rite-item formula-commemorationis">${makeheadingannotation(abbreviateName(usedcommemorations.at(-1)[0]))}${renderinner(data.datum[i], translated, data.tags.concat(parenttags))}${renderinner(data.datum.at(-1), translated, data.tags.concat(parenttags))}</div>`;
					return ret;
				} else if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disabletrivialchant'] && data.tags.some(tag => trivialchants.includes(tag)))) {
					ret = `<gabc-chant id="/chant/${data['src']}" tags="${data.tags.concat(parenttags).join('+')}"></gabc-chant>`;
					if (data.tags.includes('hymnus') && data.tags.includes('te-deum')) {
						ret = makeheader('Te Deum') + ret;
					}
					return ret;

				} else if (data.tags.join(' ').includes('/psalmi/')) {
					headers = data.datum.match(/\[.+?\]\n/g);
					for (i of headers) {
						newheader = i.slice(1, -2).replace(':', '. ') + '.';
						numeral = newheader.match(/\s([IVXLC]+)[\s|\.]/);
						if (numeral != null) {
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
						data.datum = data.datum.replace(i, '[' + newheader + ']\n');
					}
					header = makeheadingannotation(data.datum.split('\n')[0].slice(1, -1));
					data.datum = data.datum.substring(data.datum.indexOf('\n') + 1).replace(/^\d+\s/, '').split('\n');
					translated = translated == null ? null : translated.split('\n').slice(1);
					if (parenttags.includes('preces')) {
						data.tags.push('textus-psalmi-precibus');
					} else {
						data.tags.push('textus-psalmi');
					}

				} else if (data.tags.includes('nocturna')) {
					if (data.quaesitum.includes('nocturna-i')) {
						header = makeheader('Nocturnus I.', 'section-header');
					} else if (data.quaesitum.includes('nocturna-ii')) {
						header = makeheader('Nocturnus II.', 'section-header');
					} else if (data.quaesitum.includes('nocturna-iii')) {
						header = makeheader('Nocturnus III.', 'section-header');
					} else {
						header = makeheader('Nocturnus.', 'section-header');
					}
				} else if (data.tags.includes('ritus')) {
					for (i of data.tags) {
						if (i in riteheaders && !parenttags.includes(i)) {
							header = makeheader(riteheaders[i], 'section-header');
						}
					}
					if (data.tags.includes('antiphona-bmv')) {
						header = makeheader('Antiphona B.M.V.');
					}
				} else if (data.tags.includes('martyrologium')) {
					ret = `<p class="rite-text martyrologium">${stringrender(unpack(data.datum[0]))} ${stringrender(unpack(data.datum[1]))}</p>`;
					prae = unpack(data.datum[2]);
					if (prae != '') {
						ret += `<p class="rite-text martyrologium">${stringrender(prae)}</p>`;
					}
					martyrology = unpack(data.datum[3]);
					if (typeof martyrology === 'string') {
						ret += `<p class="rite-text martyrologium">${stringrender(martyrology)}</p>`;
					} else {
						for (i of unpack(data.datum[3])) {
							ret += `<p class="rite-text martyrologium">${stringrender(i)}</p>`;
						}
					}
					return ret + `<p class="rite-text martyrologium">${stringrender(unpack(data.datum[4]))}<br>${stringrender(unpack(data.datum[5]))}</p>`;
				}

				if (uniquelyhas('hymnus') && !data.tags.includes('te-deum')) {
					if (unpack(data.datum) == '') {
						return '';
					}
					else if (typeof unpack(data.datum) === 'string' && unpack(data.datum).startsWith('[')) {
						return stringrender(unpack(data.datum));
					}
					return `${header}<div class="rite-item ${data.tags.join(' ')}">` + unpack(data.datum).map((par) => `<p class="rite-text ${data.tags.join(' ')}">${renderinner(par, translated, data.tags.concat(parenttags))}</p>`).join('') + '</div>';
				}

				ret = renderinner(data.datum, translated, data.tags.concat(parenttags));
				if (ret == '') {
					return '';
				}

				dived = ['aperi-domine', 'sacrosanctae', 'ritus', 'invitatorium', 'nocturna', 'psalmi', 'preces', 'collecta-primaria', 'formula-commemorationis']
				if (dived.some(i => data.tags.includes(i))) {
					annotation = ret.match(/^<span\sclass='rite-text-rubric'>(.+?)<\/span><br>/);
					if (annotation == null) {
						if (!(ret.startsWith('<p') || ret.startsWith('<div'))) {
							ret = `<p class="rite-text ${data.tags.concat(parenttags).join(' ')}">` + ret;
						}
						ret = `${header}<div class="rite-item ${data.tags.concat(parenttags).join(' ')}">${ret}`;
						return paragraphclosed(ret) ? ret + '</div>' : ret + '</p></div>'
					} else {
						ret = ret.replace(/^<span\sclass='rite-text-rubric'>(.+?)<\/span><br>/,'');
						ret = paragraphclosed(ret) ? ret + '</div>' : ret + '</p></div>'
						return `${header}<div class="rite-item"><p class="rite-text-rubric rite-text-rubric-above-paragraph">${annotation[1]}</p><p class="rite-text ${data.tags.join(' ')}">${ret}`;
					}
				}

				// Hymnus condition essentially picks for Te Deum since all other Hymns are handled for in another condition and returned.
				fullparagraph = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'responsorium', 'responsorium-breve', 'versiculus', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-dirigere', 'rubricum', 'hymnus'];
				if ((fullparagraph.some(i => uniquelyhas(i)) || (data.tags.includes('triduum') && data.tags.includes('collecta'))) && !parenttags.includes('sacrosanctae')) {
					if (!ret.startsWith('<p')) {
						ret = `<p class="rite-text ${data.tags.concat(parenttags).join(' ')}">` + ret;
					}
					return `${header}${ret}</p>`;
				}

				closeparagraph = ['gloria-versorum'];
				if (closeparagraph.some(i => uniquelyhas(i))) {
					return `${ret}</p>`;
				}

				openparagraph = ['capitulum', 'absolutio', 'pater-noster-clara-voce', 'pater-noster-semisecreta', 'credo-semisecreta', 'confiteor', 'oratio-sanctae-mariae', 'textus-psalmi-precibus', 'commemoratio-finalis'];
				if (openparagraph.some(i => uniquelyhas(i)) || (uniquelyhasbottom('collecta') && !data.tags.includes('terminatio'))) {
					// It may seem suspicious because of nested references and the like, but we are taking advantage of the fact that the paragraph will never have more divs or the like nested in side - so if there's an annotation, it will be the first thing there.
					annotation = ret.match(/^<span\sclass='rite-text-rubric'>(.+?)<\/span><br>/);
					if (annotation == null) {
						if (!ret.startsWith('<p')) {
							ret = `<p class="rite-text ${data.tags.join(' ')}">` + ret;
						}
						return header + ret;
					} else {
						ret = ret.replace(/^<span\sclass='rite-text-rubric'>(.+?)<\/span><br>/,'');
						return `${header}<p class="rite-text-rubric rite-text-rubric-above-paragraph">Capitulum. ${annotation[1]}</p><p class="rite-text ${data.tags.join(' ')}">${ret}`;
					}
				}
				return header + ret;
			} else {
				return 'error';
			}
		} catch(err) {
			console.log(err);
			console.log(data);
			console.log("Some objects failed to render correctly.");
		}
	};

	return renderinner(data['rite'], null, []);
};
