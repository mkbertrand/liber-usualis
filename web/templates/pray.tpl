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

<html lang="{{locale.split('-')[0]}}">
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
    <script src='https://cdn.jsdelivr.net/npm/temporal-polyfill@0.3.0/global.min.js'></script>
		<script defer type="text/javascript" src={{version_management.get_versioned_resource('/dist/pray.js')}}></script>
	</head>
  <body>
    % include('web/resources/top-bar.tpl', locale=locale, options=True, text=json.load(open(f'web/locales/{locale}/resources/top-bar.json')))
    <div id="second-bar-container">
      <div id="second-bar">
        <div id="second-bar-left-aligned-container" class="second-bar-container">
          % # Shown by the page's script while the user is pinned (hard navigation) to a rite other than the current one
          <button id="return-to-current-button" class="navigation-link" type="button" data-title-template="{{text['return-to-current-tooltip']}}" style="display: none">{{text['return-to-current-button']}}</button>
        </div>
        <div id="second-bar-center-aligned-container" class="second-bar-container">
          % hour_select = '/officium-parvum-bmv' if select == 'officium-parvum-bmv' else ''
          % hour_votives = '' if len(votives) == 0 else f'?v={votives}'
          % for hour in [['matutinum-laudes', 'Matutinum &amp; Laudes'], ['prima', 'Prima'], ['tertia', 'Tertia'], ['sexta', 'Sexta'], ['nona', 'Nona'], ['vesperae', 'Vesperæ'], ['completorium', 'Completorium']]:
          <a class="navigation-link second-bar-hour-link" href="/{{locale}}/officium/{{pdate}}{{hour_select}}/{{hour[0]}}{{hour_votives}}" data-rite-link data-occasion="{{hour[0]}}">{{!hour[1]}}</a>
          % end
          % # Shown by the page's script once the next day's Matins may be said, which depends on the reader's local time
          <a id="second-bar-next-matins-link" class="navigation-link" href="/{{locale}}/officium/{{pdate + timedelta(days=1)}}{{hour_select}}/matutinum-laudes{{hour_votives}}" title="{{pdate + timedelta(days=1)}}" data-rite-link style="display: none">Matutinum &amp; Laudes (anticipata)</a>
          <div class="top-bar-button-container">
            <button id="rites-menu-toggle-button" class="navigation-link">
              {{text['more-rites-button']}}
            </button>
          </div>
        </div>
        <div id="second-bar-right-aligned-container" class="second-bar-container">
          <div class="top-bar-button-container">
            <button id="ordo-panel-toggle-button" class="navigation-link">
              {{text['ordo-button']}}
            </button>
          </div>
          <div class="top-bar-button-container">
            <button id="options-gear-button" class="ui-button" aria-label="{{text['options-panel-button']}}">
              <svg id="options-gear" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%"><path d="M262.29 192.31a64 64 0 1057.4 57.4 64.13 64.13 0 00-57.4-57.4zM416.39 256a154.34 154.34 0 01-1.53 20.79l45.21 35.46a10.81 10.81 0 012.45 13.75l-42.77 74a10.81 10.81 0 01-13.14 4.59l-44.9-18.08a16.11 16.11 0 00-15.17 1.75A164.48 164.48 0 01325 400.8a15.94 15.94 0 00-8.82 12.14l-6.73 47.89a11.08 11.08 0 01-10.68 9.17h-85.54a11.11 11.11 0 01-10.69-8.87l-6.72-47.82a16.07 16.07 0 00-9-12.22 155.3 155.3 0 01-21.46-12.57 16 16 0 00-15.11-1.71l-44.89 18.07a10.81 10.81 0 01-13.14-4.58l-42.77-74a10.8 10.8 0 012.45-13.75l38.21-30a16.05 16.05 0 006-14.08c-.36-4.17-.58-8.33-.58-12.5s.21-8.27.58-12.35a16 16 0 00-6.07-13.94l-38.19-30A10.81 10.81 0 0149.48 186l42.77-74a10.81 10.81 0 0113.14-4.59l44.9 18.08a16.11 16.11 0 0015.17-1.75A164.48 164.48 0 01187 111.2a15.94 15.94 0 008.82-12.14l6.73-47.89A11.08 11.08 0 01213.23 42h85.54a11.11 11.11 0 0110.69 8.87l6.72 47.82a16.07 16.07 0 009 12.22 155.3 155.3 0 0121.46 12.57 16 16 0 0015.11 1.71l44.89-18.07a10.81 10.81 0 0113.14 4.58l42.77 74a10.8 10.8 0 01-2.45 13.75l-38.21 30a16.05 16.05 0 00-6.05 14.08c.33 4.14.55 8.3.55 12.47z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div id="system-banner-container">
      <template id="system-banner">
        <div class="system-banner">
          <div class="system-banner-content-container">
            <p class="system-banner-content"></p>
            <div class="system-banner-answer-container">
            </div>
          </div>
          <button class="system-banner-close ui-button">{{text['banner-dismiss']}}</button>
        </div>
      </template>
      <template id="system-banner-answer">
        <button class="system-banner-answer ui-button"></button>
      </template>
    </div>
    % # Localized text for messages the page's script builds itself. "</" is escaped so no string can end this block early.
    % script_text_keys = ['banner-remain-here', 'suboptimal-content-banner-message', 'suboptimal-content-banner-go', 'outdated-content-banner-message', 'outdated-content-banner-go']
    <script type="application/json" id="pray-script-text">{{!json.dumps({key: text[key] for key in script_text_keys}, ensure_ascii=False).replace('</', '<\\/')}}</script>
    % include('web/resources/pray/rites-menu.tpl', locale=locale, date=date, text=text)
    <div id="content-container-outer">
      <div id="rite-page-container">
        % # Latin pages have no translation (and hide its options), whatever display preferences were saved elsewhere
        <main id="rite-container" data-has-translation="{{'false' if locale == 'la' else 'true'}}">
          {{!rite}}
        </main>
        <div id="next-hour-button-container">
          <a
            id="next-hour-button"
            href="{{next_hour_href}}"
            data-forbidden-title="{{text['next-hour-forbidden-tooltip']}}"
          >
            <span>{{text['next-hour']}}: <span id="next-hour-occasion">{{!next_hour_occasion_name}}</span></span>
            <svg id="next-hour-button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="currentColor" transform="scale(3)"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L12.793 8l-2.647-2.646a.5.5 0 0 1 0-.708"></path><path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5H13a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 8"></path></g></svg>
          </a>
        </div>
      </div>
    </div>
    % # On mobile the panels are full-screen sheets (see pray-mobile.css), so they neither trap focus nor lock scrolling.
    <div id="options-panel-background" style="display: none">
      <div id="options-panel-wrapper"{{!'' if mobile else ' data-trap-focus'}}>
        % include('web/resources/pray/options-panel.tpl', locale=locale, text=text, date=date)
      </div>
    </div>
    <div id="ordo-panel-background" style="display: none">
      <div id="ordo-panel-wrapper"{{!'' if mobile else ' data-trap-focus'}}>
        <div id="ordo-panel">
          <h2>{{text['ordo-panel-title']}}</h2>
          <div id="ordo-date-controls">
            <button id="ordo-date-previous" type="button" aria-label="{{text['ordo-previous-day']}}">‹</button>
            <input id="ordo-date-picker" type="date" value="{{date}}" aria-label="{{text['ordo-date']}}">
            <button id="ordo-date-next" type="button" aria-label="{{text['ordo-next-day']}}">›</button>
          </div>
          <h3>{{text['ordo-daytime-title']}}</h3>
          <p><span id="ordo-daytime-primarium"></span> &mdash; <span id="ordo-daytime-primarium-rank"></span></p>
          <div id="ordo-daytime-details"></div>
          <h3>{{text['ordo-evening-title']}}</h3>
          <p><span id="ordo-evening-primarium"></span> &mdash; <span id="ordo-evening-primarium-rank"></span></p>
          <div id="ordo-evening-details"></div>
          % # Paragraphs the page's script adds to a day's details only when they apply
          <template id="ordo-psalmi-template">
            <p class="ordo-section"><span class="ordo-section-label">{{text['ordo-psalmi-label']}}</span> <span class="ordo-section-names"></span></p>
          </template>
          <template id="ordo-commemorations-template">
            <p class="ordo-section"><span class="ordo-section-label">{{text['ordo-commemorations-label']}}</span><br><span class="ordo-section-names"></span></p>
          </template>
          <template id="ordo-omissions-template">
            <p class="ordo-section"><span class="ordo-section-label">{{text['ordo-omissions-label']}}</span><br><span class="ordo-section-names"></span></p>
          </template>
          <h3>{{text['ordo-rites-title']}}</h3>
          <div id="ordo-rite-links">
            % for item in [['matutinum-laudes', 'Matutinum &amp; Laudes'], ['prima', 'Prima'], ['tertia', 'Tertia'], ['sexta', 'Sexta'], ['nona', 'Nona'], ['vesperae', 'Vesperæ'], ['completorium', 'Completorium']]:
            % # Choosing a rite from the ordo is a deliberate choice of day, so it pins the page (hard navigation)
            <a class="ordo-rite-link" href="/{{locale}}/officium/{{pdate}}{{'/officium-parvum-bmv' if select == 'officium-parvum-bmv' else ''}}/{{item[0]}}{{'' if len(votives) == 0 else f'?v={votives}'}}" data-rite-link="hard" data-occasion="{{item[0]}}">{{!item[1]}}</a>
            % end
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
