// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

class Occasion {
	constructor(name, rite) {
		this.name = name;
		this.rite = rite;
	}
}

class Ambit {
	constructor(occasions, select, type, opt = '') {
    this.occasions = occasions;
    this.select = select;
    this.type = type;
    this.opt = opt;
	}

	riteIndex(rite) {
		for (var i = 0; i < this.occasions.length; i++) {
			if (this.occasions[i].rite == rite) {
				return i;
			}
		}
		return -1;
	}

	nextOccasion(current) {
		return this.occasions[(this.riteIndex(current) + 1) % this.occasions.length];
	}

	// Based on the hour of the day, suggest which occasion should be presented if no external information is available - e.g. if a user loads the page for the first time ever at 9AM, suggest he pray Terce. This is intended to be overwritten manually by individual objects in the Ambit class.
	suggestSelectedOccasion(hour) {
		return this.occasions[0];
	}

	// When switching between ambits with a currently selected occasion in the old ambit, suggest which occasion should be selected within the new ambit.
	slideAmbitOccasion(newAmbit, currentOccasionID) {
		let ind = newAmbit.riteIndex(currentOccasionID);
		if (ind == -1) {
			return newAmbit.occasions[0].rite;
		} else {
			return newAmbit.occasions[ind].rite;
		}
	}
}

const sevenHourTemplater = (type, select, opt) => {
  let ambit = new Ambit([
    new Occasion('Matutinum & Laudes', 'matutinum-laudes'),
    new Occasion('Prima', 'prima'),
    new Occasion('Tertia', 'tertia'),
    new Occasion('Sexta', 'sexta'),
    new Occasion('Nona', 'nona'),
    new Occasion('Vesperae', 'vesperae'),
    new Occasion('Completorium', 'completorium')
  ], select, type, opt);
  ambit.suggestSelectedOccasion = function(hour) {
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
  return ambit;
}

const defunctAmbit = new Ambit([
	new Occasion('Matutinum & Laudes', 'matutinum-laudes'),
	new Occasion('Vesperae', 'vesperae')
], 'officium-defunctorum', 'officium', '');

const benedictioMensaeAmbit = new Ambit([
	new Occasion('Pro Prandio', 'pro-prandio'),
	new Occasion('Pro Cœna', 'pro-coena')
], 'primarium', 'ritus', '');

defunctAmbit.suggestSelectedOccasion = function(hour) {
	if (hour < 16) {
		return this.occasions[0];
	} else {
		return this.occasions[1];
	}
}

function singleOccasionAmbit(name, desired) {
  return new Ambit([new Occasion(name, desired)], 'primarium', 'ritus', '');
}

export function defineAmbit(desired) {
	switch(desired) {
		case 'omnes':
			return sevenHourTemplater('officium', 'primarium', '');
		case 'officium-parvum-bmv':
			return sevenHourTemplater('officium', 'officium-parvum-bmv', '');
		case 'semper-cum-opbmv':
      return sevenHourTemplater('officium', 'primarium', 'cum-opbmv');
		case 'diei':
      return sevenHourTemplater('officium', 'primarium', 'sine-ritibus');
		case 'officium-defunctorum':
			return defunctAmbit;
		case 'benedictio-mensae':
			return benedictioMensaeAmbit;
		case 'psalmi-graduales':
			return singleOccasionAmbit('Psalmi Graduales', desired);
		case 'psalmi-poenitentiales':
			return singleOccasionAmbit('Psalmi Pœnitentiales', desired);
		case 'ordo-commendationis-animae':
			return singleOccasionAmbit('Ordo Commendationis Animæ', desired);
		case 'formula-indulgentiam-articulo-mortis':
			return singleOccasionAmbit('Formula ad Impertiendam Indulgentiam', desired);
		case 'itinerarium':
			return singleOccasionAmbit('Itinerarium Clericorum', desired);
	}
}
