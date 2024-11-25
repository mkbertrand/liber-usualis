// Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

function stringrender(data) {
	data = data.replaceAll(/\//g, '<br>');

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


function renderinner(data, chant, translated = null, translationpool = null, parenttags) {
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
		return '<h2 class="rite-name">' + data['datum'][0] + nom + '</h2>';
	}

	if (typeof data === 'object' && 'tags' in data && data['tags'].includes('responsorium-breve')) {
		incipit = data['datum'][0];
		response = data['datum'][1];
		verse = data['datum'][4];
		gloria = data['datum'].length == 9 ? data['datum'][6] : null;
		data = {src: incipit['src'], tags: data['tags'], datum: 'R. br. ' + incipit['datum'] + ' * ' + response['datum'] + '/R. ' + incipit['datum'] + ' * ' + response['datum'] + '/V. ' + verse['datum'] + '/R. ' + response['datum'] + (gloria === null ? '' : '/V. ' + gloria) + '/R. ' + incipit['datum'] + ' * ' + response['datum']};
	}

	if (typeof data === 'object' && Array.isArray(data)) {
		let ret = '';
		// Ridiculous language requires me to store the count because variable scope doesn't matter apparently.
		for (let i = 0, count = data.length; i < count; i++) {
			ret += renderinner(data[i], chant, Array.isArray(translated) && translated.length == count ? translated[i] : null, translationpool, parenttags);
		};
		return ret;

	} else if (typeof data === 'object' && chant && 'src' in data && data['src'] != undefined) {
		return '<gabc-chant id="/chant/' + data['src'] + '" tags="' + data['tags'].concat(parenttags).join('+') + '"></gabc-chant>';

	} else if (typeof data === 'object') {
			if ('tags' in data && data['tags'].join(' ').includes('psalmus')) { data['tags'].push('psalmus'); }
			if ('tags' in data && data['tags'].join(' ').includes('canticum')) { data['tags'].push('canticum'); }
		return '<div class="rite-item' + ('tags' in data ? ' ' + data['tags'].join(' ') : '') + '">' + renderinner(data['datum'], chant, translated, translationpool, ('tags' in data ? data['tags'].concat(parenttags) : parenttags)) + '</div>';

	} else if (typeof data === 'string') {
		return '<p class="rite-text ' + parenttags.join(' ') + '">' + stringrender(data) + '</p><p class="rite-text-translation">' + (translated != null && typeof translated === 'string' ? stringrender(translated) : '') + '</p>';
	} else {
		return 'error';
	}
};

// Just guarantees that the return is an array so that the x-for doesn't break
function render(data, chant) {
	return renderinner(data['rite'], chant, null, data['translation'], []);
};

async function chomp(id, tags) {
	return fetch(id + '?tags=' + tags).then(data => data.text()).then(gabc => {
		gabc = gabc.replace('<v>\\greheightstar</v>', '*');
		mode = undefined;
		if (gabc.includes('mode:')) {
			mode = gabc.substring(gabc.indexOf('mode:') + 5, gabc.indexOf('\n', gabc.indexOf('mode:'))).trim();
			if (mode.endsWith(';')) {
				mode = mode.slice(0, -1);
			}
		}

		// Remove commented text falling before content
		gabc = '%%\n' + gabc.substring(gabc.search(/\([cf]\d\)/));
		gabc = gabc.replaceAll('<sp>V/</sp>.', '<v>\\Vbar</v>').replaceAll('<sp>R/</sp>.', '<v>\\Rbar</v>').replaceAll(/<.?sc>/g, '').replaceAll(/\[.*?\]/g, '');

		if (mode !== undefined) {
			gabc = 'mode:' + mode + ';\n' + gabc;
		}
		if (tags.includes('deus-in-adjutorium')) {
			return gabc.substring(0, gabc.search(/\(Z\-?\)/));

		} else if (tags.includes('antiphona')) {
			euouae = '';
			if (gabc.includes('<eu>')) {
				euouae = gabc.match(/\s<eu>.+/)[0].replaceAll(/<.?eu>/g, '');
				gabc = gabc.substring(0, gabc.search(/<eu>/));
			}

			if (!tags.includes('paschalis') && gabc.includes('<i>T. P.</i>')) {
				gabc = gabc.substring(0, gabc.indexOf(' <i>T. P.</i>'));
			}
			if (!tags.includes('septuagesima') && gabc.includes('<i>Post Septuag.</i>')) {
				gabc = gabc.substring(0, gabc.indexOf(' <i>Post Septuag.</i>'));
			}

			if (tags.includes('intonata')) {
				gabc = gabc.substring(0, gabc.indexOf('*')) + '(::)' + euouae;
			} else if (!(tags.includes('commemoratio') || tags.includes('repetita') || tags.includes('suffragium'))) {
				gabc = gabc + euouae;
			} else {
				gabc = gabc.replace('*', '').split('\n')[2];
				firstsyllable = gabc.match(/\w+\(/)[0];
				gabc = gabc.replace(firstsyllable, firstsyllable.charAt(0).toUpperCase() + firstsyllable.slice(1).toLowerCase());
			}
			
			gabc = (tags.includes('repetita') ? 'initial-style:0;\n' : 'initial-style:1;\n') + gabc;
			return gabc;

		} else if (tags.includes('responsorium-breve')) {
			clef = gabc.substring(0, gabc.indexOf(')') + 1);
			incipit = gabc.match(/\(.\d\)\s(.+?)\s\*/)[1];
			response = gabc.match(/\*\(\W\)\s(.+?)\s\(..\)/)[1];
			verses = [...gabc.matchAll(/<v>\\Vbar<\/v>\.?(\(::\))?\s(.+?)\s\*?\(::\)/g)];
			verse = verses[0][2];
			gloria = verses[1][2];
			return clef + ' ' + incipit + ' *(;) ' + response + ' (::) <v>\\Rbar</v> ' + incipit + ' (;) ' + response + ' (::) <v>\\Vbar</v> ' + verse + ' *(;) ' + response + ' (::) <v>\\Vbar</v> ' + gloria + ' (::) <v>\\Rbar</v> ' + incipit + ' (;) ' + response + ' (::)';

		} else {
			return gabc;
		}
	});
}
