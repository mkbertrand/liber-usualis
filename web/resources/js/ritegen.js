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
			ambit = fullambit.map((entry) => ({'name': entry.name, 'content': entry.content.filter((item) => item.where == 'diei' || item.where == 'antiphona-bmv-temporis'), 'id': entry.id}))
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
	included = ['diei', 'antiphona-bmv-temporis'];
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

// Obvious
function paragraphclosed(string) {
	// Less than or equal because both equal implies value of -1 which implies no paragraphs at all
	return string.lastIndexOf('</p') >= string.lastIndexOf('<p');
}

riteheaders = {
	'matutinum': 'Ad Matutinum',
	'laudes': 'Ad Laudes',
	'prima': 'Ad Primam',
	'tertia': 'Ad Tertiam',
	'sexta': 'Ad Sextam',
	'nona': 'Ad Nonam',
	'vesperae': 'Ad Vesperas',
	'completorium': 'Ad Completorium',
	'psalmi-graduales': 'Psalmi Graduales',
	'psalmi-poenitentiales': 'Septem Psalmi Pœnitentiales cum Litaniis',
	'litaniae-sanctorum': 'Litaniæ',
	'officium-capituli': 'Martyrologium'
};
headers = {
	'capitulum': 'Capitulum',
	'hymnus': 'Hymnus',
	'preces': 'Preces',
	'confiteor': 'Confiteor',
	'collecta-primaria': 'Collecta',
	'sacrosanctae': 'Sacrosanctæ',
	'invitatorium': 'Invitatorium',
	'haec-dies': 'Antiphona'
};

function render(data, chant) {
	options = {chant: chant, disabletrivialchant: true};
	translationpool = data.translation;
	names = data['usednames'];

	function renderinner(data, translated = null, parenttags) {
		try {
			if (translationpool != null && typeof data === 'object' && 'tags' in data) {
				var tags = data.tags;
				tags.sort();
				var tran = translationpool[tags.join('+')];
				if (tran != null) {
					translated = JSON.parse(JSON.stringify(tran.datum));
				}
			}

			if (typeof data === 'object' && Array.isArray(data)) {
				let ret = '';
				for (let i = 0, count = data.length; i < count; i++) {
					plus = renderinner(data[i], Array.isArray(translated) && translated.length == count ? translated[i] : null, parenttags);
					// Obvious function but the reason is that the start of a paragraph may be specified without saying where it should end (intended functionality)
					if (plus.startsWith('<p') && !paragraphclosed(ret)) {
						ret += '</p>';
					}
					if (paragraphclosed(ret) && !(plus.startsWith('<div') || plus.startsWith('<p') || plus.startsWith('<h'))) {
						ret += `<p class="rite-text ${parenttags.join(' ')}">`;
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
						translationsplit = stringrender(translated).split('<br>');
						for (var i = 0; i < renderedsplit.length; i++) {
							ret += renderedsplit[i] + (translationsplit[i] == '' ? '' : `<br><span class="rite-text-translation">${translationsplit[i]}</span><br>`);
						}
						return ret;
					}
					return stringrender(data) + (translated == '' ? '<br>' : `<br><span class="rite-text-translation">${stringrender(translated)}</span><br>`);
				} else {
					return stringrender(data) + '<br>';
				}

			} else if (typeof data === 'object' && 'tags' in data) {

				ret = '';
				function makeheader(header, style = 'item-header') {
					return `<h4 class="${style}">${header}</h4>`;
				}
				var header = '';

				for (i of data.tags) {
					// Additional condition checks if the outside is a wrapper for an inside object of the same label. EG if the object is a hymnus, but the inside object is also a hymnus (which would happen if the outside object had referenced some other day's hymn) it only allows the header of Hymnus to be displayed once
					if (i in headers && !parenttags.includes(i) && data.datum != '') {
						header = makeheader(headers[i]);
					}
				}
				// If data.datum is an array, that means that the responsory isn't actually nested down another layer.
				if ((data.tags.includes('responsorium') || data.tags.includes('responsorium-breve')) && Array.isArray(data.datum)) {
					// This is a string if no responsory was found
					if (typeof data.datum[1] === 'string') {
						return data.datum[1].replace(", 'incipit'",'');
					}
					if (data.tags.includes('responsorium-breve')) {
						header = makeheader('Responsorium Breve');
					} else {
						nn = 1;
						if (data.datum[1].tags.includes('nocturna-ii')) {
							nn = 2
						} else if (data.datum[1].tags.includes('nocturna-iii')) {
							nn = 3
						}
						if (data.datum[1].tags.includes('responsorium-i')) {
							header = makeheader('Responsorium ' + ['I', 'IV', 'VII'][nn - 1]);
						} else if (data.datum[1].tags.includes('responsorium-ii')) {
							header = makeheader('Responsorium ' + ['II', 'V', 'VIII'][nn - 1]);
						} else if (data.datum[1].tags.includes('responsorium-iii')) {
							header = makeheader('Responsorium ' + ['III', 'VI', 'IX'][nn - 1]);
						}
					}
					if (translationpool != null && translated != null) {
						var trans = translated;
						var alldefined = true;
						for (var i = 0; i < translated.length; i++) {
							if (trans[i] == '') {
								trans[i] = unpack(translationpool[claw(data.datum[i]).tags.join('+')]);
								if (trans[i] == undefined) {
									alldefined = false;
									break;
								}
							}
						}
						if (alldefined) {
							translated = trans.join('').split('\n');
						} else {
							translated = null;
						}
					}
					data.datum = unpack(data.datum).join('').split('\n');

				} else if (['epiphania', 'festum', 'nocturna-iii', 'psalmus-i'].every(i => data.tags.includes(i))) {
					antiphon = `<p class="rite-text ${data.tags}">${unpack(data.datum[2], null, null, parenttags)}</p>`;
					return `<p class="rite-text epiphania-venite epiphania-venite-incipit">${stringrender(data.datum[0])}<br>${stringrender(data.datum[1])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[3])}<br>${stringrender(data.datum[4])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[6])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[8])}<br>${stringrender(data.datum[9])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[11])}<br>${stringrender(data.datum[12])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data.datum[14].datum)}</p>`

				} else if (data.tags.includes('formula-lectionis') && data.datum != '' && !(typeof data.datum !== 'string' && 'tags' in data.datum && data.datum.tags.includes('formula-lectionis'))) {
					if (!Array.isArray(data.datum) && typeof data.datum !== 'string') {
						btags = data.datum.tags;
					} else {
						btags = typeof data.datum[1].datum === 'object' ?
							data.datum[1].datum.tags.concat(data.datum[1].tags) :
							data.datum[1].tags;
					}
					if (data.datum.length > 3 && typeof data.datum[3] === 'object' && data.datum[3].tags.includes('lectio-brevis')) {
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

				} else if (data.tags.includes('lectio')) {
					reading = unpack(data);
					if (!(typeof data.datum === 'object' && !Array.isArray(data.datum) && data.datum.tags.includes('commemoratio-matutini'))) {
						if (!translated) {
							translated = Array(reading.length).fill('', 0);
						}

						// Readings have initial letters, but the first-letter pseudoclass is applied to the first letter of a paragraph. Therefore the reading's annotation needs to be in a separate paragraph.
						function annotate(reading, translated, cssclasses) {
							annotation = reading.match(/^\[.+?\/\]/g);
							if (annotation) {
								reading = reading.replace(/^\[.+?\/\]/g,'');
								annotation = annotation[0].slice(1, -2);
								return `<p class="rite-text-rubric rite-text-rubric-above-paragraph">${annotation}</p><p class="rite-text ${cssclasses}">${renderinner(reading, translated, [])}`
							}
							return `<p class="rite-text ${cssclasses}">${renderinner(reading, translated, [])}`
						}

						// For the first reading from a Homily
						if (Array.isArray(reading) && reading[0].includes('Evangélii')) {
							return `<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${renderinner(reading[0], translated[0], [])}</p><p class="rite-text evangelium-matutini ${data.tags.join(' ')}">${stringrender(reading[1])}</p><p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${stringrender(reading[2])}</p><p class="rite-text lectio-incipiens ${data.tags.join(' ')}">${stringrender(reading.slice(3).join(' '))}<br>`
						// Cheeky heuristic to guess if the first item is a title or if this reading is really some conjoined readings
						} else if (Array.isArray(reading) && reading[0].length < 100) {
							return `<p class="rite-text lectionis-titulum ${data.tags.join(' ')}">${stringrender(reading[0])}</p><p class="rite-text lectio-incipiens ${data.tags.join(' ')}">${stringrender(reading.slice(1).join(' '))}<br>`
						// Weird structuring but basically this is needed since sometimes readings are begun without title.
						} else if (btags.includes('lectio-i')) {
							if (Array.isArray(reading)) { reading = reading.join(' ')};
							return annotate(reading, translated, 'lectio-incipiens ' + data.tags.join(' '));
						} else {
							if (Array.isArray(reading)) { reading = reading.join(' '); translated = translated.join(' ');};
							return annotate(reading, translated, 'lectio-sequens ' + data.tags.join(' '));
						}
					}

				} else if (data.tags.includes('hymnus') && data.tags.includes('te-deum') && !options['chant']) {
					return `<p class="rite-text hymnus hymnus-te-deum">${stringrender(data.datum.join('/'))}</p>`;
				} else if (data.tags.includes('commemorationes')) {
					var ret = '';
					for (var i = 0; i < data.datum.length - 1; i++) {
						ret += makeheader(names[i + 1]) + renderinner(data.datum[i], translated, data.tags.concat(parenttags));
					}
					return data.datum.length == 0 ? '' : ret + renderinner(data.datum[data.datum.length - 1], translated, data.tags.concat(parenttags));

				} else if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disabletrivialchant'] && data.tags.some(tag => trivialchants.includes(tag)))) {
					return `<gabc-chant id="/chant/${data['src']}" tags="${data.tags.concat(parenttags).join('+')}"></gabc-chant>`;

				} else if (data.tags.join(' ').includes('/psalmi/')) {
					header = makeheader(data.datum.split('\n')[0].slice(1, -1));
					data.datum = data.datum.substring(data.datum.indexOf('\n') + 1).replace(/^\d+\s/, '').split('\n');
					translated = translated == null ? null : translated.split('\n').slice(1);
					data.tags.push('textus-psalmi');

				} else if (data.tags.includes('nocturna')) {
					if (data.tags.includes('nocturna-i')) {
						header = makeheader('Nocturna I', 'section-header');
					} else if (data.tags.includes('nocturna-ii')) {
						header = makeheader('Nocturna II', 'section-header');
					} else if (data.tags.includes('nocturna-iii')) {
						header = makeheader('Nocturna III', 'section-header');
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
				} else if (data.tags.includes('versiculus') && !parenttags.includes('versiculus') && !parenttags.includes('commemorationes') && !parenttags.includes('antiphona-bmv')) {
					header = makeheader('Versiculus');
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
				} else if (['antiphona-bmv', 'antiphona'].every((tag) => data.tags.includes(tag)) && parenttags.includes('completorium')) {
					header = makeheader('Antiphona B.M.V.');
				}

				if (data.tags.includes('hymnus') && !parenttags.includes('hymnus')) {
					if (unpack(data.datum) == '') {
						return '';
					}
					else if (typeof unpack(data.datum) === 'string' && unpack(data.datum).startsWith('[')) {
						return stringrender(unpack(data.datum));
					}
					return `${header}<div class="rite-item ${data.tags.join(' ')}">` + unpack(data.datum).map((par) => `<p class="rite-text ${data.tags.join(' ')}">${renderinner(par, translated, data.tags.concat(parenttags))}</p>`).join('') + '</div>';
				}

				dived = ['aperi-domine', 'sacrosanctae', 'ritus', 'collecta-primaria', 'formula-commemorationis']
				if (dived.some(i => data.tags.includes(i) && !parenttags.includes(i))) {
					ret = `${header}<div class="rite-item ${data.tags.join(' ')}">${renderinner(data.datum, translated, data.tags.concat(parenttags))}`;
					return paragraphclosed(ret) ? ret + '</div>' : ret + '</p></div>'
				}

				fullparagraph = ['pater-noster-secreta', 'ave-maria-secreta', 'credo-secreta', 'deus-in-adjutorium', 'antiphona', 'textus-psalmi', 'responsorium', 'responsorium-breve', 'versiculus', 'pater-noster-semisecreta', 'credo-semisecreta', 'preces', 'confiteor', 'dominus-vobiscum', 'benedicamus-domino', 'fidelium-animae', 'benedictio-finalis', 'formula-lectionis', 'oratio-sanctae-mariae', 'gloria-versorum', 'oratio-dirigere', 'rubricum'];
				if (fullparagraph.some(i => data.tags.includes(i) && !parenttags.includes(i))) {
					ret = renderinner(data.datum, translated, data.tags.concat(parenttags));
					if (ret == '') {
						return '';
					}
					if (!ret.startsWith('<p')) {
						ret = `<p class="rite-text ${data.tags.join(' ')}">` + ret;
					}
					return `${header}${ret}</p>`;
				}

				openparagraph = ['capitulum', 'absolutio'];
				if (openparagraph.some(i => data.tags.includes(i) && !parenttags.includes(i))) {
					ret = renderinner(data.datum, translated, data.tags.concat(parenttags));
					return ret == '' ? '' : `${header}<p class="rite-text ${data.tags.join(' ')}">${ret}`;
				}
				return header + renderinner(data.datum, translated, data.tags.concat(parenttags));
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
