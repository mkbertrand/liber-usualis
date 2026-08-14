function translation(locale) {
	if (locale == 'en') {
		return ['english'];
	} else if (locale == 'de') {
		return ['deutsch'];
	} else {
		return ['english'];
	}
}

// Featured art panels will be 3:10
const panelratio = 3/10;

var panelsopen = false;
var panelquotient = 0;
var riteheight = 1;
function doPanelSize() {
	var height = window.innerHeight - parseInt(window.getComputedStyle(document.body).getPropertyValue('--top-bar-title-height').slice(0, -2)) - 1;
	var minritewidth = height / 1.6;
	var panelwidth = height * panelratio;

	// Second condition checks if the screen is MUCH shorter than it is wide, in which case it presumes a mobile browser.
	canmakepanels = panelwidth * 2 + minritewidth < document.documentElement.clientWidth && height * 3 > document.documentElement.clientWidth;

	if (!canmakepanels) {
    document.getElementById('rite-page-container').style.width = '100%';
    document.getElementById('side-panel-left').style.width = '0';
    document.getElementById('side-panel-right').style.width = '0';
    document.getElementById('content-container-outer').style.width = '100%';
		panelsopen = false;
		panelquotient = 0;

	} else {

		// In other words, the rite panel will never be wider than 1:1
		ritewidth = Math.min(height, document.documentElement.clientWidth - 2 * panelwidth, 1600);

    document.getElementById('rite-page-container').style.width = `${ritewidth}px`;
    document.getElementById('side-panel-left').style.width = `${panelwidth}px`;
    document.getElementById('side-panel-right').style.width = `${panelwidth}px`;
    document.getElementById('content-container-outer').style.width = `${ritewidth + panelwidth * 2}px`;

		panelsopen = true;

		if (panelwidth / riteheight != panelquotient) {
			generatepanels();
		}

		panelquotient = panelwidth / riteheight;
	}
}

function generatepanels() {
	riteheight = document.getElementById('rite-container').clientHeight;
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

async function getRite(calendarDate, occasion, parameters, resources) {
	if (riteParametersExpectation != JSON.stringify(parameters)) {
		cachedRites = new Object();
		riteParametersExpectation = JSON.stringify(parameters);
	}

	async function fetchRite() {
		let resolvedParameters = resolveParameters(parameters);
		var response = await fetch(`/title?date=${calendarDate}
			&hour=${occasion}
			&votives=${resolvedParameters.votives}
		`);
		let titleJSON = await response.json();
		let ret = Pray.dateHeader(calendarDate) + Pray.riteTitle(titleJSON[0], titleJSON[1], 'large');
		let previousTitle = titleJSON[0];
		let liturgicalDay = await getLiturgicalDay(calendarDate, getTime(occasion), parameters);
    var response = await fetch(`/rite?date=${calendarDate}&rite=${occasion}+${resolvedParameters.ambit.type}&select=${resolvedParameters.ambit.select}&translation=${resolvedParameters.translation ? translation(parameters.locale) : 'none'}&privata=${!resolvedParameters.priest ? 'privata': 'chorali'}&chant=${resolvedParameters.priest == 'plainchant' ? 'true': 'false'}&votives=${resolvedParameters.votives}
    `);

    if (response.status == 400 || response.status == 500) {
      return await response.text();
    }

    let json = await response.json();
		for (var i = 0; i < 0; i++) {
			if (!json[i].rite.tags.includes('aperi-domine') && !json[i].rite.tags.includes('sacrosanctae') && !json[i].rite.tags.includes('antiphona-bmv') && !json[i].rite.tags.includes('officium-capituli') && json[i]['used-primary'][0] != previousTitle) {
				ret += Pray.riteTitle(json[i]['used-primary'][0], json[i]['used-primary'][1], 'small');
				previousTitle = json[i]['used-primary'][0];
			}
		}
    ret += Pray.renderRite(json, resources);
		return ret;
	}

	let key = calendarDate + occasion;
	if (!(key in cachedRites)) {
		cachedRites[key] = fetchRite();
	}
	return cachedRites[key];
}
