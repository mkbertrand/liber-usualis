<div id="side-panel-left">
</div>
<div id="home-screen">
  <h1 id="main-title-label">The Liber Usualis Project</h1>
  <p id="presents-small-text">{{text['presents']}}</p>
  <h1 id="breviarium-title">Breviarium Romanum</h1>
  % if mobile:
    <hr style="width:100%">
    <div id="breviarium-pray-container-mobile">
      <a href="/{{locale}}/pray" class="breviarium-link breviarium-link-mobile" id="pray-button-container">{{text['pray']}}</a>
    </div>
    <div id="breviarium-other-container-mobile">
      <a href="/{{locale}}/de-anno" class="breviarium-link breviarium-link-mobile">{{text['de-anno']}}</a>
      <a href="/{{locale}}/rubricae" class="breviarium-link breviarium-link-mobile">{{text['rubricae']}}</a>
      <a href="/{{locale}}/kalendar" class="breviarium-link breviarium-link-mobile">{{text['kalendarium']}}</a>
      <a href="/{{locale}}/ordo" class="breviarium-link breviarium-link-mobile">{{text['ordo']}}</a>
    </div>
  % else:
    <h3 class="breviarium-subtitle">Ex Decreto Sacrosancti Concilii Tridentini</h3>
    <h4 class="breviarium-subtitle-2">Restitutum</h4>
    <h3 class="breviarium-subtitle">S. Pii V. Pontificis Maximi</h3>
    <h4 class="breviarium-subtitle-2">Jussu Editum</h4>
    <h3 class="breviarium-subtitle">Clementis VIII., Urbani VIII. et Leonis XIII.</h3>
    <h4 class="breviarium-subtitle-2">Auctoritate Recognitum.</h4>
    <hr style="width:100%">
    <div id="breviarium-select-container">
      <div id="breviarium-select-left-container">
        <a href="/{{locale}}/de-anno" class="breviarium-link">{{text['de-anno']}}</a>
        <a href="/{{locale}}/rubricae" class="breviarium-link">{{text['rubricae']}}</a>
      </div>
      <div id="breviarium-select-center-container">
        <a href="/{{locale}}/pray" class="breviarium-link" id="pray-button-container">{{text['pray']}}</a>
      </div>
      <div id="breviarium-select-right-container">
        <a href="/{{locale}}/kalendar" class="breviarium-link">{{text['kalendarium']}}</a>
        <a href="/{{locale}}/ordo" class="breviarium-link">{{text['ordo']}}</a>
      </div>
    </div>
  % end
  <hr style="width:100%">
	<nav id="center-nav" x-data="{
		pages:[
			{'path':'/{{locale}}/about', 'name':'{{text['about']}}'},
			{'path':'/{{locale}}/help', 'name':'{{text['help']}}'},
			{'path':'/{{locale}}/credit', 'name':'{{text['credit']}}'},
			{'path':'/{{locale}}/donate', 'name':'{{text['donate']}}'},
		]
		}">
		<template x-for="page in pages">
			<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
		</template>
	</nav>
</div>
<div id="side-panel-right">
</div>
