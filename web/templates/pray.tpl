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
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/style.css')}}>
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
    sidebarnavopen: false,
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
    % include('web/resources/top-bar.tpl', locale=locale, options=True)
    % include('web/resources/pray/rites-menu.tpl', locale=locale, date=date, text=text)
    % include('web/resources/sidemenu.tpl', locale=locale, text=json.load(open(f'web/locales/{locale}/resources/sidemenu.json')))
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
    <main id="rite-container" x-html="(displayParameters.showTranslation && !displayParameters.sideBySide) ? Pray.lineByLine($store.router.rite) : $store.router.rite" :class="{
      'chant-shown': displayParameters.chant,
      'chant-hidden': !displayParameters.chant,
      'chant-playback': displayParameters.chant && displayParameters.playChant,
      'side-by-side': displayParameters.showTranslation && displayParameters.sideBySide,
      'line-by-line': displayParameters.showTranslation && !displayParameters.sideBySide,
      'no-translation': !displayParameters.showTranslation
    }">
      {{!rite}}
    </main>
    <div id="next-hour-button-container" x-intersect.margin.0px.0px.400px.0px="$store.router.recordCursusPosition()">
      <a
        id="next-hour-button"
        href="{{next_hour_href}}"
        :href="$store.router.makeURL($store.router.nextHour($store.router.contentParameters() || $store.router.lastCompletedHour()))"
        :class="!$store.router.canIncrementHour($store.router.contentParameters() || $store.router.lastCompletedHour()) && 'next-hour-button-forbidden'"
        :title="$store.router.canIncrementHour($store.router.contentParameters() || $store.router.lastCompletedHour()) ? '' : '{{text['next-hour-forbidden-tooltip']}}'"
        @click.prevent="$store.router.canIncrementHour($store.router.contentParameters() || $store.router.lastCompletedHour()) && $store.router.navigateRite($store.router.makeURL($store.router.nextHour($store.router.contentParameters() || $store.router.lastCompletedHour())))"
      >
        <span>
          <span id="next-hour-kicker">{{text['next-hour']}}</span>
          <span id="next-hour-occasion" x-text="$store.router.RITE_TITLES[$store.router.nextHour($store.router.contentParameters() || $store.router.lastCompletedHour()).occasion]">{{!next_hour_occasion_name}}</span>
        </span>
        <svg id="next-hour-button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg>
      </a>
    </div>
    </div>
    <template x-if="bottomPanelEnabled">
      <div id="bottom-easy-select-container">
        <button id="bottom-easy-select-hide" @click="bottomPanelOpen = !bottomPanelOpen"><svg id="bottom-easy-select-hide-icon" :class="!bottomPanelOpen && 'bottom-easy-select-hide-icon-closed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><path fill="currentColor" d="M38.998 15.98 24.003 30.597 9.007 15.98a1.434 1.434 0 0 0-2.004 0 1.365 1.365 0 0 0 0 1.95l15.952 15.554a1.5 1.5 0 0 0 2.095 0l15.952-15.551a1.365 1.365 0 0 0 0-1.956 1.434 1.434 0 0 0-2.004 0z"></path></svg></button>
        <div id="bottom-easy-select-content-container" x-show="bottomPanelOpen" x-transition>
          <div id="date-selector-container" x-data="{search: '{{date}}'}">
            <a id="date-selector-decrement" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate - timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="$store.router.makeURL({date: $store.router.contentParameters().date.subtract({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M5.854 4.646a.5.5 0 0 1 0 .708L3.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0"></path><path fill-rule="evenodd" d="M2.5 8a.5.5 0 0 1 .5-.5h10.5a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"></path></g></svg></a>
            <input id="date-selector-text" type="date" x-model="search">
            <a id="date-selector-text-submit" class="date-selector-button" x-rite-link:hard :href="$store.router.makeURL({date:search})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M3.17 6.706a5 5 0 0 1 7.103-3.16.5.5 0 1 0 .454-.892A6 6 0 1 0 13.455 5.5a.5.5 0 0 0-.91.417 5 5 0 1 1-9.375.789"></path><path fill-rule="evenodd" d="M8.147.146a.5.5 0 0 1 .707 0l2.5 2.5a.5.5 0 0 1 0 .708l-2.5 2.5a.5.5 0 1 1-.707-.708L10.293 3 8.147.854a.5.5 0 0 1 0-.708"></path></g></svg></a>
            <a id="date-selector-increment" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate + timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="$store.router.makeURL({date: $store.router.contentParameters().date.add({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg></a>
          </div>
          <div id="cursus-rite-selector-container">
            % for item in [['matutinum-laudes', 'Matutinum &amp; Laudes'], ['prima', 'Prima'], ['tertia', 'Tertia'], ['sexta', 'Sexta'], ['nona', 'Nona'], ['vesperae', 'Vesperæ'], ['completorium', 'Completorium']]:
            <a class="cursus-rite-selector-button" :class="$store.router.contentParameters().prayerType == 'officium' && $store.router.contentParameters().select != 'officium-defunctorum' && $store.router.contentParameters().occasion == '{{item[0]}}' ? 'cursus-rite-selector-button-selected' : ''" href="/{{locale}}/officium/{{pdate}}{{'' if select == 'primarium' else f'/{select}'}}/{{item[0]}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link:hard :href="$store.router.makeURL({prayerType: 'officium', select: $store.router.contentParameters().select == 'officium-defunctorum' ? 'primarium' : $store.router.contentParameters().select, occasion: '{{item[0]}}'})">{{!item[1]}}</a>
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
          rite: document.querySelector('main').innerHTML,
          displayPath: window.location.pathname,
          CURSUS_OCCASIONS: ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium'],
          RITE_TITLES: {
            'matutinum-laudes': 'Matutinum & Laudes', 'prima': 'Prima', 'tertia': 'Tertia',
            'sexta': 'Sexta', 'nona': 'Nona', 'vesperae': 'Vesperæ', 'completorium': 'Completorium',
            'psalmi-graduales': 'Psalmi Graduales', 'psalmi-poenitentiales': 'Psalmi Pœnitentiales',
            'ordo-commendationis-animae': 'Ordo Commendationis Animæ',
            'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis',
            'pro-prandio': 'Benedictio Mensæ (Pro Prandio)', 'pro-coena': 'Benedictio Mensæ (Pro Cœna)',
            'itinerarium': 'Itinerarium Clericorum'
          },

          // Last completed hour within the normal seven hour cursus
          lastCompletedHour() {
            let lastCompleted = JSON.parse(localStorage.getItem('lastCursusHour') || 'null')
            if (lastCompleted) {
              return {...lastCompleted, date: Temporal.PlainDate.from(lastCompleted.date)};
            } else {
              return {date: Temporal.Now.plainDateISO(), select: 'primarium', occasion: 'matutinum-laudes', votives: []};
            }
          },
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
          isRitePath(path) {
            return /\/[a-z]{2}\/(officium|ritus)\/\d{4}-\d{1,2}-\d{1,2}(\/|$)/.test(path);
          },
          contentParameters(path=this.displayPath) {
            if (!this.isRitePath(path)) return {};
            let pathVariables = path.match(/\/(?<locale>[a-z]{2})\/(?<prayerType>officium|ritus)\/(?<date>\d{4}-\d{1,2}-\d{1,2})(?:\/(?<select>officium-parvum-bmv|officium-defunctorum))?\/(?<occasion>[a-z-]+)/).groups;
            let params = new URLSearchParams(window.location.search);
            let votivestr = params.get('v');
            // For whatever reason, + is replaced with space
            let votives = votivestr ? votivestr.replaceAll(' ', '+').split('+') : [];
            let optMatch = document.cookie.match(/(?:^|;\s*)opt=([^;]*)/);
            let opt = optMatch ? decodeURIComponent(optMatch[1]).split('+').filter(t => t) : [];
            return {'locale': pathVariables.locale, 'prayerType': pathVariables.prayerType, 'date': Temporal.PlainDate.from(pathVariables.date), 'select': pathVariables.select || 'primarium', 'occasion': pathVariables.occasion, 'votives': votives, 'opt': opt};
          },
          makeURL({locale=this.contentParameters().locale, prayerType=this.contentParameters().prayerType, date=this.contentParameters().date, select=this.contentParameters().select, occasion=this.contentParameters().occasion, votives=this.contentParameters().votives} = {}) {
            return `/${locale}/${prayerType}/${date}${select == 'primarium' ? '' : '/' + select}/${occasion}${votives.length == 0 ? '' : '?v=' + votives.join('+')}`;
          },
          // The normal seven-hour cursus spans every "desired" ambit (omnes/diei/
          // officium-parvum-bmv/semper-cum-opbmv) - only Officium Defunctorum and the
          // standalone Rites fall outside it.
          isCursus(params = this.contentParameters()) {
            return params.prayerType == 'officium' && params.select != 'officium-defunctorum'
              && this.CURSUS_OCCASIONS.includes(params.occasion);
          },
          recordCursusPosition() {
            let current = this.contentParameters();
            if (this.isCursus(current)) {
              let lastCursusHour = {
                date: current.date.toString(), select: current.select,
                occasion: current.occasion, votives: current.votives
              };
              localStorage.setItem('lastCursusHour', JSON.stringify(lastCursusHour));
            }
          },
          nextHour(current) {
            let idx = this.CURSUS_OCCASIONS.indexOf(current.occasion);
            let wrapping = idx == this.CURSUS_OCCASIONS.length - 1;
            return {
              date: wrapping ? current.date.add({days: 1}) : current.date,
              occasion: wrapping ? this.CURSUS_OCCASIONS[0] : this.CURSUS_OCCASIONS[idx + 1],
              select: current.select,
              votives: current.votives
            };
          },
          canIncrementHour(current) {
            let target = this.nextHour(current);
            let today = Temporal.Now.plainDateISO();
            if (target.occasion == 'matutinum-laudes' && Temporal.PlainDate.compare(target.date, today.add({days: 1})) == 0) {
              return Temporal.Now.plainTimeISO().hour >= 14;
            }
            return Temporal.PlainDate.compare(target.date, today) == 0;
          },
          async toggleVotive(tag) {
            let current = this.contentParameters();
            let votives = current.votives.includes(tag) ? current.votives.filter(v => v != tag) : [...current.votives, tag];
            await this.navigateRite(this.makeURL({votives: votives}));
          },
          async setOpt(tags) {
            let opt = tags.filter(t => t).join('+');
            if (opt) {
              await cookieStore.set({name: 'opt', value: opt, path: '/'});
            } else {
              await cookieStore.delete({name: 'opt', path: '/'});
            }
          },
          async setDesired(select, optTag) {
            let current = this.contentParameters();
            let tags = current.opt.filter(t => t == 'privata');
            if (optTag) tags.push(optTag);
            await this.setOpt(tags);
            if (current.select != select) {
              await this.navigateRite(this.makeURL({select: select}));
            } else {
              await this.loadRite(this.displayPath);
            }
          },
          async togglePriest() {
            let current = this.contentParameters();
            let tags = current.opt.includes('privata') ? current.opt.filter(t => t != 'privata') : [...current.opt, 'privata'];
            await this.setOpt(tags);
            await this.loadRite(this.displayPath);
          },
          async fetchRite(path) {
            let contentParams = this.contentParameters(path=path);
            return fetch(`/api/rite?loc=${contentParams.locale}&date=${contentParams.date}&s=${contentParams.select}&occasion=${contentParams.occasion}+${contentParams.prayerType}&v=${contentParams.votives.join('+')}`).then(resp => resp.text());
          },
          async loadRite(path) {
            this.rite = await this.fetchRite(path);
            // day_title, straight from the same <h1 class="large-title"> the page displays -
            // no separate /api/ordo round-trip needed. Strip the single trailing period
            // rite_title() (renderer/rendering_utils.py) always appends.
            let match = this.rite.match(/<h1 class="large-title">(.*?)<\/h1>/);
            let dayTitle = match ? match[1].replace(/\.$/, '') : '';
            document.title = `${this.RITE_TITLES[this.contentParameters(path).occasion]} | ${dayTitle} | Liber Usualis`;
            window.scrollTo(0, 0);
          },
          async navigateRite(path, navigationType='soft', action='push') {
            this.displayPath = path;
            if (action == 'push') {
              history.pushState({navigationType: navigationType}, '', path);
            } else {
              history.replaceState({navigationType: navigationType}, '', path);
            }
            await this.loadRite(path);
          },
          async redirect() {
            let locale = window.location.pathname.match(/^\/([a-z]{2})\//)?.[1] || 'en';
            // We're checking if we actually have a last completed hour recorded - since the function lastCompletedHour() returns a default value rather than null.
            if (!localStorage.getItem('lastCursusHour') || !this.canIncrementHour(this.lastCompletedHour())) {
              await this.navigateRite(this.makeURL({
                locale: locale,
                prayerType: 'officium',
                date: Temporal.Now.plainDateISO().toString(),
                select: 'primarium',
                occasion: this.suggestOccasion(),
                votives: []
              }), navigationType='soft', action='replace');
            } else {
              await this.navigateRite(this.makeURL({...this.nextHour(this.lastCompletedHour()), locale: locale, prayerType: 'officium'}), navigationType='soft', action='replace');
            }
          },
          init() {
            const [navEntry] = performance.getEntriesByType('navigation');
            // Note: If no navigationType is available, this condition will be false, so redirection will not occur.
            if (!this.isRitePath(window.location.pathname) || (navEntry?.type === 'reload' && history.state?.navigationType === 'soft')) {
              this.redirect();
            }
          }
        });
        // navigationType (default: soft) is accessed to determine if the user wants the app to automatically switch to a more relevant rite or not on reload / page load.
        Alpine.directive('rite-link', (el, {value}) => {
          let navigationType = value || 'soft';
          el.addEventListener('click', (e) => {
          e.preventDefault();
          Alpine.store('router').navigateRite(new URL(el.href).pathname, navigationType);
          });
        });
      });
      window.addEventListener('popstate', () => {
        let router = Alpine.store('router');
        if (router.isRitePath(location.pathname)) {
          router.displayPath = location.pathname;
          router.navigateRite(location.pathname);
        } else {
          router.redirect();
        }
      });
    </script>
  </body>
</html>
