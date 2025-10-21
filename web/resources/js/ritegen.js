// Copyright 2024-2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

class RiteItem {
	constructor(what, where, always) {
		this.what = what;
		this.where = where;
		this.always = always;
	}
}
fullambit = [
	{'name': 'Matutinum & Laudes', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('psalmi-graduales', 'psalmi-graduales', false), new RiteItem('matutinum', 'officium-parvum-bmv', false), new RiteItem('laudes', 'officium-parvum-bmv', false), new RiteItem('matutinum', 'diei', true), new RiteItem('laudes', 'diei', true), new RiteItem('matutinum', 'officium-defunctorum', false), new RiteItem('laudes', 'officium-defunctorum', false), new RiteItem('psalmi-poenitentiales', 'psalmi-poenitentiales', false), new RiteItem('litaniae-sanctorum', 'litaniae-sanctorum', false), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'matutinum'},
	{'name': 'Prima', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('prima', 'diei', true), new RiteItem('prima', 'officium-parvum-bmv', false), new RiteItem('officium-capituli', 'diei', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'prima'},
	{'name': 'Tertia', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('tertia', 'diei', true), new RiteItem('tertia', 'officium-parvum-bmv', false), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'tertia'},
	{'name': 'Sexta', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('sexta', 'diei', true), new RiteItem('sexta', 'officium-parvum-bmv', false), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'sexta'},
	{'name': 'Nona', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('nona', 'diei', true), new RiteItem('nona', 'officium-parvum-bmv', false), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'nona'},
	{'name': 'Vesperæ', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('vesperae', 'officium-parvum-bmv', false), new RiteItem('vesperae', 'diei', true), new RiteItem('vesperae', 'officium-defunctorum', false), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'vesperae'},
	{'name': 'Completorium', 'content': [new RiteItem('aperi-domine', 'diei', true), new RiteItem('completorium', 'diei', true), new RiteItem('completorium', 'officium-parvum-bmv', false), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'completorium'}
];

opbmvambit = [
	{'name': 'Matutinum & Laudes', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('matutinum', 'officium-parvum-bmv', true), new RiteItem('laudes', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'matutinum'},
	{'name': 'Prima', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('prima', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'prima'},
	{'name': 'Tertia', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('tertia', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'tertia'},
	{'name': 'Sexta', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('sexta', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'sexta'},
	{'name': 'Nona', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('nona', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'nona'},
	{'name': 'Vesperæ', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('vesperae', 'officium-parvum-bmv', true), new RiteItem('antiphona-bmv', 'antiphona-bmv-temporis', true), new RiteItem('sacrosanctae', 'officium-parvum-bmv', true)], 'id': 'vesperae'},
	{'name': 'Completorium', 'content': [new RiteItem('aperi-domine', 'officium-parvum-bmv', true), new RiteItem('completorium', 'officium-parvum-bmv', true), new RiteItem('sacrosanctae', 'diei', true)], 'id': 'completorium'}
];

defunctambit = [
	{'name': 'Matutinum & Laudes', 'content': [new RiteItem('aperi-domine', 'officium-defunctorum', true), new RiteItem('matutinum', 'officium-defunctorum', true), new RiteItem('laudes', 'officium-defunctorum', true), new RiteItem('sacrosanctae', 'officium-defunctorum', true)], 'id': 'matutinum'},
	{'name': 'Vesperæ', 'content': [new RiteItem('aperi-domine', 'officium-defunctorum', true), new RiteItem('vesperae', 'officium-defunctorum', true), new RiteItem('sacrosanctae', 'officium-defunctorum', true)], 'id': 'vesperae'}
];

gradualambit = [{'name': 'Psalmi Graduales', 'content': [new RiteItem('psalmi-graduales', 'diei', true)], 'id': 'matutinum'}]
penitentialsambit = [{'name': 'Psalmi Pœnitentiales', 'content': [new RiteItem('psalmi-poenitentiales', 'diei', true)], 'id': 'matutinum'}]

function defineambit(desired, choral = true) {
	switch(desired) {
		case 'omnes':
			ambit = fullambit;
			break;
		case 'officium-parvum-bmv':
			ambit = opbmvambit;
			break;
		case 'officium-defunctorum':
			ambit = defunctambit;
			break;
		case 'psalmi-graduales':
			ambit = gradualambit;
			break;
		case 'psalmi-poenitentiales':
			ambit = penitentialsambit;
			break;
		case 'diei':
			ambit = fullambit.map((entry) => ({'name': entry.name, 'content': entry.content.filter((item) => item.where == 'diei'), 'id': entry.id}))
	}
	if (choral) {
		return ambit;
	} else {
		return ambit.map((entry) => ({
			'name': entry.name,
			'content': (entry.id == 'matutinum' ? entry.content : entry.content.filter((item) => item.what != 'antiphona-bmv')),
			'id': entry.id
		}));
	}
}

function ritelist(daytags, ambit) {
	included = ['diei'];
	if (daytags.some(i => i.includes('officium-parvum-bmv') && !i.includes('omissum'))) {
		included.push('officium-parvum-bmv');
	}
	if (daytags.some(i => i.includes('officium-defunctorum'))) {
		included.push('officium-defunctorum');
	}
	if (daytags.some(i => i.includes('psalmi-graduales'))) {
		included.push('psalmi-graduales');
	}
	if (daytags.some(i => i.includes('psalmi-poenitentiales'))) {
		included.push('psalmi-poenitentiales');
	}
	if (daytags.some(i => i.includes('litaniae-sanctorum'))) {
		included.push('litaniae-sanctorum');
	}

	ret = []

	for (var i = 0; i < ambit.length; i++) {
		lit = [];
		for (var j = 0; j < ambit[i].content.length; j++) {
			// The Antiphon to the Blessed Virgin Mary is never said when the Office of the Dead, Penitential Psalms, or the Litany follow (except as an integral part of Compline)
			if (
				(ambit[i].content[j].always || included.includes(ambit[i].content[j].where))
			&& !(included.includes('officium-defunctorum') && (ambit[i].id == 'vesperae' || ambit[i].id == 'matutinum') && ambit[i].content[j].what == 'antiphona-bmv')
			&& !(included.includes('psalmi-poenitentiales') && ambit[i].id == 'matutinum' && ambit[i].content[j].what == 'antiphona-bmv')
			&& !(included.includes('litaniae-sanctorum') && ambit[i].id == 'matutinum' && ambit[i].content[j].what == 'antiphona-bmv')
			&& !(daytags.some(i => i.includes('triduum')) && ambit[i].content[j].what == 'antiphona-bmv')
			&& !(daytags.some(i => i.includes('triduum')) && ambit[i].content[j].what == 'officium-capituli')
			&& !(daytags.some(i => i.includes('pascha') && i.includes('i-vesperae') && i.includes('duplex-i-classis')) && ambit[i].id == 'vesperae' && (ambit[i].content[j].what == 'antiphona-bmv' || ambit[i].content[j].what == 'aperi-domine' || ambit[i].content[j].what == 'sacrosanctae'))
			) {
				lit.push([ambit[i].content[j].what, ambit[i].content[j].where]);
			}
		}
		ret.push({'name': ambit[i].name, 'content': lit, 'id': ambit[i].id});
	}
	return ret;
}

function riteTitle(data, size = 'large') {
	if (data.rite.tags.includes('sacrosanctae') || data.rite.tags.includes('antiphona-bmv') || data.rite.tags.includes('officium-capituli')) {
		return '';
	}
	var title = data['usednames'][0];
	if (size == 'small') {
		return `<h1 class="small-title">${title}</h1>`;
	} else {
		var subtitle = '';
		if (data['usedprimary'].includes('duplex-i-classis')) {
			subtitle = 'Duplex I Classis';
		} else if (data['usedprimary'].includes('duplex-ii-classis')) {
			subtitle = 'Duplex II Classis';
		} else if (data['usedprimary'].includes('duplex-majus')) {
			subtitle = 'Duplex Majus';
		} else if (data['usedprimary'].includes('duplex-minus')) {
			subtitle = 'Duplex Minus';
		} else if (data['usedprimary'].includes('semiduplex')) {
			subtitle = 'Semiduplex';
		} else if (data['usedprimary'].includes('simplex') || data['usedprimary'].includes('feria')) {
			subtitle = 'Simplex';
		}
		return `<h1 class="large-title">${title}</h1><h2 class="large-subtitle">${subtitle}</h2>`;
	}
}

function abbreviateName(name) {
	return name.replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.');
}

titled = {
	capitulum: 'Capitulum',
	hymnus: 'Hymnus',
	preces: 'Preces',
	confiteor: 'Confiteor'
};

titled['collecta-primaria'] = 'Collecta';
titled['sacrosanctae'] = 'Sacrosanctæ';

// It can be readily observed that this is just an extremely primitive version of render()
function unpack(data) {
	if (typeof data === 'string') {
		return data;
	} else if (typeof data === 'object') {
		return Array.isArray(data) ? data.map((d) => unpack(d)).flat() : unpack(data['datum']);
	}
};

trivialchants = ['deus-in-adjutorium'];
function stringrender(data) {
	data = data.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
		.replaceAll('É', 'E').replaceAll('Í', 'I')
		.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
		.replaceAll('Ý', 'Y');
	data = data.replaceAll(/(?<!<)\//g, '<br>');

	data = data.replaceAll(/([0-9]+)\s/g, '<span class="verse-number">$1 </span>');

	data = data.replace(/\n/g, '<br>')
		.replace(/N\./g, '<span class=\'red\'>N.</span>')
		.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
		.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
		.replace(/V\./g, '<span class=\'red\'>&#8483;.</span>')
		.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
		.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
		.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
		.replace(/\*/g, '<span class=\'red\'>&ast;</span>')
		.replace(/\[(.+?)\]/g, '<span class=\'rite-text-rubric\'>\$1</span>');
	return data;
};

function sectionrender(text, translation, tags) {
	ret = `<p class="rite-text ${tags.join(' ')}">`;
	for (var i = 0; i < text.length; i++) {
		ret += `<span class="rite-text">${stringrender(text[i])}</span><br>`
		if (translation != null) {
			// For stylistic reasons, remove any rubric-text at the start of the translation like line numbers in Psalms or Versicle/Response signs.
			trans = stringrender(translation[i]).replace(/^<span.+?<\/span>/, '').replace(/\[.+?\]/g, '');
			ret += `<span class="rite-text-translation">${trans}</span><br>`;
		}
	}
	return ret + '</p>';
}

function render(data, chant) {
	options = {chant: chant, disabletrivialchant: true};
	translationpool = data.translation;
	names = data['usednames'];

	function renderinner(data, translated = null, parenttags) {
		try {
			if (translationpool != null && typeof data === 'object' && 'tags' in data) {
				tags = data['tags'];
				tags.sort();
				tran = translationpool[tags.join('+')];
				if (tran != null) {
					translated = tran['datum'];
				}
			}

			if (typeof data === 'object' && Array.isArray(data)) {
				let ret = '';
				for (let i = 0, count = data.length; i < count; i++) {
					ret += renderinner(data[i], Array.isArray(translated) && translated.length == count ? translated[i] : null, parenttags);
				};
				return ret;
			} else if (typeof data === 'string') {
				ret = `<p class="rite-text ${parenttags.join(' ')}">${stringrender(data)}</p>`
				if (translated != null && typeof translated === 'string') {
					translated = translated.replaceAll(/\[.+?\]/g, '').trim().replaceAll(/([0-9]+)\s/g, '');
					rendered = stringrender(data);
					if (rendered.includes('<br>')) {
						ret = '';
						renderedsplit = rendered.split('<br>');
						translationsplit = stringrender(translated).split('<br>');
						for (var i = 0; i < renderedsplit.length; i++) {
							ret += `<span class="rite-text ${parenttags.join(' ')} with-translation">${renderedsplit[i]}</span><br><span class="rite-text-translation">${translationsplit[i]}</span><br>`;
						}
						return ret;
					}
					ret = `<p class="rite-text ${parenttags.join(' ')} with-translation">${stringrender(data)}</p>`
					return ret + `<p class="rite-text-translation">${stringrender(translated)}</p>`;
				} else {
					return `<p class="rite-text ${parenttags.join(' ')}">${stringrender(data)}</p>`
				}

			} else if (typeof data === 'object' && 'tags' in data) {
				ret = '';
				function makeheader(header, style = 'item-header') {
					return `<h4 class="${style}">${header}</h4>`;
				}
				header = '';

				for (i of data['tags']) {
					// Additional condition checks if the outside is a wrapper for an inside object of the same label. EG if the object is a hymnus, but the inside object is also a hymnus (which would happen if the outside object had referenced some other day's hymn) it only allows the header of Hymnus to be displayed once
					if (i in titled && !(typeof data['datum'] === 'object' && 'tags' in data['datum'] && data['datum']['tags'].includes(i)) && data['datum'] != '' && header == '') {
						header = makeheader(titled[i]);
					}
				}
				// If data['datum'] is an array, that means that the responsory isn't actually nested down another layer.
				if ((data['tags'].includes('responsorium') || data['tags'].includes('responsorium-breve')) && Array.isArray(data['datum'])) {
					// This is a string if no responsory was found
					if (typeof data['datum'][1] === 'string') {
						return data['datum'][1].replace(", 'incipit'",'');
					}
					if (data['tags'].includes('responsorium-breve')) {
						header = makeheader('Responsorium Breve');
					} else {
						nn = 1;
						if (data['datum'][1]['tags'].includes('nocturna-ii')) {
							nn = 2
						} else if (data['datum'][1]['tags'].includes('nocturna-iii')) {
							nn = 3
						}
						if (data['datum'][1]['tags'].includes('responsorium-i')) {
							header = makeheader('Responsorium ' + ['I', 'IV', 'VII'][nn - 1]);
						} else if (data['datum'][1]['tags'].includes('responsorium-ii')) {
							header = makeheader('Responsorium ' + ['II', 'V', 'VIII'][nn - 1]);
						} else if (data['datum'][1]['tags'].includes('responsorium-iii')) {
							header = makeheader('Responsorium ' + ['III', 'VI', 'IX'][nn - 1]);
						}
					}
					vernacular = null;
					if (translationpool != null && translated != null) {
						trans = translated;
						alldefined = true;
						for (var i = 0; i < translated.length; i++) {
							if (trans[i] == '') {
								tran = translationpool[data['datum'][i]['tags'].join('+')];
								trans[i] = unpack(tran);
								if (trans[i] == undefined) {
									alldefined = false;
									break;
								}
							}
						}
						if (alldefined) {
							vernacular = trans.join('').split('\n');
						}
					}

					return header + sectionrender(unpack(data['datum']).join('').split('\n'), vernacular, data['tags']);

				} else if (['epiphania', 'festum', 'nocturna-iii', 'psalmus-i'].every(i => data['tags'].includes(i))) {
					antiphon = `<p class="rite text ${data['tags']}">${unpack(data['datum'][2], null, null, parenttags)}</p>`;
					return `<p class="rite-text epiphania-venite epiphania-venite-incipit">${stringrender(data['datum'][0])}<br>${stringrender(data['datum'][1])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][3])}<br>${stringrender(data['datum'][4])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][6])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][8])}<br>${stringrender(data['datum'][9])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][11])}<br>${stringrender(data['datum'][12])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][14]['datum'])}</p>`

				} else if (data['tags'].includes('formula-lectionis') && data['datum'] != '' && !(typeof data['datum'] !== 'string' && 'tags' in data['datum'] && data['datum']['tags'].includes('formula-lectionis'))) {
					if (!Array.isArray(data['datum']) && typeof data['datum'] !== 'string') {
						btags = data['datum']['tags'];
					} else {
						btags = typeof data['datum'][1]['datum'] === 'object' ?
							data['datum'][1]['datum']['tags'].concat(data['datum'][1]['tags']) :
							data['datum'][1]['tags'];
					}
					if (btags.includes('lectio-brevis')) {
						header = makeheader('Lectio Brevis');
					} else {
						nn = 1;
						if (btags.includes('nocturna-ii')) {
							nn = 2
						} else if (btags.includes('nocturna-iii')) {
							nn = 3
						}
						if (btags.includes('lectio-i')) {
							header = makeheader('Lectio ' + ['I', 'IV', 'VII'][nn - 1]);
						} else if (btags.includes('lectio-ii')) {
							header = makeheader('Lectio ' + ['II', 'V', 'VIII'][nn - 1]);
						} else if (btags.includes('lectio-iii')) {
							header = makeheader('Lectio ' + ['III', 'VI', 'IX'][nn - 1]);
						}
					}
					return header + renderinner(data['datum'], translated, data['tags'].concat(parenttags));

				} else if (data['tags'].includes('lectio')) {
					const reading = unpack(data);
					if (typeof data['datum'] === 'object' && !Array.isArray(data['datum']) && data['datum']['tags'].includes('commemoratio-matutini')) {
					}
					// Basically just figuring out whether this is the first, second, or third Reading of a Nocturne.
					else if (Array.isArray(reading) && typeof reading[0] !== 'string') {
						return `<p class="rite-text lectio-sequens ${data['tags'].join(' ')}">${stringrender(unpack(reading[0])) + '<br/>' + stringrender(unpack(reading[1]))}</p>`;
					} else if (Array.isArray(reading) && reading.length == 4) {
						return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(reading[0])}</p><p class="rite-text evangelium-matutini ${data['tags'].join(' ')}">${stringrender(reading[1])}</p><p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(reading[2])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(reading[3])}</p>`
					} else if (Array.isArray(reading) && reading.length == 2) {
						return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(reading[0])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(reading[1])}</p>`
					} else if (!btags.includes('lectio-i')) {
						return `<p class="rite-text lectio-sequens ${data['tags'].join(' ')}">${stringrender(unpack(reading))}</p>`
					} else {
						return `<p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(reading)}</p>`
					}

				} else if (data['tags'].includes('hymnus') && data['tags'].includes('te-deum') && !options['chant']) {
					return `<p class="rite-text hymnus hymnus-te-deum">${stringrender(data['datum'].join('/'))}</p>`;
				} else if (data['tags'].includes('commemorationes')) {
					if (data['datum'].length == 0) {
						return '';
					}
					ret = '';
					for (var i = 0; i < data['datum'].length - 1; i++) {
						ret += makeheader(names[i + 1]) + renderinner(data['datum'][i], translated, data['tags'].concat(parenttags));
					}
					ret += renderinner(data['datum'][data['datum'].length - 1], translated, data['tags'].concat(parenttags));
					return ret;

				} else if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disabletrivialchant'] && data['tags'].some(tag => trivialchants.includes(tag)))) {
					return `<gabc-chant id="/chant/${data['src']}" tags="${data['tags'].concat(parenttags).join('+')}"></gabc-chant>`;

				} else if (data['tags'].join(' ').includes('/psalmi/')) {
					header = makeheader(data['datum'].split('\n')[0].slice(1, -1));
					data['datum'] = data['datum'].substring(data['datum'].indexOf('\n') + 1).replace(/^\d+\s/, '');
					return header + sectionrender(data['datum'].split('\n'), translated == null ? null : translated.split('\n').slice(1), data['tags'].concat('textus-psalmi'));

				// For Easter when the Hæc dies is inserted in the place of the Chapter
				} else if (data['tags'].includes('capitulum') && typeof data['datum'] === 'object' && 'tags' in data['datum'] && data['datum']['tags'].includes('haec-dies')) {
					header = makeheader('Antiphona');

				} else if (data['tags'].includes('nocturna')) {
					if (data['tags'].includes('nocturna-i')) {
						header = makeheader('Nocturna I', 'section-header');
					} else if (data['tags'].includes('nocturna-ii')) {
						header = makeheader('Nocturna II', 'section-header');
					} else if (data['tags'].includes('nocturna-iii')) {
						header = makeheader('Nocturna III', 'section-header');
					}
				} else if (data['tags'].includes('ritus')) {
					if (data['tags'].includes('matutinum')) {
						header = makeheader('Ad Matutinum', 'section-header');
					} else if (data['tags'].includes('laudes')) {
						header = makeheader('Ad Laudes', 'section-header');
					} else if (data['tags'].includes('prima')) {
						header = makeheader('Ad Primam', 'section-header');
					} else if (data['tags'].includes('tertia')) {
						header = makeheader('Ad Tertiam', 'section-header');
					} else if (data['tags'].includes('sexta')) {
						header = makeheader('Ad Sextam', 'section-header');
					} else if (data['tags'].includes('nona')) {
						header = makeheader('Ad Nonam', 'section-header');
					} else if (data['tags'].includes('vesperae')) {
						header = makeheader('Ad Vesperas', 'section-header');
					} else if (data['tags'].includes('completorium')) {
						header = makeheader('Ad Completorium', 'section-header');
					} else if (data['tags'].includes('antiphona-bmv')) {
						header = makeheader('Antiphona B.M.V.');
					} else if (data['tags'].includes('psalmi-graduales')) {
						header = makeheader('Psalmi Graduales', 'section-header');
					} else if (data['tags'].includes('psalmi-poenitentiales')) {
						header = makeheader('Septem Psalmi Pœnitentiales cum Litaniis', 'section-header');
					} else if (data['tags'].includes('litaniae-sanctorum')) {
						header = makeheader('Litaniæ', 'section-header');
					} else if (data['tags'].includes('officium-capituli')) {
						header = makeheader('Martyrologium', 'section-header');
					}

				} else if (data['tags'].includes('versiculus')) {
					if (!parenttags.includes('commemorationes')) {
						header = makeheader('Versiculus');
					}
				} else if (data['tags'].includes('martyrologium')) {
					ret = `<p class="rite-text martyrologium">${stringrender(unpack(data['datum'][0]))} ${stringrender(unpack(data['datum'][1]))}</p><p class="rite-text martyrologium">${stringrender(unpack(data['datum'][2]))}</p>`;
					martyrology = unpack(data['datum'][3]);
					if (typeof martyrology === 'string') {
						ret += `<p class="rite-text martyrologium">${martyrology}</p>`;
					} else {
						for (i of unpack(data['datum'][3])) {
							ret += `<p class="rite-text martyrologium">${stringrender(i)}</p>`;
						}
					}
					data['datum'] = ret + `<p class="rite-text martyrologium">${stringrender(unpack(data['datum'][4]))}<br>${stringrender(unpack(data['datum'][5]))}</p>`;
				} else if (['antiphona-bmv', 'antiphona'].every((tag) => data['tags'].includes(tag)) && parenttags.includes('completorium')) {
					header = makeheader('Antiphona B.M.V.');
				}

				if (['deus-in-adjutorium', 'pater-noster-semisecreta', 'credo-semisecreta'].some(i => data['tags'].includes(i))) {
					return `${header}<div class="rite-item${' ' + data['tags'].join(' ')}">${sectionrender(data['datum'], translated, data['tags'].concat(parenttags))}</div>`;
				} else {
					return `${header}<div class="rite-item${' ' + data['tags'].join(' ')}">${renderinner(data['datum'], translated, data['tags'].concat(parenttags))}</div>`;
				}

			} else {
				return 'error';
			}
		} catch(err) {
			console.log(err);
			console.log(data);
			console.log("Some objects failed to render correctly.");
		}
	};

	return renderinner(data['rite'], null, [], data['usednames']);
};

function translation(locale) {
	if (locale == 'en') {
		return ['english'];
	} else if (locale == 'de') {
		return ['deutsch'];
	} else {
		return ['english'];
	}
}
