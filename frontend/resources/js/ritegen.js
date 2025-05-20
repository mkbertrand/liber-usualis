// Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

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
	data = data.replaceAll(/\//g, '<br>');

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


function renderinner(data, translated = null, translationpool = null, parenttags, options) {
	let tran = null;

	if (translationpool != null && typeof data === 'object' && 'tags' in data) {
		tran = translationpool[data['tags'].join('+')];
	};
	if (tran != null) {
		translated = tran['datum'];
	};

	try {
		if (typeof data === 'object' && 'tags' in data) {
			if (data['tags'].includes('nomen-ritus')) {
				if (typeof (data['datum']) === 'string') {
					return '<h2 class="rite-name">' + data['datum'] + '</h2>';
				}
				nom = data['datum'][1];
				if (typeof data['datum'][1] === 'object')
					nom = typeof data['datum'][1]['datum'][1] === 'object' ? data['datum'][1]['datum'][0] + data['datum'][1]['datum'][1]['datum']: data['datum'][1]['datum'];
				return '<h2 class="rite-name">' + data['datum'][0] + nom + '</h2>';
			} else if (Array.isArray(data['datum']) && (data['tags'].includes('responsorium') || data['tags'].includes('responsorium-breve'))) {
				let ret = '';
				for (i in data['datum']) {
					ret += unpack(data['datum'][i]);
				}
				data['datum'] = ret;
			} else if (['epiphania', 'festum', 'nocturna-iii', 'psalmus-i'].every(i => data['tags'].includes(i))) {
				antiphon = renderinner(data['datum'][2], null, null, parenttags, options);
				return `<p class="rite-text epiphania-venite epiphania-venite-incipit">${stringrender(data['datum'][0])}<br>${stringrender(data['datum'][1])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][3])}<br>${stringrender(data['datum'][4])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][6])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][8])}<br>${stringrender(data['datum'][9])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][11])}<br>${stringrender(data['datum'][12])}</p>${antiphon}<p class="rite-text epiphania-venite">${stringrender(data['datum'][14]['datum'])}</p>`
			} else if (data['tags'].includes('lectio')) {
				// Basically just figuring out whether this is the first, second, or third Reading of a Nocturne.
				if (Array.isArray(data['datum']) && data['datum'].length == 4) {
					return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][0])}</p><p class="rite-text evangelium-matutini ${data['tags'].join(' ')}">${stringrender(data['datum'][1])}</p><p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][2])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'][3])}</p>`	
				} else if (!data['tags'].includes('lectio-i')) {
					data['tags'].push('lectio-sequens');
				} else if (Array.isArray(data['datum']) && data['datum'].length == 2) {
					return `<p class="rite-text lectionis-titulum ${data['tags'].join(' ')}">${stringrender(data['datum'][0])}</p><p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'][1])}</p>`	
				} else {
					return `<p class="rite-text lectio-incipiens ${data['tags'].join(' ')}">${stringrender(data['datum'])}</p>`	
				}
			} else if (data['tags'].includes('hymnus') && data['tags'].includes('te-deum') && !options['chant']) {
				return `<p class="rite-text hymnus hymnus-te-deum">${stringrender(data['datum'].join('/'))}</p>`;
			}
		}
	} catch(err) {
		console.log(err);
		console.log("Some objects failed to render correctly.");
	}
	if (typeof data === 'object' && Array.isArray(data)) {
		let ret = '';
		for (let i = 0, count = data.length; i < count; i++) {
			ret += renderinner(data[i], Array.isArray(translated) && translated.length == count ? translated[i] : null, translationpool, parenttags, options);
		};
		return ret;

	} else if (typeof data === 'object' && options['chant'] && 'src' in data && data['src'] != undefined && !(options['disabletrivialchant'] && data['tags'].some(tag => trivialchants.includes(tag)))) {
		return `<gabc-chant id="/chant/${data['src']}" tags="${data['tags'].concat(parenttags).join('+')}"></gabc-chant>`;

	} else if (typeof data === 'object') {
		if ('tags' in data && data['tags'].join(' ').includes('/psalmi/')) {
			data['datum'] = data['datum'].replace(/^\d+\s/, '');
			data['tags'].push('psalmus');
		}

		if ('tags' in data && data['tags'].join(' ').includes('canticum')) { data['tags'].push('canticum'); }
		return '<div class="rite-item' + ('tags' in data ? ' ' + data['tags'].join(' ') : '') + '">' + renderinner(data['datum'], translated, translationpool, ('tags' in data ? data['tags'].concat(parenttags) : parenttags), options) + '</div>';

	} else if (typeof data === 'string') {
		return `<p class="rite-text ${parenttags.join(' ')}">${stringrender(data)}</p><p class="rite-text-translation">${translated != null && typeof translated === 'string' ? stringrender(translated) : ''}</p>`
	} else {
		return 'error';
	}
};

// Just guarantees that the return is an array so that the x-for doesn't break
function render(data, chant) {
	options = {chant: chant, disabletrivialchant: true};
	return renderinner(data['rite'], null, data['translation'], [], options);
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

			if (!tags.includes('paschalis') && gabc.includes('<i>T. P.</i>')) {
				gabc = gabc.substring(0, gabc.indexOf('<i>T. P.</i>')).trim();
			}
			if (!tags.includes('septuagesima') && gabc.includes('<i>Post Septuag.</i>')) {
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
				firstsyllable = gabc.match(/[\wáǽœŒéíóúý]+\(/)[0];
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
