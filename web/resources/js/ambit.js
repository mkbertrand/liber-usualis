// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

class Rite {
	constructor(what, where, always) {
		this.what = what;
		this.where = where;
		this.always = always;
	}
}

class Occasion {
	constructor(name, rites, id, title) {
		this.name = name;
		this.rites = rites;
		this.id = id;
		this.title = title;
	}
}

class Ambit {
	constructor(...occasions) {
		if (occasions.length == 1 && Array.isArray(occasions[0])) {
			this.occasions = occasions[0];
		} else {
			this.occasions = occasions;
		}
	}

	idindex(id) {
		for (var i = 0; i < this.occasions.length; i++) {
			if (this.occasions[i].id == id) {
				return i;
			}
		}
		return -1;
	}

	riteList(daytags, occasion) {

		if (typeof occasion === 'string') {
			occasion = this.occasions[this.idindex(occasion)];
		}
		let included = ['diei', 'antiphona-bmv-temporis'];
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

		let lit = [];
		for (let j = 0; j < occasion.rites.length; j++) {
			// The Antiphon to the Blessed Virgin Mary is never said when the Office of the Dead, Penitential Psalms, or the Litany follow (except as an integral part of Compline)
			if (
				(occasion.rites[j].always || included.includes(occasion.rites[j].where))
			&& !(occasion.rites[j].what == 'antiphona-bmv' && (
				(included.includes('officium-defunctorum') && occasion.rites.some(rite => rite.where == 'officium-defunctorum'))
				|| (included.includes('psalmi-poenitentiales') && occasion.rites.some(rite => rite.what == 'psalmi-poenitentiales')) 
				|| (included.includes('litaniae-sanctorum') && occasion.rites.some(rite => rite.what == 'litaniae-sanctorum')) 
				|| (daytags.some(i => i.includes('triduum')))
			))
			&& !(daytags.some(i => i.includes('triduum')) && occasion.rites[j].what == 'officium-capituli')
			&& !(daytags.some(i => i.includes('pascha') && i.includes('i-vesperae') && i.includes('duplex-i-classis')) && occasion.id == 'vesperae' && (occasion.rites[j].what == 'antiphona-bmv' || occasion.rites[j].what == 'aperi-domine' || occasion.rites[j].what == 'sacrosanctae'))
			) {
				lit.push([occasion.rites[j].what, occasion.rites[j].where]);
			}
		}
		return lit;
	}

	fullRiteList(daytags) {
		return this.occasions.map((occasion) => this.riteList(daytags, occasion));
	}

	// In the case that you are switching from one ambit to another, you will want a way to pick which occasion will be selected.
	suggestTransition(oldAmbit) {
		return this.occasions[0].id;
	}

	nextOccasion(current) {
		return this.occasions[(this.idindex(current) + 1) % this.occasions.length];
	}

	// Based on the hour of the day, suggest which occasion should be presented if no external information is available - e.g. if a user loads the page for the first time ever at 9AM, suggest he pray Terce. This is intended to be overwritten manually by individual objects in the Ambit class.
	suggestSelectedOccasion(hour) {
		return this.occasions[0];
	}

	// When switching between ambits with a currently selected occasion in the old ambit, suggest which occasion should be selected within the new ambit.
	slideAmbitOccasion(newAmbit, currentOccasionID) {
		let ind = newAmbit.idindex(currentOccasionID);
		if (ind == -1) {
			return this.occasions[0].id;
		} else {
			return newAmbit.occasions[ind].id;
		}
	}
}

fullAmbit = new Ambit([
	new Occasion('Matutinum & Laudes', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('psalmi-graduales', 'psalmi-graduales', false),
		new Rite('matutinum', 'officium-parvum-bmv', false),
		new Rite('laudes', 'officium-parvum-bmv', false),
		new Rite('matutinum', 'diei', true),
		new Rite('laudes', 'diei', true),
		new Rite('matutinum', 'officium-defunctorum', false),
		new Rite('laudes', 'officium-defunctorum', false),
		new Rite('psalmi-poenitentiales', 'psalmi-poenitentiales', false),
		new Rite('litaniae-sanctorum', 'litaniae-sanctorum', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'matutinum', 'diei'),
	new Occasion('Prima', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('prima', 'diei', true),
		new Rite('prima', 'officium-parvum-bmv', false),
		new Rite('officium-capituli', 'diei', true),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'prima', 'diei'),
	new Occasion('Tertia', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('tertia', 'diei', true),
		new Rite('tertia', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'tertia', 'diei'),
	new Occasion('Sexta', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('sexta', 'diei', true),
		new Rite('sexta', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'sexta', 'diei'),
	new Occasion('Nona', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('nona', 'diei', true),
		new Rite('nona', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'nona', 'diei'),
	new Occasion('Vesperæ', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('vesperae', 'officium-parvum-bmv', false),
		new Rite('vesperae', 'diei', true),
		new Rite('vesperae', 'officium-defunctorum', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'vesperae', 'diei'),
	new Occasion('Completorium', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('completorium', 'diei', true),
		new Rite('completorium', 'officium-parvum-bmv', false),
		new Rite('sacrosanctae', 'diei', true)
	], 'completorium', 'diei')
]);

fullAmbit.suggestSelectedOccasion = function(hour) {
	if (hour < 6) {
		return this.occasions[0];
	} else if (hour < 9) {
		return this.occasions[1];
	} else if (hour < 11) {
		return this.occasions[2];
	} else if (hour < 14) {
		return this.occasions[3];
	} else if (hour < 16) {
		return this.occasions[4];
	} else if (hour < 20) {
		return this.occasions[5];
	} else {
		return this.occasions[6];
	}
}

class SingleAmbit extends Ambit {
	constructor(desired) {
		super(
			new Occasion('Matutinum & Laudes', [
				new Rite('aperi-domine', desired, true),
				new Rite('matutinum', desired, true),
				new Rite('laudes', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'matutinum', desired),
			new Occasion('Prima', [
				new Rite('aperi-domine', desired, true),
				new Rite('prima', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'prima', desired),
			new Occasion('Tertia', [
				new Rite('aperi-domine', desired, true),
				new Rite('tertia', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'tertia', desired),
			new Occasion('Sexta', [
				new Rite('aperi-domine', desired, true),
				new Rite('sexta', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'sexta', desired),
			new Occasion('Nona', [
				new Rite('aperi-domine', desired, true),
				new Rite('nona', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'nona', desired),
			new Occasion('Vesperæ', [
				new Rite('aperi-domine', desired, true),
				new Rite('vesperae', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'vesperae', desired),
			new Occasion('Completorium', [
				new Rite('aperi-domine', desired, true),
				new Rite('completorium', desired, true),
				new Rite('sacrosanctae', desired, true)
			], 'completorium', desired)
		);
	}
	
	suggestSelectedOccasion = fullAmbit.suggestSelectedOccasion;
}

defunctAmbit = new Ambit(
	new Occasion('Matutinum & Laudes', [
		new Rite('aperi-domine', 'officium-defunctorum', true),
		new Rite('matutinum', 'officium-defunctorum', true),
		new Rite('laudes', 'officium-defunctorum', true),
		new Rite('sacrosanctae', 'officium-defunctorum', true)
	], 'matutinum', 'officium-defunctorum'),
	new Occasion('Vesperæ', [
		new Rite('aperi-domine', 'officium-defunctorum', true),
		new Rite('vesperae', 'officium-defunctorum', true),
		new Rite('sacrosanctae', 'officium-defunctorum', true)
	], 'vesperae', 'officium-defunctorum')
);

defunctAmbit.suggestSelectedOccasion = function(hour) {
	if (hour < 16) {
		return this.occasions[0];
	} else {
		return this.occasions[1];
	}
}

benedictioMensaeAmbit = new Ambit(
	new Occasion('Pro Prandio', [
		new Rite('pro-prandio', 'diei', true),
	], 'matutinum', 'diei'),
	new Occasion('Pro Cœna', [
		new Rite('pro-coena', 'diei', true),
	], 'vesperae', 'diei')
);

benedictioMensaeAmbit.suggestSelectedOccasion = defunctAmbit.suggestSelectedOccasion;

function singleOccasionAmbit(name, desired) {
	return new Ambit(new Occasion(name, [new Rite(desired, 'diei', true)], 'matutinum', 'diei'));
}

function defineAmbit(desired, choral = true) {
	switch(desired) {
		case 'omnes':
			ambit = fullAmbit;
			break;
		case 'officium-parvum-bmv':
			ambit = new SingleAmbit('officium-parvum-bmv');
			break;
		case 'officium-defunctorum':
			ambit = defunctAmbit;
			break;
		case 'psalmi-graduales':
			ambit = singleOccasionAmbit('Psalmi Graduales', desired);
			break;
		case 'psalmi-poenitentiales':
			ambit = singleOccasionAmbit('Psalmi Pœnitentiales', desired);
			break;
		case 'ordo-commendationis-animae':
			ambit = singleOccasionAmbit('Ordo Commendationis Animæ', desired);
			break;
		case 'formula-indulgentiam-articulo-mortis':
			ambit = singleOccasionAmbit('Formula ad Impertiendam Indulgentiam', desired);
			break;
		case 'benedictio-mensae':
			ambit = benedictioMensaeAmbit;
			break;
		case 'itinerarium':
			ambit = singleOccasionAmbit('Itinerarium Clericorum', desired);
			break;
		case 'semper-cum-opbmv':
			ambit = new Ambit(fullAmbit.occasions.map(
				(occasion) => new Occasion(occasion.name, occasion.rites.map(
					(rite) => rite.where == 'officium-parvum-bmv' ? new Rite(rite.what, rite.where, true) : (rite)
				), occasion.id, occasion.title)
			));
			ambit.suggestSelectedOccasion = fullAmbit.suggestSelectedOccasion;
			break;
		case 'diei':
			ambit = new Ambit(fullAmbit.occasions.map(
				(occasion) => new Occasion(occasion.name, occasion.rites.filter(
					(rite) => rite.where == 'diei' || rite.where == 'antiphona-bmv-temporis'
				), occasion.id, occasion.title)
			));
			ambit.suggestSelectedOccasion = fullAmbit.suggestSelectedOccasion;
	}
	if (choral) {
		return ambit;
	} else {
		ret = new Ambit(ambit.occasions.map(
			(occasion) => new Occasion(occasion.name, (occasion.id == 'matutinum' ? occasion.rites : occasion.rites.filter((rite) => rite.what != 'antiphona-bmv')), occasion.id, occasion.title)
		));
		ret.suggestSelectedOccasion = ambit.suggestSelectedOccasion;
		return ret;
	}
}

let lastParams = null;
let lastResult = null;
function resolveParameters(parameters) {
	if (lastParams == JSON.stringify(parameters)) {
		return lastResult;
	} else {
		lastParams = JSON.stringify(parameters);
		let resolved = {...parameters, 'chant': parameters.recitation == 'plainchant', 'choral': parameters.recitation != 'private'};
		resolved['ambit'] = defineAmbit(parameters.desired, parameters.choral);
		resolved.votives = Object.entries(resolved.votives).filter(i => i[1]).map(i => i[0]).join('+');
		lastResult = resolved;
    resolved['side-by-side'] = resolved['side-by-side'] && resolved.translation;
		return resolved;
	}
}

function getTime(occasion) {
	return (occasion == 'vesperae' || occasion == 'completorium') ? 'vesperale' : 'diurnale';
}

let dayParametersExpectation = null;
let cachedDays = new Object();
async function getLiturgicalDay(calendarDate, time, parameters) {
	if (dayParametersExpectation != JSON.stringify(parameters)) {
		cachedDays = new Object();
		dayParametersExpectation = JSON.stringify(parameters);
	}

	let resolvedParameters = resolveParameters(parameters);

	async function fetchLiturgicalDay() {
		return fetch(`/day?date=${calendarDate}&time=${time}&votives=${resolvedParameters.votives}`).then(response => response.json());
	}

	let key = calendarDate + time;
	if (!(key in cachedDays)) {
		cachedDays[key] = fetchLiturgicalDay();
	}
	return cachedDays[key];
}

let riteParametersExpectation = null;
let cachedRites = new Object();

async function getRite(calendarDate, occasion, parameters, version) {
	if (riteParametersExpectation != JSON.stringify(parameters)) {
		cachedRites = new Object();
		riteParametersExpectation = JSON.stringify(parameters);
	}

	async function fetchRite() {
		let resolvedParameters = resolveParameters(parameters);
		var response = await fetch(`/title?date=${calendarDate}
			&hour=${occasion}
			&select=${resolvedParameters.ambit.occasions[resolvedParameters.ambit.idindex(occasion)].title}
			&votives=${resolvedParameters.votives}
		`);
		let titleJSON = await response.json();
		let ret = riteTitle(titleJSON[0], titleJSON[1], 'large');
		let previousTitle = titleJSON[0];
		let liturgicalDay = await getLiturgicalDay(calendarDate, getTime(occasion), parameters);
		let rites = resolvedParameters.ambit.riteList(liturgicalDay.tags, occasion);
		for (var i = 0; i < rites.length; i++) {
			let response = await fetch(`/rite?date=${calendarDate}
				&hour=${rites[i][0]}&noending=${i != rites.length - 1 && (rites[i + 1][1] == 'officium-parvum-bmv' || rites[i + 1][1] == 'officium-defunctorum' || rites[i + 1][0] == 'psalmi-poenitentiales' || rites[i + 1][0] == 'litaniae-sanctorum' || rites[i + 1][0] == 'officium-capituli')}
				&translation=${resolvedParameters.translation ? translation(parameters.locale) : 'none'}
				&privata=${!resolvedParameters.choral ? 'privata': 'chorali'}
				&chant=${resolvedParameters.recitation == 'plainchant' ? 'true': 'false'}
				&select=${rites[i][1]}
				&votives=${resolvedParameters.votives}
				&version=${version}
			`);
			if (response.status == 400 || response.status == 500) {
				ret = await response.text();
				break;
			}
			let json = await response.json();
			if (!json.rite.tags.includes('aperi-domine') && !json.rite.tags.includes('sacrosanctae') && !json.rite.tags.includes('antiphona-bmv') && !json.rite.tags.includes('officium-capituli') && json['used-primary'][0] != previousTitle) {
				ret += riteTitle(json['used-primary'][0], json['used-primary'][1], 'small');
				previousTitle = json['used-primary'][0];
			}
			ret += renderRite(json, resolvedParameters);
		}
		return ret;
	}

	let key = calendarDate + occasion;
	if (!(key in cachedRites)) {
		cachedRites[key] = fetchRite();
	}
	return cachedRites[key];
}
