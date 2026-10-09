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
              <span>{{text['more-rites-button']}} <svg class="icon small-icon inline-icon" width="16" height="16" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M212.24,100.24l-80,80a6,6,0,0,1-8.48,0l-80-80a6,6,0,0,1,8.48-8.48L128,167.51l75.76-75.75a6,6,0,0,1,8.48,8.48Z"/></svg></span>
            </button>
          </div>
        </div>
        <div id="second-bar-right-aligned-container" class="second-bar-container">
          <div class="top-bar-button-container">
            <button id="ordo-panel-toggle-button" class="ui-button ui-button-secondary">
              {{text['ordo-button']}}
            </button>
          </div>
          <div class="top-bar-button-container">
            <button id="options-gear-button" class="ui-button icon-button ui-button-secondary" aria-label="{{text['options-panel-button']}}">
              <svg class="icon options-gear-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M128,82a46,46,0,1,0,46,46A46.06,46.06,0,0,0,128,82Zm0,80a34,34,0,1,1,34-34A34,34,0,0,1,128,162ZM214,130.84c.06-1.89.06-3.79,0-5.68L229.33,106a6,6,0,0,0,1.11-5.29A105.34,105.34,0,0,0,219.76,74.9a6,6,0,0,0-4.53-3l-24.45-2.71q-1.93-2.07-4-4l-2.72-24.46a6,6,0,0,0-3-4.53,105.65,105.65,0,0,0-25.77-10.66A6,6,0,0,0,150,26.68l-19.2,15.37c-1.89-.06-3.79-.06-5.68,0L106,26.67a6,6,0,0,0-5.29-1.11A105.34,105.34,0,0,0,74.9,36.24a6,6,0,0,0-3,4.53L69.23,65.22q-2.07,1.94-4,4L40.76,72a6,6,0,0,0-4.53,3,105.65,105.65,0,0,0-10.66,25.77A6,6,0,0,0,26.68,106l15.37,19.2c-.06,1.89-.06,3.79,0,5.68L26.67,150.05a6,6,0,0,0-1.11,5.29A105.34,105.34,0,0,0,36.24,181.1a6,6,0,0,0,4.53,3l24.45,2.71q1.94,2.07,4,4L72,215.24a6,6,0,0,0,3,4.53,105.65,105.65,0,0,0,25.77,10.66,6,6,0,0,0,5.29-1.11L125.16,214c1.89.06,3.79.06,5.68,0l19.21,15.38a6,6,0,0,0,3.75,1.31,6.2,6.2,0,0,0,1.54-.2,105.34,105.34,0,0,0,25.76-10.68,6,6,0,0,0,3-4.53l2.71-24.45q2.07-1.93,4-4l24.46-2.72a6,6,0,0,0,4.53-3,105.49,105.49,0,0,0,10.66-25.77,6,6,0,0,0-1.11-5.29Zm-3.1,41.63-23.64,2.63a6,6,0,0,0-3.82,2,75.14,75.14,0,0,1-6.31,6.31,6,6,0,0,0-2,3.82l-2.63,23.63A94.28,94.28,0,0,1,155.14,218l-18.57-14.86a6,6,0,0,0-3.75-1.31h-.36a78.07,78.07,0,0,1-8.92,0,6,6,0,0,0-4.11,1.3L100.87,218a94.13,94.13,0,0,1-17.34-7.17L80.9,187.21a6,6,0,0,0-2-3.82,75.14,75.14,0,0,1-6.31-6.31,6,6,0,0,0-3.82-2l-23.63-2.63A94.28,94.28,0,0,1,38,155.14l14.86-18.57a6,6,0,0,0,1.3-4.11,78.07,78.07,0,0,1,0-8.92,6,6,0,0,0-1.3-4.11L38,100.87a94.13,94.13,0,0,1,7.17-17.34L68.79,80.9a6,6,0,0,0,3.82-2,75.14,75.14,0,0,1,6.31-6.31,6,6,0,0,0,2-3.82l2.63-23.63A94.28,94.28,0,0,1,100.86,38l18.57,14.86a6,6,0,0,0,4.11,1.3,78.07,78.07,0,0,1,8.92,0,6,6,0,0,0,4.11-1.3L155.13,38a94.13,94.13,0,0,1,17.34,7.17l2.63,23.64a6,6,0,0,0,2,3.82,75.14,75.14,0,0,1,6.31,6.31,6,6,0,0,0,3.82,2l23.63,2.63A94.28,94.28,0,0,1,218,100.86l-14.86,18.57a6,6,0,0,0-1.3,4.11,78.07,78.07,0,0,1,0,8.92,6,6,0,0,0,1.3,4.11L218,155.13A94.13,94.13,0,0,1,210.85,172.47Z"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div id="system-banner-container">
      <template id="system-banner">
        <div class="system-banner">
          <p class="system-banner-content"></p>
          <div class="system-banner-answer-container">
          </div>
        </div>
      </template>
      <template id="system-banner-answer">
        <button class="system-banner-answer ui-button ui-button-secondary"></button>
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
            <svg id="next-hour-button-icon" class="icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M180.24,132.24l-80,80a6,6,0,0,1-8.48-8.48L167.51,128,91.76,52.24a6,6,0,0,1,8.48-8.48l80,80A6,6,0,0,1,180.24,132.24Z"/></svg>
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
            <button id="ordo-date-previous" type="button" aria-label="{{text['ordo-previous-day']}}"><svg class="icon small-icon" width="16" height="16" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M164.24,203.76a6,6,0,1,1-8.48,8.48l-80-80a6,6,0,0,1,0-8.48l80-80a6,6,0,0,1,8.48,8.48L88.49,128Z"/></svg></button>
            <input id="ordo-date-picker" type="date" value="{{date}}" aria-label="{{text['ordo-date']}}">
            <button id="ordo-date-next" type="button" aria-label="{{text['ordo-next-day']}}"><svg class="icon small-icon" width="16" height="16" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M180.24,132.24l-80,80a6,6,0,0,1-8.48-8.48L167.51,128,91.76,52.24a6,6,0,0,1,8.48-8.48l80,80A6,6,0,0,1,180.24,132.24Z"/></svg></button>
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
