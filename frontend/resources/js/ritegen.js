// Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

function stringrender(data) {
	data = data.replace(/\//g, '<br>');

	let numbers = data.match(/^[0-9]+\s/gm);

	if (numbers != null) {
		numbers.reverse();
		for (const i of numbers) {
			data = data.replaceAll(i, '<span class=\'verse-number\'>' + i + '</span>');
		}
	}

	data = data.replace(/\n/g, '<br>')
		.replace(/N\./g, '<span class=\'red\'>N.</span>')
		.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
		.replace(/V\./g, '<span class=\'red\'>&#8483;.</span>')
		.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
		.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
		.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
		.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
		.replace(/\*/g, '<span class=\'red\'>&ast;</span>');
	return data;
};


function renderinner(data, chant, translated = null, translationpool = null, incomm = false) {
	let tran = null;

	if (translationpool != null && typeof data === 'object' && 'tags' in data) {
		tran = translationpool[data['tags'].join('+')];
	};
	if (tran != null) {
		translated = tran['datum'];
	};

	if (typeof data === 'object' && 'tags' in data && data['tags'].includes('nomen-ritus')) {
		nom = data['datum'][1];
		if (typeof data['datum'][1] === 'object')
			nom = typeof data['datum'][1]['datum'][1] === 'object' ? data['datum'][1]['datum'][0] + data['datum'][1]['datum'][1]['datum']: data['datum'][1]['datum'];
		return {'content': '<h2 class="rite-name">' + data['datum'][0] + nom + '</h2>'};
	}
	if (typeof data === 'object' && 'tags' in data && data['tags'].includes('responsorium-breve')) {
		incipit = data['datum'][0];
		response = data['datum'][1];
		verse = data['datum'][4];
		gloria = data['datum'].length == 9 ? data['datum'][6] : null;
		data = {src: incipit['src'], tags: data['tags'], datum: 'R. br. ' + incipit['datum'] + ' * ' + response['datum'] + '/R. ' + incipit['datum'] + ' * ' + response['datum'] + '/V. ' + verse['datum'] + '/R. ' + response['datum'] + (gloria === null ? '' : '/V. ' + gloria) + '/R. ' + incipit['datum'] + ' * ' + response['datum']};
	}
	if (typeof data === 'object' && Array.isArray(data)) {
		let ret = [];
		// Ridiculous language requires me to store the count because variable scope doesn't matter apparently.
		for (let i = 0, count = data.length; i < count; i++) {
			const rendered = renderinner(data[i], chant, Array.isArray(translated) && translated.length == count ? translated[i] : null, translationpool, incomm);
			if (Array.isArray(rendered)) {
				// I guess js doesn't actually like for in loops for unclear reasons
				for (let j = 0; j < rendered.length; j++) {
					ret.push(rendered[j]);
				}
			} else {
				ret.push(rendered);
			}
		};
		return ret;
	} else if (typeof data === 'object' && chant && 'src' in data && data['src'] != undefined) {
		if (incomm) {
			data['tags'].push('commemoratio');
		}
		return {chantid: '/chant/' + data['src'], chanttags: data['tags'].join('+')};
	} else if (typeof data === 'object') {
		return renderinner(data['datum'], chant, translated, translationpool, ('tags' in data && data['tags'].includes('commemoratio')));
	} else if (typeof data === 'string') {
	return translated != null && typeof translated === 'string' ? {content: stringrender(data), translation: stringrender(translated)} : {content: stringrender(data)};
	} else {
		return 'error';
	}
};

// Just guarantees that the return is an array so that the x-for doesn't break
function render(data, chant) {
	const rendered = renderinner(data['rite'], chant, null, data['translation']);
	return Array.isArray(rendered) ? rendered : [rendered];
};

async function chomp(id, tags) {
	return fetch(id + '?tags=' + tags).then(data => data.text());
}
