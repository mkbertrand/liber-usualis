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
		% if mobile:
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/pray-mobile.css')}}>
		% end
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
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/jquery.hypher.js')}}></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/js/la-hypher.js')}}></script>
	</head>
	<body x-data="{
	optionspanel: false,
	bottompanel: $persist(false),
	bottompanelopen: true,
	search: '',
	calendarDate: null,
	liturgicalDay: '',
	hour: null,
	parameters: $persist({
		'desired': 'omnes',
		'recitation': 'recto-tono',
		'translation': false,
		'side-by-side': false,
		'display-trivial-chants': false
	}),
	version: '{{version_management.get_resource_version('/js/ritegen.js')}}-{{version_management.get_resource_version('/styles/pray.css')}}',
	rite: '',
	initialized: false,
	canIncrementOccasion: true,
	nextOccasion: $persist(null),
	get Rite() {
		if (panelsopen) {
			$nextTick(() => generatepanels());
		}
		return this.rite;
	},
	// Sets this.calendarDate with a local date which is adjusted to UTC.
	setCalendarDate(calendarDate) {
		this.calendarDate = new Date(new Date(calendarDate + new Date().toISOString().substring(10)).getTime() + this.calendarDate.getTimezoneOffset() * 60000);
	},
	// Returns the date (yyyy-mm-dd) adjusted for timezone.
	getCalendarDate(calendarDate) {
		return new Date(calendarDate.getTime() - calendarDate.getTimezoneOffset() * 60000).toISOString().substring(0, 10);
	},
	updateRiteAsyncLock: false,
	async updateRite(scroll = true) {
		if (!this.updateRiteAsyncLock) {
			this.updateRiteAsyncLock = true;

			this.rite = getRite(this.getCalendarDate(this.calendarDate), this.hour, this.parameters, this.version);
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
	async updateLiturgicalDay() {
		this.liturgicalDay = await getLiturgicalDay(this.getCalendarDate(this.calendarDate), getTime(this.hour), this.parameters);
		this.updateRite();
		this.ignoreCalendarDateChange = false;
	},
	setOccasion(id) {
		oldTime = getTime(this.hour);
		this.hour = id;
		if (oldTime != getTime(this.hour)) {
			this.updateLiturgicalDay();
		} else {
			this.updateRite();
		}
	},
	async incrementOccasion() {
		// Otherwise things will happen async that need to be synchronous
		this.ignoreCalendarDateChange = true;
		this.calendarDate = this.nextOccasion[0];
		this.search = this.getCalendarDate(this.calendarDate);
		// This has the effect of actually hitting updateLiturgicalDay()
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
		this.nextOccasion = [resolveParameters(this.parameters).ambit.idindex(this.hour) + 1 == resolveParameters(this.parameters).ambit.occasions.length ? new Date(this.calendarDate.getTime() + 86400000) : this.calendarDate, resolveParameters(this.parameters).ambit.nextOccasion(this.hour).id];
		getRite(this.getCalendarDate(this.nextOccasion[0]), this.nextOccasion[1], this.parameters, this.version);
	}
}" x-init="
	if (!('votives' in parameters)) {
		parameters.votives = {'de-sanctis-angelis': false, 'de-sanctis-apostolis': false, 'de-joseph': false, 'de-eucharistiae-sacramento': false, 'de-passione': false, 'de-immaculata-conceptione': false};
	}
	% if not mobile:
	doPanelSize();
	% end
	parameters.locale = '{{locale}}';
	if (parameters.locale == 'la') {
		parameters.translation = false;
	}
	if (nextOccasion && typeof nextOccasion[0] === 'string') {
		nextOccasion[0] = new Date(nextOccasion[0]);
	}

	if (canIncrementTo()) {
		calendarDate = nextOccasion[0];
		hour = nextOccasion[1];
	} else {
		calendarDate = new Date();
		hour = resolveParameters(parameters).ambit.suggestSelectedOccasion(calendarDate.getHours()).id;
	}

	$watch('calendarDate', calendarDate => {if (!ignoreCalendarDateChange) {updateLiturgicalDay()}});
	$watch('parameters', (parameters, oldParameters) => {
		hour = resolveParameters(oldParameters).ambit.slideAmbitOccasion(resolveParameters(parameters).ambit, hour);
		updateRite();
		nextOccasion = null;
	});
	updateLiturgicalDay();
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
				% if not mobile:
				<div x-cloak id="options-panel-background" x-show="optionspanel">
					<div id="options-panel-wrapper" x-trap.noscroll="optionspanel" @click.outside="optionspanel = false">
						% include('web/resources/options-panel.tpl', locale=locale, text=text)
					</div>
				</div>
				% else:
					<div x-cloak id="options-panel-wrapper-mobile" x-show="optionspanel">
						% include('web/resources/options-panel.tpl', locale=locale, text=text)
					</div>
				% end
				% if not mobile:
					<div id="side-panel-left">
					</div>
				% end
				<div id="rite-page-container">
					<div x-show="initialized" id="rite-container" x-html="Rite">
					</div>
					<template x-if="bottompanel">
						<div id="bottom-easy-select-container">
							<button id="bottom-easy-select-hide" @click="bottompanelopen = !bottompanelopen"><img id="bottom-easy-select-hide-icon" :class="!bottompanelopen && 'bottom-easy-select-hide-icon-closed'" src="/resources/svg/arrow-down.svg" /></button>
							<div id="bottom-easy-select-content-container" x-show="bottompanelopen" x-transition>
								<div id="date-selector-container">
									<button id="date-selector-decrement" class="date-selector-button" @mouseover.throttle="getRite(getCalendarDate(new Date(calendarDate.getTime() - 86400000)), hour, parameters, version)" @click="calendarDate = new Date(calendarDate.getTime() - 86400000); search = getCalendarDate(calendarDate); getRite(getCalendarDate(new Date(calendarDate.getTime() - 86400000)), hour, parameters, version);"><img src="/resources/svg/arrow-left.svg" /></button>
									<input id="date-selector-text" type="date" x-model="search" x-init="search = getCalendarDate(calendarDate)">
									<button id="date-selector-text-submit" class="date-selector-button" @mouseover.throttle="getRite(search, hour, parameters, version)" @click="setCalendarDate(search)"><img src="/resources/svg/arrow-clockwise.svg" /></button>
									<button id="date-selector-increment" class="date-selector-button" @mouseover.throttle="getRite(getCalendarDate(new Date(calendarDate.getTime() + 86400000)), hour, parameters, version)" @click="calendarDate = new Date(calendarDate.getTime() + 86400000); search = getCalendarDate(calendarDate); getRite(getCalendarDate(new Date(calendarDate.getTime() + 86400000)), hour, parameters, version);"><img src="/resources/svg/arrow-right.svg" /></button>
								</div>
								<div id="rite-selector-container">
									<template x-for="occasion in resolveParameters(parameters).ambit.occasions">
										<button class="rite-selector-button" :class="(occasion.id == hour) && 'rite-selector-button-selected'" @mouseover.throttle="getRite(getCalendarDate(calendarDate), occasion.id, parameters, version)" @click="setOccasion(occasion.id)" x-text="occasion.name"></button>
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
				% if not mobile:
				<div id="side-panel-right">
				</div>
				<div id="size-change-listener" x-resize="doPanelSize()"></div>
				% end
			</div>
		</div>
	</body>
</html>
