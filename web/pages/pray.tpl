<!DOCTYPE html>

<!-- Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json

<html lang="{{locale.split('-')[0]}}">
	<head>
		<title>Pray</title>
		<script type="application/ld+json">
		{
			"@context":"https://schema.org",
			"@type":"WebSite",
			"name":"Liber Usualis",
			"url":"https://liberusualis.org/"
		}
		</script>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei.png">
		<link rel="stylesheet" type="text/css" href="/resources/styles/pray.css?v=39">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css?v=15">
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
		<style>
			@import url('https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap');
		</style>
		<script type="text/javascript" src="/resources/js/pray.js?v=1"></script>
		<script type="text/javascript" src="/resources/js/ritegen.js?v=33"></script>
		<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
		<script type="text/javascript" src="/resources/js/exsurge.js"></script>
		<script type="text/javascript" src="/resources/js/gabc-chant.js"></script>
	</head>
	<body x-data="{
	liturgylist: [],
	optionspanel: false,
	date: null,
	time: 'diurnale',
	liturgicalday: '',
	hour: '',
	choral: $persist(true),
	chant: $persist(false),
	recitation: $persist('recto-tono'),
	translation: $persist(false),
	bottompanel: $persist(false),
	bottompanelopen: true,
	search: '',
	desired: $persist('omnes'), ambit: $persist([]),
	rite: '',
	initialized: false,
	dayinitialized: false,
	ignoredatechange: false,
	canincrementhour: true,
	nexthour: $persist(null),
	get Rite() {
		if (panelsopen) {
			$nextTick(() => generatepanels());
		}
		return this.rite;
	},
	// Sets this.date with a local date which is adjusted to UTC.
	setDate(date) {
		this.date = new Date(new Date(date + new Date().toISOString().substring(10)).getTime() + this.date.getTimezoneOffset() * 60000);
	},
	// Returns the date (yyyy-mm-dd) adjusted for timezone.
	getLocalDate() {
		return new Date(this.date.getTime() - this.date.getTimezoneOffset() * 60000).toISOString().substring(0, 10);
	},
	setRecitation(recitation) {
		if (recitation == 'plainchant') {
			this.choral = true;
			this.chant = true;
		} else if (recitation == 'recto-tono') {
			this.choral = true;
			this.chant = false;
		} else if (recitation == 'private') {
			this.choral = false;
			this.chant = false;
		}
		this.ambit = defineambit(this.desired, this.choral);
		this.liturgylist = ritelist(this.liturgicalday.tags, this.ambit);
		this.slideHour(this.hour.id);
		this.recitation = recitation;
	},
	updateRiteAsyncLock: false,
	async updateRite(scroll = true) {
		lasttitle = '';
		if (!this.updateRiteAsyncLock) {
			this.updateRiteAsyncLock = true;
			newrite = '';
			for (var i = 0; i < this.hour.content.length; i++) {
				select = this.hour.content[i][1] == 'diei' ? '' : this.hour.content[i][1];
				noending = false;
				if (i != this.hour.content.length - 1 && (this.hour.content[i + 1][1] == 'officium-parvum-bmv' || this.hour.content[i + 1][1] == 'officium-defunctorum' || this.hour.content[i + 1][0] == 'psalmi-poenitentiales' || this.hour.content[i + 1][0] == 'litaniae-sanctorum' || this.hour.content[i + 1][0] == 'officium-capituli')) {
					noending = true;
				}
				var response = await fetch(`/rite?date=${this.getLocalDate()}&time=${this.time}&hour=${this.hour.content[i][0]}&noending=${noending}&translation=${this.translation ? translation('{{locale}}') : 'none'}&privata=${this.recitation=='private' ? 'privata': 'chorali'}` + (select == '' ? '' : `&select=${select}`));
				if (response.status == 500) {
					newrite = await response.text();
					break;
				}
				var json = await response.json();
				// If this is the first item in the updated rite, wipe the slate clean. Otherwise just append.
				if (i == 0) {
					title = riteTitle(json, 'large')
					if (scroll) {
						window.scrollTo({top:0, behavior: 'smooth'});
					}
				} else {
					title = '';
					if (json.usednames[0] != lasttitle) {
						title = riteTitle(json, 'small');
					}
				}
				newrite += title + render(json, this.chant);
				lasttitle = json.usednames[0];
			}
			this.rite = newrite;
			this.initialized = true;
			this.updateRiteAsyncLock = false;
		} else {
			console.log('Simultaneous attempts to update Rite');
		}
	},
	slideHour(id) {
		for (var i = 0; i < this.liturgylist.length; i++) {
			if (this.liturgylist[i].id == id) {
				this.hour = this.liturgylist[i];
				return;
			}
		}
	},
	async updateDay() {
		var response = await fetch(`/day?date=${this.getLocalDate()}&time=${this.time}`);
		var json = await response.json();
		var primary = json.primary[1];
		this.liturgylist = ritelist(json.tags, this.ambit);
		this.liturgicalday = json;
		if (this.dayinitialized) {
			this.slideHour(this.hour.id);
			this.updateRite();
		}
		this.dayinitialized = true;
		this.ignoredatechange = false;
	},
	setTime(time) {
		this.time = time;
		this.updateDay();
	},
	setHour(id) {
		this.slideHour(id);
		oldtime = this.time;
		newtime = (this.hour.id == 'vesperae' || this.hour.id == 'completorium') ? 'vesperale' : 'diurnale';
		if (newtime != oldtime) {
			this.setTime(newtime);
		} else {
			this.updateRite();
		}
	},
	async incrementHour() {
		for (var i = 0; i < this.liturgylist.length; i++) {
			if (this.liturgylist[i].id == this.hour.id) {
				if (i != this.liturgylist.length - 1) {
					this.setHour(this.liturgylist[i + 1].id);
				} else {
					// Otherwise things will happen async that need to be synchronous
					this.ignoredatechange = true;
					this.date = new Date(this.date.getTime() + 86400000);
					this.search = this.getLocalDate();
					// This has the effect of actually hitting setTime() and updateDay()
					await this.setHour(this.liturgylist[0].id);
				}
				return;
			}
		}
	},
	canIncrementTo() {
		if (this.nexthour == null) {
			return false;
		}
		zeroedsetdate = new Date(this.nexthour[0].getFullYear(), this.nexthour[0].getMonth(), this.nexthour[0].getDate());
		currentdate = new Date();
		zeroedcurrentdate = new Date(currentdate.getFullYear(), currentdate.getMonth(), currentdate.getDate());
		if (this.nexthour[1] == 'matutinum' && zeroedsetdate - 86400000 == zeroedcurrentdate - 0) {
			return new Date().getHours() >= 14;
		} else {
			return zeroedsetdate - 0 == zeroedcurrentdate - 0;
		}
	},
	determineNextHour() {
		zeroedsetdate = new Date(this.date.getFullYear(), this.date.getMonth(), this.date.getDate());
		currentdate = new Date();
		zeroedcurrentdate = new Date(currentdate.getFullYear(), currentdate.getMonth(), currentdate.getDate());
		if (zeroedsetdate - 86400000 == zeroedcurrentdate - 0 && this.hour.id == 'matutinum' && this.liturgylist.length != 1) {
			this.nexthour = [this.date, this.liturgylist[1].id];
		} else if (zeroedsetdate - 0 != zeroedcurrentdate - 0) {
			// If user completes an hour from the day before, they've clearly made a mistake and will have to manually select their hour next time they reload the page.
			this.nexthour = null;
		} else {
			for (var i = 0; i < this.liturgylist.length; i++) {
				if (this.liturgylist[i].id == this.hour.id) {
					if (i != this.liturgylist.length - 1) {
						this.nexthour = [this.date, this.liturgylist[i + 1].id];
					} else {
						this.nexthour = [new Date(this.date.getTime() + 86400000), this.liturgylist[0].id];
					}
					break;
				}
			}
		}
	},
	setAmbit(ambit) {
		oldambit = this.ambit;
		this.ambit = ambit;
		this.liturgylist = ritelist(this.liturgicalday.tags, this.ambit);

		if (this.ambit.length < oldambit.length && this.ambit.length == 1) {
			this.setHour('matutinum');
		} else if (this.ambit.length < oldambit.length && this.ambit.length == 2) {
			if (this.hour.id == 'completorium') {
				this.setHour('vesperae');
			} else if (['prima', 'tertia', 'sexta', 'nona'].includes(this.hour.id)) {
				this.setHour('matutinum');
			} else {
				this.slideHour(this.hour.id);
				this.updateRite();
			}
		} else {
			this.slideHour(this.hour.id);
			this.updateRite();
		}

		if (this.nexthour) {
			if (this.ambit.length < oldambit.length && this.ambit.length == 1) {
				this.nexthour[1] = 'matutinum';
			} else if (this.ambit.length < oldambit.length && this.ambit.length == 2) {
				if (this.hour.id == 'completorium') {
					this.nexthour[1] = 'vesperae';
				} else if (['prima', 'tertia', 'sexta', 'nona'].includes(this.hour.id)) {
					this.nexthour[1] = 'matutinum';
				}
			}
		}
	}
}" x-init="
	dopanelsize();
	if ('{{locale}}' == 'la') {
		translation = false;
	}
	if (ambit == '') {
		ambit = defineambit(desired, choral);
	}
	if (nexthour && typeof nexthour[0] === 'string') {
		nexthour[0] = new Date(nexthour[0]);
	}
	if (canIncrementTo()) {
		date = nexthour[0];
		time = nexthour[1] == 'vesperae' || nexthour[1] == 'completorium' ? 'vesperale' : 'diurnale';
	} else {
		date = new Date();
		if (date.getHours() >= 16) {
			time = 'vesperale';
		}
	}
	$watch('date', date => {if (!ignoredatechange) {updateDay()}});
	$watch('desired', desired => setAmbit(defineambit(desired, choral)));
	$watch('recitation', recitation => updateRite(false));
	$watch('translation', translation => updateRite());
	$watch('dayinitialized', dayinitialized => {
		if (canIncrementTo()) {
			for (var i = 0; i < liturgylist.length; i++) {
				if (liturgylist[i].id == nexthour[1]) {
					hour = liturgylist[i];
					break;
				}
			}
		}
		else if (liturgylist.length == 7) {
			if (date.getHours() < 6) {
				hour = liturgylist[0];
			} else if (date.getHours() < 9) {
				hour = liturgylist[1];
			} else if (date.getHours() < 11) {
				hour = liturgylist[2];
			} else if (date.getHours() < 14) {
				hour = liturgylist[3];
			} else if (date.getHours() < 16) {
				hour = liturgylist[4];
			} else if (date.getHours() < 20) {
				hour = liturgylist[5];
			} else {
				hour = liturgylist[6];
			}
		} else if (liturgylist.length == 2) {
			if (date.getHours() < 16) {
				hour = liturgylist[0];
			} else {
				hour = liturgylist[1];
			}
		} else if (liturgylist.length == 1) {
			hour = liturgylist[0];
		}
		updateRite();
	});
	updateDay();
	">
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen"><img id="sidebar-nav-toggle" src="/resources/svg/hamburger-menu.svg" /></button>
				<div id="project-logo">
					<a href="/{{preferredlocale}}/index"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS"></a>
				</div>
				<button id="options-gear-wrapper" @click="optionspanel = !optionspanel">
					<img id="options-gear" src="/resources/svg/settings-outline.svg" />
				</button>
			</div>
			% include('web/resources/sidemenu.tpl', preferredlocale=preferredlocale, text=json.load(open(f'web/locales/{preferredlocale}/resources/sidemenu.json')))

<div id="content-container-outer">
	<div x-cloak id="options-panel-background" x-show="optionspanel">
		<div id="options-panel" x-trap.noscroll="optionspanel" @click.outside="optionspanel = false">
			<h3 id="options-panel-title">{{text['options-panel-title']}}</h3>
			% if locale != 'la':
			<button class="options-panel-button" @click="translation = !translation" :class="translation? 'options-panel-button-on' : 'options-panel-button-off'">{{text['translation-toggle']}}</button>
			% end
			<div class="recitation-select-container">
				<button class="options-panel-button recitation-select-button" @click="setRecitation('plainchant');" :class="recitation == 'plainchant'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-plainchant']}}</button>
				<button class="options-panel-button recitation-select-button" @click="setRecitation('recto-tono');" :class="recitation == 'recto-tono'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-recto-tono']}}</button>
				<button class="options-panel-button recitation-select-button" @click="setRecitation('private');" :class="recitation == 'private'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-private']}}</button>
			</div>
			<template x-if="initialized">
				<div id="options-panel-require-initialized-container">
					<div id="coincidences-list-container">
						<h3 class="options-panel-section-head">{{text['coincidences-list-title']}}</h3>
						<h4 class="coincidences-label">{{text['coincidences-list-primary']}}</h4>
						<div id="primary-entry" class="coincidence-entry" x-text="abbreviateName(liturgicalday.primary[0])"></div>
						<h4 class="coincidences-label">{{text['coincidences-list-commemorations']}}</h4>
						<template x-for="commemoration in liturgicalday.commemorations.filter((commemoration) => !commemoration[1].includes('suffragium'))">
							<div class="coincidence-entry" x-text="abbreviateName(commemoration[0])"></div>
						</template>
						<h4 class="coincidences-label">{{text['coincidences-list-omissions']}}</h4>
						<template x-for="omission in liturgicalday.omissions">
							<div class="coincidence-entry" x-text="abbreviateName(omission[0])"></div>
						</template>
						<h4 class="coincidences-label">{{text['coincidences-list-votives']}}</h3>
					</div>
					<div id="ambit-select-wrapper">
						<div id="ambit-select-container" x-data="{ambitEntries: [['omnes', 'Officium'], ['diei', 'Officium diei'], ['officium-parvum-bmv', 'Officium Parvum B.M.V.'], ['officium-defunctorum', 'Officium Defunctorum'], ['psalmi-graduales', 'Psalmi Graduales'], ['psalmi-poenitentiales', 'Psalmi Pœnitentiales']]}">
							<h3 class="options-panel-section-head">{{text['selection-title']}}</h3>
							<template x-for="entry in ambitEntries">
								<button class="options-panel-button" :class="desired == entry[0] ? 'options-panel-button-on' : 'options-panel-button-off'" x-text="entry[1]" @click="desired = entry[0]"></button>
							</template>
						</div>
					</div>
				</div>
			</template>
			<button class="options-panel-button" @click="bottompanel = !bottompanel; if(bottompanel) {bottompanelopen=true;}" :class="bottompanel? 'options-panel-button-on' : 'options-panel-button-off'">{{text['bottom-panel-toggle']}}</button>
			<p id="bottom-panel-explanation">{{text['bottom-panel-explanation']}}</p>
		</div>
	</div>
	<div id="side-panel-left">
	</div>
	<div id="rite-page-container">
		<div x-show="initialized" id="rite-container" x-html="Rite">
		</div>
		<template x-if="bottompanel">
			<div id="bottom-easy-select-container">
				<button id="bottom-easy-select-hide" @click="bottompanelopen = !bottompanelopen"><img id="bottom-easy-select-hide-icon" :class="!bottompanelopen && 'bottom-easy-select-hide-icon-closed'" src="/resources/svg/arrow-down.svg" /></button>
				<div id="bottom-easy-select-content-container" x-show="bottompanelopen" x-transition>
					<div id="date-selector-container">
						<button id="date-selector-decrement" class="date-selector-button" @click="date = new Date(date.getTime() - 86400000); search = getLocalDate()"><img src="/resources/svg/arrow-left.svg" /></button>
						<input id="date-selector-text" type="date" x-model="search" x-init="search = getLocalDate()" @keyup.enter.window="setDate(search);">
						<button id="date-selector-text-submit" class="date-selector-button" @click="setDate(search);"><img src="/resources/svg/arrow-clockwise.svg" /></button>
						<button id="date-selector-increment" class="date-selector-button" @click="date = new Date(date.getTime() + 86400000); search = getLocalDate()"><img src="/resources/svg/arrow-right.svg" /></button>
					</div>
					<div id="rite-selector-container">
						<template x-for="item in liturgylist">
							<button class="rite-selector-button" :class="(item.id == hour.id) && 'rite-selector-button-selected'" @click="setHour(item.id)" x-text="item.name"></button>
						</template>
					</div>
				</div>
			</div>
		</template>
		<div x-show="initialized" id="next-hour-button-container" x-data="{showtooltip: false}">
			<div style="height:0;" x-intersect="determineNextHour()"></div>
			<button id="next-hour-button" :class="canincrementhour? 'next-hour-button-allowed' : 'next-hour-button-forbidden'" @mouseenter="canincrementhour = canIncrementTo();" @click="if (canincrementhour) {incrementHour()} else {showtooltip = true}" @mouseleave="showtooltip = false" @scroll.window="showtooltip = false">{{text['next-hour']}}<span><img id="next-hour-button-icon" src="/resources/svg/arrow-right.svg" /></span></button>
			<span id="next-hour-forbidden-tooltip" x-show="!canincrementhour && showtooltip">{{text['next-hour-forbidden-tooltip']}}</span>
		</div>
	</div>
	<div id="side-panel-right">
	</div>
	<div id="size-change-listener" x-resize="dopanelsize()"></div>
</div>
		</div>
	</body>
</html>
