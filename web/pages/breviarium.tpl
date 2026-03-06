<div id="side-panel-left">
</div>
<div id="home-screen">
<h1 id="breviarium-title">Breviarium Romanum</h1>
<h3 class="breviarium-subtitle">Ex Decreto Sacrosancti Concilii Tridentini</h3>
<h4 class="breviarium-subtitle-2">Restitutum</h4>
<h3 class="breviarium-subtitle">S. Pii V. Pontificis Maximi</h3>
<h4 class="breviarium-subtitle-2">Jussu Editum</h4>
<h3 class="breviarium-subtitle">Clementis VIII., Urbani VIII. et Leonis XIII.</h3>
<h4 class="breviarium-subtitle-2">Auctoritate Recognitum.</h4>
<hr style="width:100%">
<p>Hi! You're on an incomplete part of the website. This navigation page is only somewhat usable. Don't worry; using this page will not break anything.</p>
<nav id="breviarium-contents-nav" x-data="{
	pages:[
		{'path':'/{{locale}}/de-anno', 'name':'{{text['de-anno']}}'},
		{'path':'/{{locale}}/kalendar', 'name':'{{text['kalendar']}}'},
		{'path':'/{{locale}}/rubricae', 'name':'{{text['rubrics']}}'},
		{'path':'/{{locale}}/pray', 'name':'{{text['pray']}}'}
	]
	}">
	<template x-for="page in pages">
		<p><a class="nav-element" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a></p>
	</template>
</nav>
</div>
<div id="side-panel-right">
</div>
