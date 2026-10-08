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
    % # Icons from Phosphor Icons (https://phosphoricons.com), MIT License
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
            <button id="ordo-panel-toggle-button" class="ui-button">
              {{text['ordo-button']}}
            </button>
          </div>
          <div class="top-bar-button-container">
            <button id="options-gear-button" class="ui-button" aria-label="{{text['options-panel-button']}}">
              <svg class="icon options-gear-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M128,80a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Zm0,80a32,32,0,1,1,32-32A32,32,0,0,1,128,160Zm88-29.84q.06-2.16,0-4.32l14.92-18.64a8,8,0,0,0,1.48-7.06,107.21,107.21,0,0,0-10.88-26.25,8,8,0,0,0-6-3.93l-23.72-2.64q-1.48-1.56-3-3L186,40.54a8,8,0,0,0-3.94-6,107.71,107.71,0,0,0-26.25-10.87,8,8,0,0,0-7.06,1.49L130.16,40Q128,40,125.84,40L107.2,25.11a8,8,0,0,0-7.06-1.48A107.6,107.6,0,0,0,73.89,34.51a8,8,0,0,0-3.93,6L67.32,64.27q-1.56,1.49-3,3L40.54,70a8,8,0,0,0-6,3.94,107.71,107.71,0,0,0-10.87,26.25,8,8,0,0,0,1.49,7.06L40,125.84Q40,128,40,130.16L25.11,148.8a8,8,0,0,0-1.48,7.06,107.21,107.21,0,0,0,10.88,26.25,8,8,0,0,0,6,3.93l23.72,2.64q1.49,1.56,3,3L70,215.46a8,8,0,0,0,3.94,6,107.71,107.71,0,0,0,26.25,10.87,8,8,0,0,0,7.06-1.49L125.84,216q2.16.06,4.32,0l18.64,14.92a8,8,0,0,0,7.06,1.48,107.21,107.21,0,0,0,26.25-10.88,8,8,0,0,0,3.93-6l2.64-23.72q1.56-1.48,3-3L215.46,186a8,8,0,0,0,6-3.94,107.71,107.71,0,0,0,10.87-26.25,8,8,0,0,0-1.49-7.06Zm-16.1-6.5a73.93,73.93,0,0,1,0,8.68,8,8,0,0,0,1.74,5.48l14.19,17.73a91.57,91.57,0,0,1-6.23,15L187,173.11a8,8,0,0,0-5.1,2.64,74.11,74.11,0,0,1-6.14,6.14,8,8,0,0,0-2.64,5.1l-2.51,22.58a91.32,91.32,0,0,1-15,6.23l-17.74-14.19a8,8,0,0,0-5-1.75h-.48a73.93,73.93,0,0,1-8.68,0,8,8,0,0,0-5.48,1.74L100.45,215.8a91.57,91.57,0,0,1-15-6.23L82.89,187a8,8,0,0,0-2.64-5.1,74.11,74.11,0,0,1-6.14-6.14,8,8,0,0,0-5.1-2.64L46.43,170.6a91.32,91.32,0,0,1-6.23-15l14.19-17.74a8,8,0,0,0,1.74-5.48,73.93,73.93,0,0,1,0-8.68,8,8,0,0,0-1.74-5.48L40.2,100.45a91.57,91.57,0,0,1,6.23-15L69,82.89a8,8,0,0,0,5.1-2.64,74.11,74.11,0,0,1,6.14-6.14A8,8,0,0,0,82.89,69L85.4,46.43a91.32,91.32,0,0,1,15-6.23l17.74,14.19a8,8,0,0,0,5.48,1.74,73.93,73.93,0,0,1,8.68,0,8,8,0,0,0,5.48-1.74L155.55,40.2a91.57,91.57,0,0,1,15,6.23L173.11,69a8,8,0,0,0,2.64,5.1,74.11,74.11,0,0,1,6.14,6.14,8,8,0,0,0,5.1,2.64l22.58,2.51a91.32,91.32,0,0,1,6.23,15l-14.19,17.74A8,8,0,0,0,199.87,123.66Z"/></svg>
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
            <button id="ordo-date-previous" type="button" aria-label="{{text['ordo-previous-day']}}"><svg class="icon ordo-date-icon" width="16" height="16" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M165.66,202.34a8,8,0,0,1-11.32,11.32l-80-80a8,8,0,0,1,0-11.32l80-80a8,8,0,0,1,11.32,11.32L91.31,128Z"/></svg></button>
            <input id="ordo-date-picker" type="date" value="{{date}}" aria-label="{{text['ordo-date']}}">
            <button id="ordo-date-next" type="button" aria-label="{{text['ordo-next-day']}}"><svg class="icon ordo-date-icon" width="16" height="16" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M181.66,133.66l-80,80a8,8,0,0,1-11.32-11.32L164.69,128,90.34,53.66a8,8,0,0,1,11.32-11.32l80,80A8,8,0,0,1,181.66,133.66Z"/></svg></button>
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
