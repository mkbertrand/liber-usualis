// Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

class Occasion {
	constructor(name, rite) {
		this.name = name;
		this.rite = rite;
	}
}

class Ambit {
	constructor(occasions, select, type = 'ritus') {
    this.occasions = occasions;
    this.select = select;
    this.type = type;
	}

	idindex(id) {
		for (var i = 0; i < this.occasions.length; i++) {
			if (this.occasions[i].id == id) {
				return i;
			}
		}
		return -1;
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
			return newAmbit.occasions[0].rite;
		} else {
			return newAmbit.occasions[ind].rite;
		}
	}
}

const sevenHourTemplater = (type, select, mods) => {
  let ambit = new Ambit([
    new Occasion('Matutinum & Laudes', 'matutinum' + mods),
    new Occasion('Prima', 'prima' + mods),
    new Occasion('Tertia', 'tertia' + mods),
    new Occasion('Sexta', 'sexta' + mods),
    new Occasion('Nona', 'nona' + mods),
    new Occasion('Vesperae', 'vesperae' + mods),
    new Occasion('Completorium', 'completorium' + mods)
  ], select, type);
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

defunctAmbit = new Ambit([
	new Occasion('Matutinum & Laudes', 'matutinum'),
	new Occasion('Vesperae', 'vesperae')
], 'officium-defunctorum', 'ritus');

benedictioMensaeAmbit = new Ambit([
	new Occasion('Pro Prandio', 'pro-prandio'),
	new Occasion('Pro Cœna', 'pro-coena')
], 'primarium', 'ritus');

defunctAmbit.suggestSelectedOccasion = function(hour) {
	if (hour < 16) {
		return this.occasions[0];
	} else {
		return this.occasions[1];
	}
}

function singleOccasionAmbit(name, desired) {
  return new Ambit([new Occasion(name, desired)], 'primarium');
}

export function defineAmbit(desired) {
	switch(desired) {
		case 'omnes':
			return sevenHourTemplater('officium', 'primarium', '');
		case 'officium-parvum-bmv':
			return sevenHourTemplater('ritus', 'officium-parvum-bmv', '');
		case 'officium-defunctorum':
			return defunctAmbit;
		case 'psalmi-graduales':
			return singleOccasionAmbit('Psalmi Graduales', desired);
		case 'psalmi-poenitentiales':
			return singleOccasionAmbit('Psalmi Pœnitentiales', desired);
		case 'ordo-commendationis-animae':
			return singleOccasionAmbit('Ordo Commendationis Animæ', desired);
		case 'formula-indulgentiam-articulo-mortis':
			return singleOccasionAmbit('Formula ad Impertiendam Indulgentiam', desired);
		case 'benedictio-mensae':
			return benedictioMensaeAmbit;
		case 'itinerarium':
			return singleOccasionAmbit('Itinerarium Clericorum', desired);
		case 'semper-cum-opbmv':
      return sevenHourTemplater('officium', 'primarium', '+cum-opbmv');
		case 'diei':
      return sevenHourTemplater('officium', 'primarium', '+sine-ritibus');
	}
}
