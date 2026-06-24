<!DOCTYPE html>

<!-- Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% import version_management
% locale = locales[0]
% text = json.load(open(version_management.bestlocalized(f'/pages/{page}.json', locales)))

<html lang="{{locale.split('-')[0]}}">
	<head>
		<title>{{text['title']}}</title>
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
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/style.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/pray.css')}}>
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
		<style>
			@import url('https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap');
		</style>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/pray.js')}}></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/ambit.js')}}></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/ritegen.js')}}></script>
		<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/exsurge.js')}}></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/gabc-chant.js')}}></script>
	</head>
	<body x-data="{
	optionspanel: false,
	bottompanel: $persist(false),
	bottompanelopen: true,
	search: '',
	calendarDate: null,
	liturgicalday: '',
	hour: null,
	desired: $persist('omnes'),
	ambit: null,
	recitation: $persist('recto-tono'),
	translation: $persist(false),
	sidebyside: $persist(false),
	rite: '',
	initialized: false,
	canIncrementOccasion: true,
	nextOccasion: $persist(null),
	version: '{{version_management.get_resource_version('/js/ritegen.js')}}-{{version_management.get_resource_version('/styles/pray.css')}}',
	get Rite() {
		if (panelsopen) {
			$nextTick(() => generatepanels());
		}
		return this.rite;
	},
	getTime() {
		return (this.hour == 'vesperae' || this.hour == 'completorium') ? 'vesperale' : 'diurnale';
	},
	// Sets this.calendarDate with a local date which is adjusted to UTC.
	setCalendarDate(calendarDate) {
		this.calendarDate = new Date(new Date(calendarDate + new Date().toISOString().substring(10)).getTime() + this.calendarDate.getTimezoneOffset() * 60000);
	},
	// Returns the date (yyyy-mm-dd) adjusted for timezone.
	getCalendarDate() {
		return new Date(this.calendarDate.getTime() - this.calendarDate.getTimezoneOffset() * 60000).toISOString().substring(0, 10);
	},
	choral() {
		return this.recitation != 'private';
	},
	chant() {
		return this.recitation == 'plainchant';
	},
	setRecitation(recitation) {
		this.recitation = recitation;
		this.ambit = defineambit(this.desired, this.choral());
	},
	updateRiteAsyncLock: false,
	async updateRite(scroll = true) {
		if (!this.updateRiteAsyncLock) {
			this.updateRiteAsyncLock = true;

			riteRenderingOptions = {'chant': this.chant(), 'disable-trivial-chant': true, 'translation': this.translation, 'side-by-side': this.sidebyside};

			var response = await fetch(`/title?date=${this.getCalendarDate()}
				&hour=${this.hour}
				&select=${this.ambit.occasions[this.ambit.idindex(this.hour)].title}
			`);
			let titleJSON = await response.json();
			newRite = riteTitle(titleJSON[0], titleJSON[1], 'large');
			previousTitle = titleJSON[0];
			rites = this.ambit.riteList(this.liturgicalday.tags, this.hour);
			for (var i = 0; i < rites.length; i++) {
				noending = false;
				if (i != rites.length - 1 && (rites[i + 1][1] == 'officium-parvum-bmv' || rites[i + 1][1] == 'officium-defunctorum' || rites[i + 1][0] == 'psalmi-poenitentiales' || rites[i + 1][0] == 'litaniae-sanctorum' || rites[i + 1][0] == 'officium-capituli')) {
					noending = true;
				}
				var response = await fetch(`/rite?date=${this.getCalendarDate()}
					&hour=${rites[i][0]}&noending=${noending}
					&translation=${this.translation ? translation('{{locale}}') : 'none'}
					&privata=${!this.choral() ? 'privata': 'chorali'}
					&select=${rites[i][1]}
					&version=${this.version}
				`);
				if (response.status == 400 || response.status == 500) {
					newRite = await response.text();
					break;
				}
				var json = await response.json();
				if (!json.rite.tags.includes('aperi-domine') && !json.rite.tags.includes('sacrosanctae') && !json.rite.tags.includes('antiphona-bmv') && !json.rite.tags.includes('officium-capituli') && json['used-primary'][0] != previousTitle) {
					newRite += riteTitle(json['used-primary'][0], json['used-primary'][1], 'small');
					previousTitle = json['used-primary'][0];
				}
				newRite += renderRite(json, riteRenderingOptions);
			}
			this.rite = newRite;
			if (scroll) {
				window.scrollTo({top:0});
			}
			this.initialized = true;
			this.updateRiteAsyncLock = false;
		} else {
			console.log('Simultaneous attempts to update Rite');
		}
	},
	ignoreCalendarDateChange: false,
	async updateDay() {
		var response = await fetch(`/day?date=${this.getCalendarDate()}&time=${this.getTime()}`);
		var json = await response.json();
		var primary = json.primary[1];
		this.liturgicalday = json;
		this.updateRite();
		this.ignoreCalendarDateChange = false;
	},
	setOccasion(id) {
		oldTime = this.getTime();
		this.hour = id;
		if (oldTime != this.getTime()) {
			this.updateDay();
		} else {
			this.updateRite();
		}
	},
	async incrementOccasion() {
		// Otherwise things will happen async that need to be synchronous
		this.ignoreCalendarDateChange = true;
		this.calendarDate = this.nextOccasion[0];
		this.search = this.getCalendarDate();
		// This has the effect of actually hitting updateDay()
		await this.setOccasion(this.nextOccasion[1]);
	},
	canIncrementTo() {
		if (this.nextOccasion == null) {
			return false;
		}
		zeroedsetdate = new Date(this.nextOccasion[0].getFullYear(), this.nextOccasion[0].getMonth(), this.nextOccasion[0].getDate());
		currentdate = new Date();
		zeroedcurrentdate = new Date(currentdate.getFullYear(), currentdate.getMonth(), currentdate.getDate());
		if (this.nextOccasion[1] == 'matutinum' && zeroedsetdate - 86400000 == zeroedcurrentdate - 0) {
			return new Date().getHours() >= 14;
		} else {
			return zeroedsetdate - 0 == zeroedcurrentdate - 0;
		}
	},
	// Not biased as to whether the 'next hour' can be said or not. That's for canIncrementTo to determine.
	determineNextHour() {
		this.nextOccasion = [this.ambit.idindex(this.hour) + 1 == this.ambit.occasions.length ? new Date(this.calendarDate.getTime() + 86400000) : this.calendarDate, this.ambit.nextOccasion(this.hour).id]
	},
	setAmbit(ambit) {
		oldambit = this.ambit;
		this.ambit = ambit;
		this.hour = oldambit.slideAmbitOccasion(this.ambit, this.hour);
		this.updateRite();
		this.nextOccasion = null;
	}
}" x-init="
	dopanelsize();
	if ('{{locale}}' == 'la') {
		translation = false;
	}
	if (ambit === null) {
		ambit = defineambit(desired, choral());
	}
	if (nextOccasion && typeof nextOccasion[0] === 'string') {
		nextOccasion[0] = new Date(nextOccasion[0]);
	}

	if (canIncrementTo()) {
		calendarDate = nextOccasion[0];
		hour = nextOccasion[1];
	} else {
		calendarDate = new Date();
		hour = ambit.suggestSelectedOccasion(calendarDate.getHours()).id;
	}

	$watch('calendarDate', calendarDate => {if (!ignoreCalendarDateChange) {updateDay()}});
	$watch('desired', desired => setAmbit(defineambit(desired, choral())));
	$watch('recitation', recitation => updateRite(false));
	$watch('translation', translation => updateRite());
	$watch('sidebyside', sidebyside => updateRite());
	updateDay();
	">
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen"><img id="sidebar-nav-toggle" src="/resources/svg/hamburger-menu.svg" /></button>
				<div id="project-logo">
					<div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS"></a></div>
				</div>
				<select id="locale-selector" @change="window.location.assign('/' + $event.target.value + window.location.pathname.slice(3) + window.location.search)">
					<option value="la" {{!'selected' if locale == 'la' else ''}}>LA</option>
					<option value="en" {{!'selected' if locale == 'en' else ''}}>EN</option>
					<option value="de" {{!'selected' if locale == 'de' else ''}}>DE</option>
				</select>
				<button id="options-gear-wrapper" @click="optionspanel = !optionspanel">
					<img id="options-gear" src="/resources/svg/settings-outline.svg" />
				</button>
			</div>
			% include('web/resources/sidemenu.tpl', locale=locale, text=json.load(open(f'web/locales/{locale}/resources/sidemenu.json')))

			<div id="content-container-outer">
				<div x-cloak id="options-panel-background" x-show="optionspanel">
					<div id="options-panel" x-trap.noscroll="optionspanel" @click.outside="optionspanel = false">
						<h3 id="options-panel-title">{{text['options-panel-title']}}</h3>
						% if locale != 'la':
						<button class="options-panel-button" @click="translation = !translation" :class="translation? 'options-panel-button-on' : 'options-panel-button-off'">{{text['translation-toggle']}}</button>
						<button class="options-panel-button" @click="sidebyside = !sidebyside" :class="sidebyside? 'options-panel-button-on' : 'options-panel-button-off'">Side-by-side translation (experimental)</button>
						% end
						<div class="recitation-select-container">
							<button class="options-panel-button recitation-select-button" @click="setRecitation('plainchant');" :class="recitation == 'plainchant'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-plainchant']}}</button>
							<button class="options-panel-button recitation-select-button" @click="setRecitation('recto-tono');" :class="recitation == 'recto-tono'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-recto-tono']}}</button>
							<button class="options-panel-button recitation-select-button" @click="setRecitation('private');" :class="recitation == 'private'? 'options-panel-button-on' : 'options-panel-button-off'">{{text['recitation-select-private']}}</button>
						</div>
						<template x-if="initialized">
							<div id="options-panel-require-initialized-container">
								<div id="options-panel-sides">
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
										<div id="ambit-select-container" x-data="{ambitEntries: [
											['omnes', 'Officium'],
											['diei', 'Officium diei'],
											['officium-parvum-bmv', 'Officium Parvum B.M.V.'],
											['officium-defunctorum', 'Officium Defunctorum'],
											['semper-cum-opbmv', 'Officium diei cum Officio Parvo B.M.V.']
										]}">
											<h3 class="options-panel-section-head">{{text['selection-title']}}</h3>
											<template x-for="entry in ambitEntries">
												<button class="options-panel-button" :class="desired == entry[0] ? 'options-panel-button-on' : 'options-panel-button-off'" x-text="entry[1]" @click="desired = entry[0]"></button>
											</template>
										</div>
									</div>
								</div>
								<div id="occasional-rite-selection" x-data="{ambitEntries: [
									['psalmi-graduales', 'Psalmi Graduales'],
									['psalmi-poenitentiales', 'Psalmi Pœnitentiales'],
									['ordo-commendationis-animae', 'Ordo Commendationis Animæ'],
									['formula-indulgentiam-articulo-mortis', 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis.'],
									['benedictio-mensae', 'Benedictio Mensæ'],
									['itinerarium', 'Itinerarium Clericorum'],
								]}">
									<h3 class="options-panel-section-head">{{text['selection-title']}}</h3>
									<template x-for="entry in ambitEntries">
										<button class="options-panel-button" :class="desired == entry[0] ? 'options-panel-button-on' : 'options-panel-button-off'" x-text="entry[1]" @click="desired = entry[0]"></button>
									</template>
								</div>
							</div>
						</template>
						<div id="bottom-panel-options-container">
							<button id="bottom-panel-toggle-button" class="options-panel-button" @click="bottompanel = !bottompanel; if(bottompanel) {bottompanelopen=true;}" :class="bottompanel? 'options-panel-button-on' : 'options-panel-button-off'">{{text['bottom-panel-toggle']}}</button>
							<p id="bottom-panel-explanation">{{text['bottom-panel-explanation']}}</p>
						</div>
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
									<button id="date-selector-decrement" class="date-selector-button" @click="calendarDate = new Date(calendarDate.getTime() - 86400000); search = getCalendarDate()"><img src="/resources/svg/arrow-left.svg" /></button>
									<input id="date-selector-text" type="date" x-model="search" x-init="search = getCalendarDate()">
									<button id="date-selector-text-submit" class="date-selector-button" @click="setCalendarDate(search);"><img src="/resources/svg/arrow-clockwise.svg" /></button>
									<button id="date-selector-increment" class="date-selector-button" @click="calendarDate = new Date(calendarDate.getTime() + 86400000); search = getCalendarDate()"><img src="/resources/svg/arrow-right.svg" /></button>
								</div>
								<div id="rite-selector-container">
									<template x-for="occasion in ambit.occasions">
										<button class="rite-selector-button" :class="(occasion.id == hour) && 'rite-selector-button-selected'" @click="setOccasion(occasion.id)" x-text="occasion.name"></button>
									</template>
								</div>
							</div>
						</div>
					</template>
					<div x-show="initialized" id="next-hour-button-container" x-data="{showtooltip: false}">
						<div style="height:0;" x-intersect="determineNextHour()"></div>
						<button id="next-hour-button" :class="canIncrementOccasion? 'next-hour-button-allowed' : 'next-hour-button-forbidden'" @mouseenter="canIncrementOccasion = canIncrementTo();" @click="if (canIncrementOccasion) {incrementOccasion()} else {showtooltip = true}" @mouseleave="showtooltip = false" @scroll.window="showtooltip = false">{{text['next-hour']}}<span><img id="next-hour-button-icon" src="/resources/svg/arrow-right.svg" /></span></button>
						<span id="next-hour-forbidden-tooltip" x-show="!canIncrementOccasion && showtooltip">{{text['next-hour-forbidden-tooltip']}}</span>
					</div>
				</div>
				<div id="side-panel-right">
				</div>
				<div id="size-change-listener" x-resize="dopanelsize()"></div>
			</div>
		</div>
	</body>
</html>
