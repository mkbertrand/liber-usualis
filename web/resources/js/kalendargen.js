litterae = ['<span class="red">A</span>', 'b', 'c', 'd', 'e', 'f', 'g'];
n25 = '<span style="color:black">25. </span>';
epact = [
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', n25 + 'xxvi', 'xxv, xxiv', 'xxiii', 'xxii', 'xxi', 'xx', 'xix', 'xviii', 'xvii', 'xvi', 'xv', 'xiv', 'xiii', 'xii', 'xi', 'x', 'ix', 'viii', 'vii', 'vi', 'v', 'iv', 'iii', 'ii', 'i',
	'*', 'xxix', 'xxviii', 'xxvii', 'xxvi', n25 + 'xxv', 'xxiv', 'xxiii', 'xxii', 'xxi', '<span style="color:black">19. </span> xx'
];
function epact(e) {
	return `<span class='red'>${epact[e]}</span>`;
}

months = ['januarii', 'februarii', 'martii', 'aprilis', 'maji', 'junii', 'julii', 'augusti', 'septembris', 'octobris', 'novembris', 'decembris'];
dates = ['pridie-', 'ad-ii-', 'ad-iii-', 'ad-iv-', 'ad-v-', 'ad-vi-', 'ad-vii-', 'ad-viii-', 'ad-ix-', 'ad-x-', 'ad-xi-', 'ad-xii-', 'ad-xiii-', 'ad-xiv-', 'ad-xv-', 'ad-xvi-', 'ad-xvii-', 'ad-xviii-', 'ad-xix-'];
function occurrencename(name) {
	if (name.length == 1) {
		name = name[0];
	}

	if (!name.includes('-')) {
		return name;
	} else {
		return gregoriandate(name);
	}
}

function abbreviateName(name) {
	if (name.includes('infra Octavam')) {
		return 'De Octava';
	}
	return name.replaceAll('Apostoli', 'Apost.').replaceAll('Evangelistæ', 'Evang.').replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.');
}

function abbreviateComm(name) {
	return name.replace(/^.+ infra Octavam/, 'Oct.').replaceAll('Apostoli', 'Apost.').replaceAll('Evangelistæ', 'Evang.').replaceAll('Martyris', 'Mart.').replaceAll('Martyrum', 'Mm.').replaceAll('Confessoris', 'Conf.').replaceAll('Episcopi', 'Ep.').replaceAll('Pontificum', 'Pont.').replaceAll('Ecclesiæ Doctoris', 'Eccl. Doct.').replaceAll('Virginis', 'Virg.').replaceAll('Viduæ', 'Vid.').replaceAll('Sociorum', 'Soc.');
}

function abbreviateOcc(name) {
	return name.replaceAll('Dominica', 'Dom.').replaceAll('Hebdomadam', 'Hebd.');
}

function dateabbreviation(occurrences) {
	name = '';
	if (typeof occurrences === 'string') {
		return '';
	} else {
		for (var i = 0; i < occurrences.length; i++) {
			for (var j = 0; j < occurrences[i].length; j++) {
				if (occurrences[i].includes('tempus') && months.some(month => occurrences[i][j].includes('-' + month))) {
					name = occurrences[i][j];
				}
			}
		}
	}
	if (name.includes('pridie')) {
		return '<span class="red">Prid.</span>';
	} else if (name.includes('kalendae')) {
		return '<span class="red">Kal.</span>';
	} else if (name.includes('nonae')) {
		return '<span class="red">Non.</span>';
	} else if (name.includes('idus') && !name.includes('ad-')) {
		return '<span class="red">Idib.</span>';
	} else {
		return name.split('-')[1];
	}
}

function gregoriandate(name) {
	month = '';
	monthnumber = -1;
	for (var i = 0; i < 12; i++) {
		if (name.includes(months[i])) {
			month = months[i];
			monthnumber = i;
			break;
		}
	}
	day = 0;
	// Basically these months are called pleni menses and have the Nones on the 7th and the Ides on the 15th instead of the Nones on the 5th and the Ides on the 13th.
	plenus = ['martii', 'maji', 'julii', 'octobris'].includes(month);
	if (name.includes('kalendae')) {
		day = 1;
	} else if (name.includes('nonae')) {
		day = plenus ? 7 : 5;
	} else if (name.includes('idus')) {
		day = plenus ? 15: 13;
	} else {
		offset = 0;
		for (var i = 0; i < dates.length; i++) {
			if (name.includes(dates[i])) {
				offset = i + 1;
				break;
			}
		}
		if (name.includes('kalendas')) {
			lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
			day = lengths[monthnumber] - offset + 1;
			month = months[(month + 11) % 12];
			monthnumber = (monthnumber + 11) % 12;
		} else if (name.includes('nonas')) {
			day = (plenus ? 7 : 5) - offset;
		} else {
			day = (plenus ? 15 : 13) - offset;
		}
	}
	return [monthnumber + 1, day];
}

const MONTH_TITLES = {'01': 'Januarius.', '02': 'Februarius.', '03': 'Martius.', '04': 'Aprilis.', '05': 'Majus.', '06': 'Junius.', '07': 'Julius.', '08': 'Augustus.', '09': 'September.', '10': 'October.', '11': 'November.', '12': 'December.'};
const KALENDAR_NOTES = {
	'2001-02-28': `<span class='red'>In anno bissextili mensis Febr. est dierum <span style='color:black'>29.</span> et festum S. Mathiæ celebratur die <span style='color:black'>25.</span> Febr. et bis dicitur <span style='color:black'>sexto Kalendas,</span> id est die <span style='color:black'>24.</span> et die <span style='color:black'>25.</span> et littera Dominicalis, quæ assumpta fuit in mense Januario, mutatur in præcedentem; ut si in Januario littera Dominicalis fuerit <span style='color:black'>A,</span> mutatur in præcedentem, quæ est <span style='color:black'>g.</span> etc; et littera <span style='color:black'>f.</span> bis servit, <span style='color:black'>24.</span> et <span style='color:black'>25.</span></span>`,
	'2001-12-31': `<span class='red'>Hæc Epacta <span style='color:black'>19.</span> nigra numquam est in usu, nisi quando eodem anno concurrit cum Aureo numero <span style='color:black'>xix.</span></span>`
};

// Rows of the kalendar in display order: [date, occurrences] for each day, preceded by a month title on the
// first of each month and followed by any note. Title and note rows are [key, html], with key ending in '-excluded'.
function kalendarRows(skeleton) {
	let rows = [];
	Object.entries(skeleton).forEach(([date, occurrences], index) => {
		if (/\d{4}-\d{2}-01/.test(date)) {
			rows.push([date + '-excluded', `<h4 class='month-name-title'>${MONTH_TITLES[date.split('-')[1]]}</h4>`]);
		}
		// Dominical letter cycles through the week; the epact index counts days from the start of the year
		rows.push([date, [...occurrences, ['littera', index % 7, index]]]);
		if (KALENDAR_NOTES[date]) {
			rows.push([date + '-excluded', KALENDAR_NOTES[date]]);
		}
	});
	return rows;
}

function deviseentry(entry) {
	let tags = typeof entry.names === 'string' ? [entry.tags] : entry.tags;
	let names = typeof entry.names === 'string' ? [entry.names] : entry.names;
	let ret = abbreviateName(names[0]);
	if (tags[0].includes('commemoratio')) {
		ret = `${ret}. <span class='red'>commem.</span>`;
	} else if (tags[0].includes('duplex-i-classis')) {
		ret = `<span class='red'>${ret}. </span>dupl. 1. class.`;
	} else if (tags[0].includes('duplex-ii-classis')) {
		ret = `<span class='red'>${ret}. </span>dupl. 2. class.`;
	} else if (tags[0].includes('duplex-majus')) {
		ret = `<span class='red'>${ret}. </span>dupl. maj.`;
	} else if (tags[0].includes('duplex-minus')) {
		ret = `${ret}. <span class='red'>dupl.</span>`;
	} else if (tags[0].includes('semiduplex') && !tags[0].includes('infra-octavam')) {
		ret = `${ret}. <span class='red'>semidupl.</span>`;
	}
	if (tags.length > 1) {
		ret += ', comm. ' + names.slice(1).map(abbreviateComm).join(', ');
	}
	return ret + '.';
}

function makeentry(kalendar, occurrences) {
	// Month titles and notes are already markup
	if (typeof occurrences === 'string') {
		return occurrences;
	}
	let ret = '';
	for (let occurrence of occurrences) {
		for (let entry of kalendar) {
			if (entry.occurrence.every(tag => occurrence.includes(tag))) {
				if (occurrence.includes('tempus')) {
					ret += deviseentry(entry);
				} else {
					ret += `<br /><span class='red'>${abbreviateOcc(entry['occurrence-name'])}.</span> ${deviseentry(entry)}`;
				}
			}
		}
	}
	return ret.replaceAll('..', '.').replaceAll('.</span>.', '.</span>');
}

function kalendarCell(html, extraClass) {
	let cell = document.createElement('td');
	cell.className = 'kalendar-table-entry' + (extraClass ? ' ' + extraClass : '');
	cell.innerHTML = html;
	return cell;
}

async function renderKalendar(table) {
	let response = await fetch('/api/kalendar');
	let json = await response.json();
	for (let [date, occurrences] of kalendarRows(json.skeleton)) {
		let row = document.createElement('tr');
		if (date.endsWith('-excluded')) {
			row.append(kalendarCell('', 'red kalendar-entry-nowrap'), kalendarCell(''), kalendarCell(''), kalendarCell('', 'date-entry'));
		} else {
			let littera = occurrences.find(item => item[0] == 'littera');
			let dayNumber = kalendarCell('', 'date-entry');
			dayNumber.textContent = parseInt(date.split('-')[2]);
			row.append(kalendarCell(epact[littera[2]], 'red kalendar-entry-nowrap'), kalendarCell(litterae[littera[1]]), kalendarCell(dateabbreviation(occurrences)), dayNumber);
		}
		row.append(kalendarCell(makeentry(json.kalendar, occurrences)));
		table.append(row);
	}
	table.style.display = '';
}
