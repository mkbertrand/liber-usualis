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

export function stringRender(text, translation = false) {
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

