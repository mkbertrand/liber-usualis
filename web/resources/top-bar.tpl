% # Icons from Phosphor Icons (https://phosphoricons.com), MIT License
<div id="top-bar-title">
  <div id="top-bar-left-aligned-container">
    <div id="project-logo">
      <div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.webp" alt="LIBER USUALIS"></a></div>
    </div>
    <a id="pray-navigation-link" class="ui-button ui-button-primary" href="/{{locale}}/pray"{{!' aria-current="page"' if page == 'pray' else ''}}>{{text['pray']}}</a>
    <a class="navigation-link" href="/{{locale}}/de-anno">{{text['de-anno']}}</a>
    <a class="navigation-link" href="/{{locale}}/rubricae">{{text['rubricae']}}</a>
    <a class="navigation-link" href="/{{locale}}/kalendar">{{text['kalendar']}}</a>
    <a class="navigation-link" href="/{{locale}}/ordo">{{text['ordo']}}</a>
    <a class="navigation-link" href="/{{locale}}/about">{{text['about']}}</a>
    <a class="navigation-link" href="/{{locale}}/resources">{{text['resources']}}</a>
    <a class="navigation-link" href="/{{locale}}/help">{{text['help']}}</a>
    <a class="navigation-link" href="/{{locale}}/credit">{{text['credit']}}</a>
  </div>
  <div id="top-bar-right-aligned-container">
    <div class="top-bar-button-container">
      <a id="donate-button" class="ui-button ui-button-primary" href="/{{locale}}/donate">{{text['donate']}}</a>
    </div>
    <div class="top-bar-button-container">
      % include('web/resources/locale-selector.tpl', locale=locale)
    </div>
    <div class="top-bar-button-container">
      <button id="dark-mode-toggle" class="ui-button icon-button ui-button-secondary" type="button">
        <svg class="icon dark-mode-toggle-moon-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M232.13,143.64a6,6,0,0,0-6-1.49A90.07,90.07,0,0,1,113.86,29.85a6,6,0,0,0-7.49-7.48A102.88,102.88,0,0,0,54.48,58.68,102,102,0,0,0,197.32,201.52a102.88,102.88,0,0,0,36.31-51.89A6,6,0,0,0,232.13,143.64Zm-42,48.29a90,90,0,0,1-126-126A90.9,90.9,0,0,1,99.65,37.66,102.06,102.06,0,0,0,218.34,156.35,90.9,90.9,0,0,1,190.1,191.93Z"/></svg>
        <svg class="icon dark-mode-toggle-sun-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M122,40V16a6,6,0,0,1,12,0V40a6,6,0,0,1-12,0Zm68,88a62,62,0,1,1-62-62A62.07,62.07,0,0,1,190,128Zm-12,0a50,50,0,1,0-50,50A50.06,50.06,0,0,0,178,128ZM59.76,68.24a6,6,0,1,0,8.48-8.48l-16-16a6,6,0,0,0-8.48,8.48Zm0,119.52-16,16a6,6,0,1,0,8.48,8.48l16-16a6,6,0,1,0-8.48-8.48ZM192,70a6,6,0,0,0,4.24-1.76l16-16a6,6,0,0,0-8.48-8.48l-16,16A6,6,0,0,0,192,70Zm4.24,117.76a6,6,0,0,0-8.48,8.48l16,16a6,6,0,0,0,8.48-8.48ZM46,128a6,6,0,0,0-6-6H16a6,6,0,0,0,0,12H40A6,6,0,0,0,46,128Zm82,82a6,6,0,0,0-6,6v24a6,6,0,0,0,12,0V216A6,6,0,0,0,128,210Zm112-88H216a6,6,0,0,0,0,12h24a6,6,0,0,0,0-12Z"/></svg>
      </button>
    </div>
  </div>
</div>
