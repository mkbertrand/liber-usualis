// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

const MONTHS = ['Januarii', 'Februarii', 'Martii', 'Aprilis', 'Maji', 'Junii', 'Julii', 'Augusti', 'Septembris', 'Octobris', 'Novembris', 'Decembris'];
export function dateHeader(date) {
  date = date.split('-');
  return `<h4 class="date-header">Die ${parseInt(date[2])} ${MONTHS[(parseInt(date[1]) - 1) % 12]} ${date[0]}.</h4>`;
}

export function riteTitle(title, tags, size = 'large') {
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

export function abbreviateName(name) {
	name = name.replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.') + '.';
	name = name.replaceAll(/\.\.$/g, '.');
	return name;
}

export function rubricRender(data) {
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

export function stringRender(text) {
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

export function tags(element) {
  if (typeof element === 'object' && !Array.isArray(element)) {
    return new Set(element.tags);
  } else {
    return new Set();
  }
}

export function quaesitum(element) {
  if (typeof element === 'object' && !Array.isArray(element) && 'quaesitum' in element) {
    return new Set(element.quaesitum);
  } else {
    return tags(element);
  }
}

// It can be readily observed that this is just an extremely primitive version of render()
export function unpack(data) {
	if (typeof data === 'string') {
		return data;
  } else if (data === null) {
    return null;
	} else if (typeof data === 'object') {
		return Array.isArray(data) ? data.map((d) => unpack(d)).flat() : unpack(data.datum);
	}
};

// Digs out nested data recursively (useful for translation)
export function claw(data) {
	if (typeof data.datum === 'string' || Array.isArray(data.datum)) {
		return data;
	} else {
		return claw(data.datum);
	}
}

