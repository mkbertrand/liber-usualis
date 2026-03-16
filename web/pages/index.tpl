<div id="side-panel-left">
</div>
<div id="home-screen">
	<h1 id="main-title-label">Liber Usualis Project</h1>
	<nav id="center-nav" x-data="{
		pages:[
			{'path':'/{{locale}}/pray', 'name':'{{text['pray']}}'},
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
