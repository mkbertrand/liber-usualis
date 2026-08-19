// Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

function translation(locale) {
	if (locale == 'en') {
		return ['english'];
	} else if (locale == 'de') {
		return ['deutsch'];
	} else {
		return ['english'];
	}
}

let lastParams = null;
let lastResult = null;
function resolveParameters(parameters) {
	if (lastParams == JSON.stringify(parameters)) {
		return lastResult;
	} else {
		lastParams = JSON.stringify(parameters);
		let resolved = {...parameters};
		resolved['ambit'] = Pray.defineAmbit(parameters.desired, parameters.priest);
		resolved.votives = Object.entries(resolved.votives).filter(i => i[1]).map(i => i[0]).join('+');
		lastResult = resolved;
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
		return fetch(`/api/ordo?date=${calendarDate}&time=${time}&votives=${resolvedParameters.votives}`).then(response => response.json());
	}

	let key = calendarDate + time;
	if (!(key in cachedDays)) {
		cachedDays[key] = fetchLiturgicalDay();
	}
	return cachedDays[key];
}

let riteParametersExpectation = null;
let cachedRites = new Object();

async function getRite(calendarDate, occasion, parameters, resources) {
	if (riteParametersExpectation != JSON.stringify(parameters)) {
		cachedRites = new Object();
		riteParametersExpectation = JSON.stringify(parameters);
	}

	async function fetchRite() {
		let resolvedParameters = resolveParameters(parameters);
    var response = await fetch(`/api/composer?date=${calendarDate}&rite=${occasion}+${resolvedParameters.ambit.type}&opt=${resolvedParameters.ambit.opt}${resolvedParameters.priest ? '' : '+privata'}&select=${resolvedParameters.ambit.select}&translation=${resolvedParameters.translation ? translation(parameters.locale) : 'none'}&votives=${resolvedParameters.votives}`);

    if (response.status == 400 || response.status == 500) {
      return await response.text();
    }

    let json = await response.json();
    return Pray.dateHeader(calendarDate) + Pray.riteTitle(json['used-primary'][0], json['used-primary'][1], 'large') + Pray.renderRite(json, resources);
	}

	let key = calendarDate + occasion;
	if (!(key in cachedRites)) {
		cachedRites[key] = fetchRite();
	}
	return cachedRites[key];
}
