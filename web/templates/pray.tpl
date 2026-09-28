<!DOCTYPE html>

<!-- Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% import version_management
% locale = locales[0]
% text = json.load(open(version_management.bestlocalized(f'/pages/{page}.json', locales)))
% import datamanage
% from datetime import datetime, timedelta
% CURSUS_OCCASIONS = ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']
% RITE_TITLES = {'matutinum-laudes': 'Matutinum \N{AMPERSAND} Laudes', 'prima': 'Prima', 'tertia': 'Tertia', 'sexta': 'Sexta', 'nona': 'Nona', 'vesperae': 'Vesperæ', 'completorium': 'Completorium', 'psalmi-graduales': 'Psalmi Graduales', 'psalmi-poenitentiales': 'Psalmi Pœnitentiales', 'ordo-commendationis-animae': 'Ordo Commendationis Animæ', 'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis', 'pro-prandio': 'Benedictio Mensæ (Pro Prandio)', 'pro-coena': 'Benedictio Mensæ (Pro Cœna)', 'itinerarium': 'Itinerarium Clericorum'}
% if date is None:
%   # For bare navigation (just navigation to /pray)
%   rite = ''
%   pdate = datetime.now().date()
%   date = str(pdate)
%   occasion = 'matutinum-laudes'
%   prayer_type = 'officium'
%   select = 'primarium'
%   votives = ''
%   next_hour_href = '#'
%   next_hour_occasion_name = ''
%   day_title = ''
%   rite_title_for_head = ''
% else:
%   rite = datamanage.rendered_rite_request(date, occasion + '+' + prayer_type, options, select, translation, votives)
%   pdate = datetime.strptime(date, '%Y-%m-%d').date()
%   # Frontend navigation just steals the title from the generated rite (sorry, I think that making a call to /api/ordo would in fact suck even more)
%   # so requesting this way relies on the same source of truth and also is cheap since the rite request will've been memoized anyway
%   day_title = datamanage.rite_request(date, occasion + '+' + prayer_type, options, select, translation, votives)['used-primary'][0]
%   rite_title_for_head = RITE_TITLES.get(occasion, occasion)
%   if prayer_type == 'officium' and select != 'officium-defunctorum' and occasion in CURSUS_OCCASIONS:
%     _cursus_idx = CURSUS_OCCASIONS.index(occasion)
%     if _cursus_idx == len(CURSUS_OCCASIONS) - 1:
%       next_hour_date, next_hour_occasion = pdate + timedelta(days=1), CURSUS_OCCASIONS[0]
%     else:
%       next_hour_date, next_hour_occasion = pdate, CURSUS_OCCASIONS[_cursus_idx + 1]
%     end
%     next_hour_select = select
%   else:
%     next_hour_date, next_hour_occasion, next_hour_select = pdate, CURSUS_OCCASIONS[0], 'primarium'
%   end
%   next_hour_occasion_name = RITE_TITLES[next_hour_occasion]
%   next_hour_href = f"/{locale}/officium/{next_hour_date}{'' if next_hour_select == 'primarium' else f'/{next_hour_select}'}/{next_hour_occasion}{'' if len(votives) == 0 else f'?v={votives}'}"
% end

<html lang="{{locale.split('-')[0]}}" x-data :data-theme="$store.theme.current">
	<head>
		% if rite_title_for_head == '':
		<title>{{text['title']}}</title>
		% else:
		<title>{{rite_title_for_head}} | {{day_title}} | Liber Usualis</title>
		% end
		<script type="application/ld+json">
		{
			"@context":"https://schema.org",
			"@type":"WebSite",
			"name":"Liber Usualis",
			"url":"https://liberusualis.org/"
		}
		</script>
    % include('web/resources/themer.tpl')
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei-icon.png">
		<link rel="apple-touch-icon" href="/resources/agnus-dei-apple-touch-icon.png">
		<link rel="preload" href="/resources/fonts/OldStandardTT-Regular.woff2" as="font" type="font/woff2" crossorigin>
		<link rel="preload" href="/resources/fonts/Arsenal-Regular.woff2" as="font" type="font/woff2" crossorigin>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/dist/style.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/dist/pray.css')}}>
		% if mobile:
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/pray/css/pray-mobile.css')}}>
		% end
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.x.x/dist/cdn.min.js"></script>
		<script defer type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src='https://cdn.jsdelivr.net/npm/temporal-polyfill@0.3.0/global.min.js'></script>
		<script type="text/javascript" src={{version_management.get_versioned_resource('/dist/pray.js')}}></script>
	</head>
  <body x-data="{
    optionspanel: false,
    ritesMenuOpen: false,
    bottomPanelEnabled: $persist(false),
    bottomPanelOpen: true,
    displayParameters: $persist({
      'chant': false,
      'displayTrivialChants': false,
      'showTranslation': true,
      'sideBySide': false,
      'playChant': false
    })
    }">
    % include('web/resources/top-bar.tpl', locale=locale, options=True, text=json.load(open(f'web/locales/{locale}/resources/top-bar.json')))
    % include('web/resources/pray/rites-menu.tpl', locale=locale, date=date, text=text)
    <div id="content-container-outer">
    % if not mobile:
    <div x-cloak id="options-panel-background" x-show="optionspanel">
      <div id="options-panel-wrapper" x-trap.noscroll="optionspanel" @click.outside="optionspanel = false">
        % include('web/resources/pray/options-panel.tpl', locale=locale, text=text, date=date)
      </div>
    </div>
    % else:
    <div x-cloak id="options-panel-wrapper-mobile" x-show="optionspanel">
      % include('web/resources/pray/options-panel.tpl', locale=locale, text=text, date=date)
    </div>
    % end
    <div id="rite-page-container">
    <main id="rite-container" x-html="(displayParameters.showTranslation && !displayParameters.sideBySide) ? Pray.lineByLine($store.router.rite) : $store.pray.rite" :class="{
      'chant-shown': displayParameters.chant,
      'chant-hidden': !displayParameters.chant,
      'chant-playback': displayParameters.chant && displayParameters.playChant,
      'side-by-side': displayParameters.showTranslation && displayParameters.sideBySide,
      'line-by-line': displayParameters.showTranslation && !displayParameters.sideBySide,
      'no-translation': !displayParameters.showTranslation
    }">
      {{!rite}}
    </main>
    <div id="next-hour-button-container" x-intersect.margin.0px.0px.400px.0px="Pray.markAsDone($store.pray)" x-data="{now: Temporal.Now.plainDateTimeISO()}">
      <a
        id="next-hour-button"
        href="{{next_hour_href}}"
        :href="Pray.makePath(Pray.nextHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray)))"
        :class="!Pray.canIncrementHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray), now) && 'next-hour-button-forbidden'"
        :title="Pray.canIncrementHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray), now) ? '' : '{{text['next-hour-forbidden-tooltip']}}'"
        @click.prevent="Pray.canIncrementHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray), now) && Pray.navigateRite($store.pray, Pray.makePath(Pray.nextHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray))))"
      >
        <span>
          <span id="next-hour-kicker">{{text['next-hour']}}</span>
          <span id="next-hour-occasion" x-text="Pray.RITE_TITLES[Pray.nextHour(Pray.contentParameters($store.pray.displayPath) || Pray.lastCompletedHour($store.pray)).occasion]">{{!next_hour_occasion_name}}</span>
        </span>
        <svg id="next-hour-button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg>
      </a>
    </div>
    </div>
    <template x-if="bottomPanelEnabled">
      <div id="bottom-easy-select-container">
        <button id="bottom-easy-select-hide" @click="bottomPanelOpen = !bottomPanelOpen"><svg id="bottom-easy-select-hide-icon" :class="!bottomPanelOpen && 'bottom-easy-select-hide-icon-closed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><path fill="currentColor" d="M38.998 15.98 24.003 30.597 9.007 15.98a1.434 1.434 0 0 0-2.004 0 1.365 1.365 0 0 0 0 1.95l15.952 15.554a1.5 1.5 0 0 0 2.095 0l15.952-15.551a1.365 1.365 0 0 0 0-1.956 1.434 1.434 0 0 0-2.004 0z"></path></svg></button>
        <div id="bottom-easy-select-content-container" x-show="bottomPanelOpen" x-transition>
          <div id="date-selector-container" x-data="{search: '{{date}}'}" x-init="$watch('$store.router.displayPath', () => { search = Pray.contentParameters($store.pray.displayPath).date?.toString() ?? search })">
            <a id="date-selector-decrement" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate - timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="Pray.makePath({...Pray.contentParameters($store.pray.displayPath), date: Pray.contentParameters($store.pray.displayPath).date.subtract({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M5.854 4.646a.5.5 0 0 1 0 .708L3.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0"></path><path fill-rule="evenodd" d="M2.5 8a.5.5 0 0 1 .5-.5h10.5a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"></path></g></svg></a>
            <input id="date-selector-text" type="date" x-model="search">
            <a id="date-selector-text-submit" class="date-selector-button" x-rite-link:hard :href="Pray.makePath({...Pray.contentParameters($store.pray.displayPath), date:search})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M3.17 6.706a5 5 0 0 1 7.103-3.16.5.5 0 1 0 .454-.892A6 6 0 1 0 13.455 5.5a.5.5 0 0 0-.91.417 5 5 0 1 1-9.375.789"></path><path fill-rule="evenodd" d="M8.147.146a.5.5 0 0 1 .707 0l2.5 2.5a.5.5 0 0 1 0 .708l-2.5 2.5a.5.5 0 1 1-.707-.708L10.293 3 8.147.854a.5.5 0 0 1 0-.708"></path></g></svg></a>
            <a id="date-selector-increment" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate + timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="Pray.makePath({...Pray.contentParameters($store.pray.displayPath), date: Pray.contentParameters($store.pray.displayPath).date.add({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg></a>
          </div>
          <div id="cursus-rite-selector-container">
            % for item in [['matutinum-laudes', 'Matutinum &amp; Laudes'], ['prima', 'Prima'], ['tertia', 'Tertia'], ['sexta', 'Sexta'], ['nona', 'Nona'], ['vesperae', 'Vesperæ'], ['completorium', 'Completorium']]:
            <a class="cursus-rite-selector-button" :class="Pray.contentParameters($store.pray.displayPath).prayerType == 'officium' && Pray.contentParameters($store.pray.displayPath).select != 'officium-defunctorum' && Pray.contentParameters($store.pray.displayPath).occasion == '{{item[0]}}' ? 'cursus-rite-selector-button-selected' : ''" href="/{{locale}}/officium/{{pdate}}{{'' if select == 'primarium' else f'/{select}'}}/{{item[0]}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="Pray.makePath({...Pray.contentParameters($store.pray.displayPath), prayerType: 'officium', select: Pray.contentParameters($store.pray.displayPath).select == 'officium-defunctorum' ? 'primarium' : Pray.contentParameters($store.pray.displayPath).select, occasion: '{{item[0]}}'})">{{!item[1]}}</a>
            % end
          </div>
        </div>
      </div>
    </template>
    <script defer>
      document.addEventListener('alpine:init', () => {
        Alpine.store('theme', {
          current: document.documentElement.getAttribute('data-theme') || 'light',
          toggle() {
            this.current = this.current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', this.current);
          },
          set(value) {
            this.current = value;
            localStorage.setItem('theme', value);
          }
        });
        Alpine.store('router', {
          // Last completed hour within the normal seven hour cursus
          suggestOccasion() {
            let hour = Temporal.Now.plainTimeISO().hour;
            if (hour < 6 || hour > 21) return 'matutinum-laudes';
            if (hour < 8) return 'prima';
            if (hour < 11) return 'tertia';
            if (hour < 14) return 'sexta';
            if (hour < 16) return 'nona';
            if (hour < 20) return 'vesperae';
            return 'completorium';
          },
          async redirect() {
            let locale = window.location.pathname.match(/^\/([a-z]{2})\//)?.[1] || 'en';
            let now = Temporal.Now.plainDateTimeISO();
            // We're checking if we actually have a last completed hour recorded - since the function lastCompletedHour(prayState) returns a default value rather than null.
            if (!localStorage.getItem('lastCursusHour') || !Pray.canIncrementHour(Pray.lastCompletedHour(Alpine.store('pray')), now)) {
              await Pray.navigateRite(Alpine.store('pray'), Pray.makePath({
                locale: locale,
                prayerType: 'officium',
                date: Temporal.Now.plainDateISO().toString(),
                select: 'primarium',
                occasion: this.suggestOccasion(),
                votives: []
              }), navigationType='soft', action='replace');
            } else {
              await Pray.navigateRite(Alpine.store('pray'), Pray.makePath({...Pray.nextHour(Pray.lastCompletedHour(Alpine.store('pray'))), locale: locale, prayerType: 'officium'}), navigationType='soft', action='replace');
            }
          },
          init() {
            const [navEntry] = performance.getEntriesByType('navigation');
            // Note: If no navigationType is available, this condition will be false, so redirection will not occur.
            if (!Pray.isRitePath(window.location.pathname) || (navEntry?.type === 'reload' && history.state?.navigationType === 'soft')) {
              this.redirect();
            }
          }
        });
        // navigationType (default: soft) is accessed to determine if the user wants the app to automatically switch to a more relevant rite or not on reload / page load.
        Alpine.directive('rite-link', (el, {value}) => {
          let navigationType = value || 'soft';
          el.addEventListener('click', (e) => {
          e.preventDefault();
          Pray.navigateRite(Alpine.store('pray'), new URL(el.href).pathname, navigationType);
          });
        });
      });
      window.addEventListener('popstate', () => {
        let router = Alpine.store('router');
        if (Pray.isRitePath(location.pathname)) {
          Alpine.store('pray').displayPath = location.pathname;
          Pray.navigateRite(location.pathname);
        } else {
          router.redirect();
        }
      });
    </script>
  </body>
</html>
