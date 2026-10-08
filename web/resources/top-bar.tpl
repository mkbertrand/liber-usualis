% # Icons from Phosphor Icons (https://phosphoricons.com), MIT License
<div id="top-bar-title">
  <div id="top-bar-left-aligned-container">
    <div id="project-logo">
      <div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.webp" alt="LIBER USUALIS"></a></div>
    </div>
    <a id="pray-navigation-link" href="/{{locale}}/pray">{{text['pray']}}</a>
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
    <a class="navigation-link" href="/{{locale}}/donate">{{text['donate']}}</a>
    <div class="top-bar-button-container">
      % include('web/resources/locale-selector.tpl', locale=locale)
    </div>
    <div class="top-bar-button-container">
      <button id="dark-mode-toggle" class="ui-button" type="button">
        <svg class="icon dark-mode-toggle-moon-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M233.54,142.23a8,8,0,0,0-8-2,88.08,88.08,0,0,1-109.8-109.8,8,8,0,0,0-10-10,104.84,104.84,0,0,0-52.91,37A104,104,0,0,0,136,224a103.09,103.09,0,0,0,62.52-20.88,104.84,104.84,0,0,0,37-52.91A8,8,0,0,0,233.54,142.23ZM188.9,190.34A88,88,0,0,1,65.66,67.11a89,89,0,0,1,31.4-26A106,106,0,0,0,96,56,104.11,104.11,0,0,0,200,160a106,106,0,0,0,14.92-1.06A89,89,0,0,1,188.9,190.34Z"/></svg>
        <svg class="icon dark-mode-toggle-sun-icon" width="24" height="24" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M120,40V16a8,8,0,0,1,16,0V40a8,8,0,0,1-16,0Zm72,88a64,64,0,1,1-64-64A64.07,64.07,0,0,1,192,128Zm-16,0a48,48,0,1,0-48,48A48.05,48.05,0,0,0,176,128ZM58.34,69.66A8,8,0,0,0,69.66,58.34l-16-16A8,8,0,0,0,42.34,53.66Zm0,116.68-16,16a8,8,0,0,0,11.32,11.32l16-16a8,8,0,0,0-11.32-11.32ZM192,72a8,8,0,0,0,5.66-2.34l16-16a8,8,0,0,0-11.32-11.32l-16,16A8,8,0,0,0,192,72Zm5.66,114.34a8,8,0,0,0-11.32,11.32l16,16a8,8,0,0,0,11.32-11.32ZM48,128a8,8,0,0,0-8-8H16a8,8,0,0,0,0,16H40A8,8,0,0,0,48,128Zm80,80a8,8,0,0,0-8,8v24a8,8,0,0,0,16,0V216A8,8,0,0,0,128,208Zm112-88H216a8,8,0,0,0,0,16h24a8,8,0,0,0,0-16Z"/></svg>
      </button>
    </div>
  </div>
</div>
