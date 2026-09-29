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
      <button id="dark-mode-toggle" class="ui-button" type="button" @click="$store.theme.toggle()">
        <svg x-show="$store.theme.current == 'light'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100%" height="100%" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
        <svg x-show="$store.theme.current == 'dark'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100%" height="100%" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path></svg>
      </button>
    </div>
  </div>
</div>
