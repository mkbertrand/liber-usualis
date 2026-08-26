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
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei-icon.png">
		<link rel="apple-touch-icon" href="/resources/agnus-dei-apple-touch-icon.png">
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/style.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/dist/pray.css')}}>
		% if mobile:
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/pray/css/pray-mobile.css')}}>
		% end
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/pray/js/pray-window.js')}}></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/dist/pray.js')}}></script>
	</head>
	<body x-data="{
	optionspanel: false,
	bottompanel: $persist(false),
	bottompanelopen: true,
	darkMode: $persist(false).as('dark-mode'),
	search: '',
	calendarDate: null,
	liturgicalDay: '',
	hour: null,
	parameters: $persist({
		'desired': 'omnes',
		'priest': true,
		'translation': true
	}),
  displayParameters: $persist({
    'chant': false,
		'display-trivial-chants': false,
		'side-by-side': false
  }),
	rite: '',
	initialized: false,
	canIncrementOccasion: true,
	nextOccasion: $persist(null),
  resources: new Pray.CorpusResources(),
	get Rite() {
		if (panelsopen) {
			$nextTick(() => generatepanels());
		}
		return this.displayParameters['side-by-side'] || !this.initialized ? this.rite : this.rite.then(Pray.lineByLine);
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

			this.rite = getRite(this.getCalendarDate(this.calendarDate), this.hour, this.parameters, this.resources);
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
		if (this.nextOccasion[1] == 'matutinum-laudes' && zeroedsetdate - 86400000 == zeroedcurrentdate - 0) {
			return new Date().getHours() >= 14;
		} else {
			return zeroedsetdate - 0 == zeroedcurrentdate - 0;
		}
	},
	// Not biased as to whether the 'next hour' can be said or not. That's for canIncrementTo to determine.
	determineNextHour() {
		this.nextOccasion = [resolveParameters(this.parameters).ambit.riteIndex(this.hour) + 1 == resolveParameters(this.parameters).ambit.occasions.length ? new Date(this.calendarDate.getTime() + 86400000) : this.calendarDate, resolveParameters(this.parameters).ambit.nextOccasion(this.hour).rite];
		getRite(this.getCalendarDate(this.nextOccasion[0]), this.nextOccasion[1], this.parameters, this.resources);
	}
}" x-init="
  resources.load();
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
  
  var urlGovernedOccasion = window.location.href.match(/pray\/(.+?)\/(.+)$/);
  if (urlGovernedOccasion && urlGovernedOccasion.length == 3) {
		calendarDate = new Date();
    setCalendarDate(urlGovernedOccasion[1]);
    hour = urlGovernedOccasion[2];
  } else if (canIncrementTo()) {
		calendarDate = nextOccasion[0];
		hour = nextOccasion[1];
	} else {
		calendarDate = new Date();
		hour = resolveParameters(parameters).ambit.suggestSelectedOccasion(calendarDate.getHours()).rite;
	}

	$watch('calendarDate', calendarDate => {if (!ignoreCalendarDateChange) {updateLiturgicalDay()}});
	$watch('parameters', (parameters, oldParameters) => {
		hour = resolveParameters(oldParameters).ambit.slideAmbitOccasion(resolveParameters(parameters).ambit, hour);
		updateRite();
		nextOccasion = null;
	});
	updateLiturgicalDay();
	" :data-theme="darkMode ? 'dark' : 'light'">
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen">
				% include('web/resources/svg/hamburger-menu.tpl')
			</button>
				<div id="project-logo">
					<div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.webp" alt="LIBER USUALIS"></a></div>
				</div>
				<button id="options-gear-wrapper" @click="optionspanel = !optionspanel">
					<svg id="options-gear" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%"><path d="M262.29 192.31a64 64 0 1057.4 57.4 64.13 64.13 0 00-57.4-57.4zM416.39 256a154.34 154.34 0 01-1.53 20.79l45.21 35.46a10.81 10.81 0 012.45 13.75l-42.77 74a10.81 10.81 0 01-13.14 4.59l-44.9-18.08a16.11 16.11 0 00-15.17 1.75A164.48 164.48 0 01325 400.8a15.94 15.94 0 00-8.82 12.14l-6.73 47.89a11.08 11.08 0 01-10.68 9.17h-85.54a11.11 11.11 0 01-10.69-8.87l-6.72-47.82a16.07 16.07 0 00-9-12.22 155.3 155.3 0 01-21.46-12.57 16 16 0 00-15.11-1.71l-44.89 18.07a10.81 10.81 0 01-13.14-4.58l-42.77-74a10.8 10.8 0 012.45-13.75l38.21-30a16.05 16.05 0 006-14.08c-.36-4.17-.58-8.33-.58-12.5s.21-8.27.58-12.35a16 16 0 00-6.07-13.94l-38.19-30A10.81 10.81 0 0149.48 186l42.77-74a10.81 10.81 0 0113.14-4.59l44.9 18.08a16.11 16.11 0 0015.17-1.75A164.48 164.48 0 01187 111.2a15.94 15.94 0 008.82-12.14l6.73-47.89A11.08 11.08 0 01213.23 42h85.54a11.11 11.11 0 0110.69 8.87l6.72 47.82a16.07 16.07 0 009 12.22 155.3 155.3 0 0121.46 12.57 16 16 0 0015.11 1.71l44.89-18.07a10.81 10.81 0 0113.14 4.58l42.77 74a10.8 10.8 0 01-2.45 13.75l-38.21 30a16.05 16.05 0 00-6.05 14.08c.33 4.14.55 8.3.55 12.47z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>
				</button>
			</div>
			% include('web/resources/sidemenu.tpl', locale=locale, text=json.load(open(f'web/locales/{locale}/resources/sidemenu.json')))

			<div id="content-container-outer">
				% if not mobile:
				<div x-cloak id="options-panel-background" x-show="optionspanel">
					<div id="options-panel-wrapper" x-trap.noscroll="optionspanel" @click.outside="optionspanel = false">
						% include('web/resources/pray/options-panel.tpl', locale=locale, text=text)
					</div>
				</div>
				% else:
					<div x-cloak id="options-panel-wrapper-mobile" x-show="optionspanel">
						% include('web/resources/pray/options-panel.tpl', locale=locale, text=text)
					</div>
				% end
				% if not mobile:
					<div id="side-panel-left">
					</div>
				% end
				<div id="rite-page-container">
					<div x-show="initialized" id="rite-container" x-html="Rite" :class="{
            'chant-shown': displayParameters.chant,
            'chant-hidden': !displayParameters.chant,
            'side-by-side': displayParameters['side-by-side'] && parameters.translation,
            'line-by-line': !displayParameters['side-by-side'] && parameters.translation,
            'no-translation': !parameters.translation
            }">
					</div>
					<template x-if="bottompanel">
						<div id="bottom-easy-select-container">
							<button id="bottom-easy-select-hide" @click="bottompanelopen = !bottompanelopen"><svg id="bottom-easy-select-hide-icon" :class="!bottompanelopen && 'bottom-easy-select-hide-icon-closed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><path fill="currentColor" d="M38.998 15.98 24.003 30.597 9.007 15.98a1.434 1.434 0 0 0-2.004 0 1.365 1.365 0 0 0 0 1.95l15.952 15.554a1.5 1.5 0 0 0 2.095 0l15.952-15.551a1.365 1.365 0 0 0 0-1.956 1.434 1.434 0 0 0-2.004 0z"></path></svg></button>
							<div id="bottom-easy-select-content-container" x-show="bottompanelopen" x-transition>
								<div id="date-selector-container">
									<button id="date-selector-decrement" class="date-selector-button" @mouseover.throttle="getRite(getCalendarDate(new Date(calendarDate.getTime() - 86400000)), hour, parameters, resources)" @click="calendarDate = new Date(calendarDate.getTime() - 86400000); search = getCalendarDate(calendarDate); getRite(getCalendarDate(new Date(calendarDate.getTime() - 86399999)), hour, parameters, resources);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M5.854 4.646a.5.5 0 0 1 0 .708L3.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0"></path><path fill-rule="evenodd" d="M2.5 8a.5.5 0 0 1 .5-.5h10.5a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"></path></g></svg></button>
									<input id="date-selector-text" type="date" x-model="search" x-init="search = getCalendarDate(calendarDate)">
									<button id="date-selector-text-submit" class="date-selector-button" @mouseover.throttle="getRite(search, hour, parameters, resources)" @click="setCalendarDate(search)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M3.17 6.706a5 5 0 0 1 7.103-3.16.5.5 0 1 0 .454-.892A6 6 0 1 0 13.455 5.5a.5.5 0 0 0-.91.417 5 5 0 1 1-9.375.789"></path><path fill-rule="evenodd" d="M8.147.146a.5.5 0 0 1 .707 0l2.5 2.5a.5.5 0 0 1 0 .708l-2.5 2.5a.5.5 0 1 1-.707-.708L10.293 3 8.147.854a.5.5 0 0 1 0-.708"></path></g></svg></button>
									<button id="date-selector-increment" class="date-selector-button" @mouseover.throttle="getRite(getCalendarDate(new Date(calendarDate.getTime() + 86400000)), hour, parameters, resources)" @click="calendarDate = new Date(calendarDate.getTime() + 86400000); search = getCalendarDate(calendarDate); getRite(getCalendarDate(new Date(calendarDate.getTime() + 86400000)), hour, parameters, resources);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg></button>
								</div>
								<div id="rite-selector-container">
									<template x-for="occasion in resolveParameters(parameters).ambit.occasions">
										<button class="rite-selector-button" :class="(occasion.rite == hour) && 'rite-selector-button-selected'" @mouseover.throttle="getRite(getCalendarDate(calendarDate), occasion.rite, parameters, resources)" @click="setOccasion(occasion.rite)" x-text="occasion.name"></button>
									</template>
								</div>
							</div>
						</div>
					</template>
					<div x-show="initialized" id="next-hour-button-container" x-data="{showtooltip: false}">
						<div style="height:0;" x-intersect="determineNextHour()"></div>
						<button id="next-hour-button" :class="canIncrementOccasion? 'next-hour-button-allowed' : 'next-hour-button-forbidden'" @mouseenter="canIncrementOccasion = canIncrementTo();" @click="if (canIncrementOccasion) {incrementOccasion()} else {showtooltip = true}" @mouseleave="showtooltip = false" @scroll.window="showtooltip = false">{{text['next-hour']}}<span><svg id="next-hour-button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg></span></button>
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
