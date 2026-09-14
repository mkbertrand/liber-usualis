<!DOCTYPE html>

<!-- Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% import version_management
% locale = locales[0]
% text = json.load(open(version_management.bestlocalized(f'/pages/{page}.json', locales)))
% import datamanage
% rite = datamanage.rendered_rite_request(date, occasion + '+' + prayer_type, options, select, translation, votives)
% from datetime import datetime, timedelta
% pdate = datetime.strptime(date, '%Y-%m-%d').date()
% ordo = datamanage.ordo(date, 'vesperale' if occasion in {'vesperae', 'completorium', 'pro-coena'} else 'diurnale', votives)

<html lang="{{locale.split('-')[0]}}" x-data :data-theme="$store.theme.current">
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
    <main id="rite-container" x-html="displayParameters.sideBySide? $store.router.rite : Pray.lineByLine($store.router.rite)" :class="{
      'chant-shown': displayParameters.chant,
      'chant-hidden': !displayParameters.chant,
      'chant-playback': displayParameters.chant && displayParameters.playChant,
      'side-by-side': displayParameters.sideBySide,
      'line-by-line': !displayParameters.sideBySide,
      'no-translation': !displayParameters.showTranslation
    }">
      {{!rite}}
    </main>
    <template x-if="bottomPanelEnabled">
      <div id="bottom-easy-select-container">
        <button id="bottom-easy-select-hide" @click="bottomPanelOpen = !bottomPanelOpen"><svg id="bottom-easy-select-hide-icon" :class="!bottomPanelOpen && 'bottom-easy-select-hide-icon-closed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><path fill="currentColor" d="M38.998 15.98 24.003 30.597 9.007 15.98a1.434 1.434 0 0 0-2.004 0 1.365 1.365 0 0 0 0 1.95l15.952 15.554a1.5 1.5 0 0 0 2.095 0l15.952-15.551a1.365 1.365 0 0 0 0-1.956 1.434 1.434 0 0 0-2.004 0z"></path></svg></button>
        <div id="bottom-easy-select-content-container" x-show="bottomPanelOpen" x-transition>
          <div id="date-selector-container" x-data="{search: '{{date}}'}">
            <a id="date-selector-decrement" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate - timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link :href="$store.router.makeURL({date: $store.router.contentParameters().date.subtract({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M5.854 4.646a.5.5 0 0 1 0 .708L3.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0"></path><path fill-rule="evenodd" d="M2.5 8a.5.5 0 0 1 .5-.5h10.5a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"></path></g></svg></a>
            <input id="date-selector-text" type="date" x-model="search">
            <a id="date-selector-text-submit" class="date-selector-button" :href="$store.router.makeURL({date:search})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M3.17 6.706a5 5 0 0 1 7.103-3.16.5.5 0 1 0 .454-.892A6 6 0 1 0 13.455 5.5a.5.5 0 0 0-.91.417 5 5 0 1 1-9.375.789"></path><path fill-rule="evenodd" d="M8.147.146a.5.5 0 0 1 .707 0l2.5 2.5a.5.5 0 0 1 0 .708l-2.5 2.5a.5.5 0 1 1-.707-.708L10.293 3 8.147.854a.5.5 0 0 1 0-.708"></path></g></svg></a>
            <a id="date-selector-increment" class="date-selector-button" href="/{{locale}}/{{prayer_type}}/{{pdate + timedelta(days=1)}}{{'' if select == 'primarium' else f'/{select}'}}/{{occasion}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link :href="$store.router.makeURL({date: $store.router.contentParameters().date.add({days:1})})"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg></a>
          </div>
          <div id="rite-selector-container">
            % for item in [['matutinum-laudes', 'Matutinum &amp; Laudes'], ['prima', 'Prima'], ['tertia', 'Tertia'], ['sexta', 'Sexta'], ['nona', 'Nona'], ['vesperae', 'Vesperæ'], ['completorium', 'Completorium']]:
            <a class="rite-selector-button" :class="$store.router.contentParameters().prayerType == 'officium' && $store.router.contentParameters().select != 'officium-defunctorum' && $store.router.contentParameters().occasion == '{{item[0]}}' ? 'rite-selector-button-selected' : ''" href="/{{locale}}/officium/{{pdate}}{{'' if select == 'primarium' else f'/{select}'}}/{{item[0]}}{{'' if len(votives) == 0 else f'?v={votives}'}}" x-rite-link :href="$store.router.makeURL({prayerType: 'officium', select: $store.router.contentParameters().select == 'officium-defunctorum' ? 'primarium' : $store.router.contentParameters().select, occasion: '{{item[0]}}'})">{{!item[1]}}</a>
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
          contentParameters(path=this.displayPath) {
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
          },
          async navigateRite(path) {
            this.displayPath = path;
            history.pushState({}, '', path);
            await this.loadRite(path);
          }
        });
        Alpine.directive('rite-link', (el) => {
          el.addEventListener('click', (e) => {
          e.preventDefault();
          Alpine.store('router').navigateRite(new URL(el.href).pathname);
          });
        });
      });
      window.addEventListener('popstate', () => {
        Alpine.store('router').displayPath = location.pathname;
        Alpine.store('router').navigateRite(location.pathname);
      });
    </script>
  </body>
</html>
