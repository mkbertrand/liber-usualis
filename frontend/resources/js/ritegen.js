// Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

titled = {
	capitulum: 'Capitulum',
	hymnus: 'Hymnus'
};

titled['collecta-primaria'] = 'Collecta';

function patternpsalmtitle(title) {
	ret = '';
	for (i of title.split(' ')) {
		if (/^[clxvi]+$/.test(i)) {
			ret += ' ' + i.toUpperCase();
		} else {
			ret += ' ' + i[0].toUpperCase() + i.substring(1);
		}
	}

	return ret.substring(1);
}

function unpack(data) {
	if (typeof data === 'string') {
		return data;
	} else if (typeof data === 'object') {
		return unpack(data['datum']);
	}
};

trivialchants = ['deus-in-adjutorium'];
function stringrender(data) {
	data = data.replaceAll('Á', 'A').replaceAll('Ǽ', 'Æ')
		.replaceAll('É', 'E').replaceAll('Í', 'I')
		.replaceAll('Ó', 'O').replaceAll('Ú', 'U')
		.replaceAll('Ý', 'Y');
	data = data.replaceAll(/(?<!<)\//g, '<br>');

	let numbers = data.match(/\s[0-9]+\s/gm);

	if (numbers != null) {
		numbers.reverse();
		for (const i of numbers) {
			data = data.replaceAll(i, '<span class=\'verse-number\'>' + i + '</span>');
		}
	}

	data = data.replace(/\n/g, '<br>')
		.replace(/N\./g, '<span class=\'red\'>N.</span>')
		.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
		.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
		.replace(/V\./g, '<span class=\'red\'>&#8483;.</span>')
		.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
		.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
		.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
		.replace(/\*/g, '<span class=\'red\'>&ast;</span>');
	return data;
};

function renderinner(data, translated = null, translationpool = null, parenttags, options, names) {
	try {
		let tran = null;

		if (translationpool != null && typeof data === 'object' && 'tags' in data) {
			tran = translationpool[data['tags'].join('+')];
		};
		if (tran != null) {
			translated = tran['datum'];
		};

		if (typeof data === 'object' && Array.isArray(data)) {
			let ret = '';
			for (let i = 0, count = data.length; i < count; i++) {
				ret += renderinner(data[i], Array.isArray(translated) && translated.length == count ? translated[i] : null, translationpool, parenttags, options, names);
			};
			return ret;
		}
		if (typeof data === 'object' && 'tags' in data) {
			if (data['tags'].includes('nomen-ritus')) {
				if (typeof (data['datum']) === 'string') {
					return '<h2 class="rite-name">' + data['datum'] + '</h2>';
				}
				nom = data['datum'][1];
				if (typeof data['datum'][1] === 'object')
					nom = typeof data['datum'][1]['datum'][1] === 'object' ? data['datum'][1]['datum'][0] + data['datum'][1]['datum'][1]['datum']: data['datum'][1]['datum'];
				return '<h2 class="rite-name">' + data['datum'][0] + nom + '</h2>';

			} else if ((data['tags'].includes('responsorium') || data['tags'].includes('responsorium-breve')) && Array.isArray(data['datum'])) {
				if (typeof data['datum'][1] === 'string') {
					return data['datum'][1].replace(", 'incipit'",'');
				}
				header = 'Responsorium';
				if (data['tags'].includes('responsorium-breve')) {
					header = 'Responsorium Breve';
				} else {
					nn = 1;
					if (data['datum'][1]['tags'].includes('nocturna-ii')) {
						nn = 2
					} else if (data['datum'][1]['tags'].includes('nocturna-iii')) {
						nn = 3
					}
					if (data['datum'][1]['tags'].includes('responsorium-i')) {
						switch(nn) { case 1: header = 'Responsorium I'; break; case 2: header = 'Responsorium IV'; break; case 3: header = 'Responsorium VII';};
					} else if (data['datum'][1]['tags'].includes('responsorium-ii')) {
						switch(nn) { case 1: header = 'Responsorium II'; break; case 2: header = 'Responsorium V'; break; case 3: header = 'Responsorium VII';};
					} else if (data['datum'][1]['tags'].includes('responsorium-iii')) {
						switch(nn) { case 1: header = 'Responsorium III'; break; case 2: header = 'Responsorium VI'; break; case 3: header = 'Responsorium IX';};
					}
				}
				let ret = '';
				for (i in data['datum']) {
					ret += unpack(data['datum'][i]);
				}
				data['datum'] = ret;
				return `<h4 class="item-header">${header}</h4><div class="rite-item'${data['tags'].join(' ')}'">${renderinner(data['datum'], translated, translationpool, data['tags'].concat(parenttags), options, names)}</div>`;

			} else if (['epiphania', 'festum', 'nocturna-iii', 'psalmus-i'].every(i => data['tags'].includes(i))) {
				antiphon = renderinner(data['datum'][2], null, null, parenttags, options, names);
				return `<p class="rite-text epiphania-venite epiphania-venite-incipit">${stringrender(data['datum'][0])}<br>${stringrender(data['datum'][1])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][3])}<br>${stringrender(data['datum'][4])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][6])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][8])}<br>${stringrender(data['datum'][9])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][11])}<br>${stringrender(data['datum'][12])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][14]['datum'])}</p>`
			} else if (data['tags'].includes('formula-lectionis')) {
				header = 'Lectio';
				if (data['datum'][1]['tags'].includes('lectio-brevis')) {
					header = 'Lectio Brevis';
				} else {
					nn = 1;
					if (data['datum'][1]['tags'].includes('nocturna-ii')) {
						nn = 2
					} else if (data['datum'][1]['tags'].includes('nocturna-iii')) {
						nn = 3
					}
					if (data['datum'][1]['tags'].includes('lectio-i')) {
						switch(nn) { case 1: header = 'Lectio I'; break; case 2: header = 'Lectio IV'; break; case 3: header = 'Lectio VII';};
					} else if (data['datum'][1]['tags'].includes('lectio-ii')) {
						switch(nn) { case 1: header = 'Lectio II'; break; case 2: header = 'Lectio V'; break; case 3: header = 'Lectio VII';};
					} else if (data['datum'][1]['tags'].includes('lectio-iii')) {
						switch(nn) { case 1: header = 'Lectio III'; break; case 2: header = 'Lectio VI'; break; case 3: header = 'Lectio IX';};
					}
				}
				return `<h4 class="item-header">${header}</h4>` + renderinner(data['datum'], translated, translationpool, data['tags'].concat(parenttags), options, names);
			} else if (data['tags'].includes('lectio')) {
				// Basically just figuring out whether this is the first, second, or third Reading of a Nocturne.
				if (Array.isArray(data['datum']) && data['datum'].length == 4) {
					return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][0])}</p><p class="rite-text evangelium-matutini ${data['tags'].join(' ')}">${stringrender(data['datum'][1])}</p><p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][2])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'][3])}</p>`	
				} else if (!data['tags'].includes('lectio-i')) {
					return `<p class="rite-text lectio-sequens ${data['tags'].join(' ')}">${stringrender(data['datum'])}</p>`	
				} else if (Array.isArray(data['datum']) && data['datum'].length == 2) {
					return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][0])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'][1])}</p>`	
				} else {
					return `<p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'])}</p>`
				}
			} else if (data['tags'].includes('hymnus') && data['tags'].includes('te-deum') && !options['chant']) {
				return `<p class="rite-text hymnus hymnus-te-deum">${stringrender(data['datum'].join('/'))}</p>`;
			} else if (data['tags'].includes('commemorationes')) {
				ret = '';
				for (var i = 0; i < data['datum'].length - 1; i++) {
					ret += `<h4 class="item-header">${names[i]}</h4>` + renderinner(data['datum'][i], translated, translationpool, data['tags'].concat(parenttags), options, names);
				}
				ret += renderinner(data['datum'][data['datum'].length - 1], translated, translationpool, data['tags'].concat(parenttags), options, names);
				return ret;
			} else if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disabletrivialchant'] && data['tags'].some(tag => trivialchants.includes(tag)))) {
				return `<gabc-chant id="/chant/${data['src']}" tags="${data['tags'].concat(parenttags).join('+')}"></gabc-chant>`;
			}
		}

		if (typeof data === 'object') {
			header = '';
			if ('tags' in data && data['tags'].join(' ').includes('/psalmi/')) {
				data['datum'] = data['datum'].replace(/^\d+\s/, '');
				for (tag of data['tags']) {
					if (tag.startsWith('/psalmi/')) {
						header = tag.substring(8).replaceAll('-', ' ').split(',')[0];
						if (header.includes(':')) {
							headerspl = header.split(':');
							header = `${patternpsalmtitle(headerspl[0])}<small> ${headerspl[1]}</small>`;
						} else {
							header = patternpsalmtitle(header);
						}
					}
				}
				data['tags'].push('psalmus');
			}

			if ('tags' in data && data['tags'].join(' ').includes('canticum')) {
				data['tags'].push('canticum');
			}
			if (data['tags'].includes('hora')) {
				if (data['tags'].includes('matutinum')) {
					header = 'Ad Matutinum';
				} else if (data['tags'].includes('laudes')) {
					header = 'Ad Laudes';
				} else if (data['tags'].includes('prima')) {
					header = 'Ad Primam';
				} else if (data['tags'].includes('tertia')) {
					header = 'Ad Tertiam';
				} else if (data['tags'].includes('sexta')) {
					header = 'Ad Sextam';
				} else if (data['tags'].includes('nona')) {
					header = 'Ad Nonam';
				} else if (data['tags'].includes('vesperae')) {
					header = 'Ad Vesperas';
				} else if (data['tags'].includes('completorium')) {
					header = 'Ad Completorium';
				}
			} else if (data['tags'].includes('psalmi-poenitentiales')) {
				header = 'Septem Psalmi Pœnitentiales cum Litaniis';
			} else if (data['tags'].includes('psalmi-graduales')) {
				header = 'Psalmi Graduales';
			}
			for (i of data['tags']) {
				if (i in titled) {
					header = titled[i];
				}
			}

			return (header == '' ? '' : `<h4 class="item-header">${header}</h4>`) + `<div class="rite-item'${('tags' in data ? ' ' + data['tags'].join(' ') : '')}'">${renderinner(data['datum'], translated, translationpool, ('tags' in data ? data['tags'].concat(parenttags) : parenttags), options, names)}</div>`;

		} else if (typeof data === 'string') {
			return `<p class="rite-text ${parenttags.join(' ')}">${stringrender(data)}</p><p class="rite-text-translation">${translated != null && typeof translated === 'string' ? stringrender(translated) : ''}</p>`
		} else {
			return 'error';
		}
	} catch(err) {
		console.log(err);
		console.log(data);
		console.log("Some objects failed to render correctly.");
	}
};

// Just guarantees that the return is an array so that the x-for doesn't break
function render(data, chant) {
	options = {chant: chant, disabletrivialchant: true};
	var title;
	for (var i = 0; i < data['day'].length; i++) {
		if (data['day'][i].includes('primarium')) {
			title = data['names'][i];
		}
	}
	return `<h1 class="day-title">${title}</h1>` + renderinner(data['rite'], null, data['translation'], [], options, data['names']);
};

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

			if (!tags.includes('in-tempore-paschali') && gabc.includes('<i>T. P.</i>')) {
				gabc = gabc.substring(0, gabc.indexOf('<i>T. P.</i>')).trim();
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
