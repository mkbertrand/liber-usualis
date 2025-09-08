months = ['januarii', 'februarii', 'martii', 'aprilis', 'maji', 'junii', 'julii', 'augusti', 'septembris', 'octobris', 'novembris', 'decembris']
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
