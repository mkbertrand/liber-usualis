// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

class Rite {
	constructor(what, where, always) {
		this.what = what;
		this.where = where;
		this.always = always;
	}
}

class Occasion {
	constructor(name, rites, id) {
		this.name = name;
		this.rites = rites;
		this.id = id;
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
	], 'matutinum'),
	new Occasion('Prima', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('prima', 'diei', true),
		new Rite('prima', 'officium-parvum-bmv', false),
		new Rite('officium-capituli', 'diei', true),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'prima'),
	new Occasion('Tertia', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('tertia', 'diei', true),
		new Rite('tertia', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'tertia'),
	new Occasion('Sexta', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('sexta', 'diei', true),
		new Rite('sexta', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'sexta'),
	new Occasion('Nona', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('nona', 'diei', true),
		new Rite('nona', 'officium-parvum-bmv', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'nona'),
	new Occasion('Vesperæ', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('vesperae', 'officium-parvum-bmv', false),
		new Rite('vesperae', 'diei', true),
		new Rite('vesperae', 'officium-defunctorum', false),
		new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
		new Rite('sacrosanctae', 'diei', true)
	], 'vesperae'),
	new Occasion('Completorium', [
		new Rite('aperi-domine', 'diei', true),
		new Rite('completorium', 'diei', true),
		new Rite('completorium', 'officium-parvum-bmv', false),
		new Rite('sacrosanctae', 'diei', true)
	], 'completorium')
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
			], 'matutinum'),
			new Occasion('Prima', [
				new Rite('aperi-domine', desired, true),
				new Rite('prima', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'prima'),
			new Occasion('Tertia', [
				new Rite('aperi-domine', desired, true),
				new Rite('tertia', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'tertia'),
			new Occasion('Sexta', [
				new Rite('aperi-domine', desired, true),
				new Rite('sexta', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'sexta'),
			new Occasion('Nona', [
				new Rite('aperi-domine', desired, true),
				new Rite('nona', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'nona'),
			new Occasion('Vesperæ', [
				new Rite('aperi-domine', desired, true),
				new Rite('vesperae', desired, true),
				new Rite('antiphona-bmv', 'antiphona-bmv-temporis', true),
				new Rite('sacrosanctae', desired, true)
			], 'vesperae'),
			new Occasion('Completorium', [
				new Rite('aperi-domine', desired, true),
				new Rite('completorium', desired, true),
				new Rite('sacrosanctae', desired, true)
			], 'completorium')
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
	], 'matutinum'),
	new Occasion('Vesperæ', [
		new Rite('aperi-domine', 'officium-defunctorum', true),
		new Rite('vesperae', 'officium-defunctorum', true),
		new Rite('sacrosanctae', 'officium-defunctorum', true)
	], 'vesperae')
);

defunctAmbit.suggestSelectedOccasion = function(hour) {
	if (hour < 16) {
		return this.occasions[0];
	} else {
		return this.occasions[1];
	}
}

function singleOccasionAmbit(name, desired) {
	return new Ambit(new Occasion(name, [new Rite(desired, 'diei', true)], 'matutinum'));
}

function defineambit(desired, choral = true) {
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
			ambit = singleOccasionAmbit('Benedictio Mensæ', desired);
			break;
		case 'itinerarium':
			ambit = singleOccasionAmbit('Itinerarium Clericorum', desired);
			break;
		case 'semper-cum-opbmv':
			ambit = new Ambit(fullAmbit.occasions.map(
				(occasion) => new Occasion(occasion.name, occasion.rites.map(
					(rite) => rite.where == 'officium-parvum-bmv' ? new Rite(rite.what, rite.where, true) : (rite)
				), occasion.id)
			));
			ambit.suggestSelectedOccasion = fullAmbit.suggestSelectedOccasion;
			break;
		case 'diei':
			ambit = new Ambit(fullAmbit.occasions.map(
				(occasion) => new Occasion(occasion.name, occasion.rites.filter(
					(rite) => rite.where == 'diei' || rite.where == 'antiphona-bmv-temporis'
				), occasion.id)
			));
			ambit.suggestSelectedOccasion = fullAmbit.suggestSelectedOccasion;
	}
	if (choral) {
		return ambit;
	} else {
		ret = new Ambit(ambit.occasions.map(
			(occasion) => new Occasion(occasion.name, (occasion.id == 'matutinum' ? occasion.rites : occasion.rites.filter((rite) => rite.what != 'antiphona-bmv')), occasion.id)
		));
		ret.suggestSelectedOccasion = ambit.suggestSelectedOccasion;
		return ret;
	}
}
