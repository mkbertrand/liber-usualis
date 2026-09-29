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
      % include('web/resources/dark-mode-toggle.tpl')
    </div>
  </div>
</div>
