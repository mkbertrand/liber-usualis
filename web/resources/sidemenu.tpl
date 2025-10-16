<nav id="sidebar-nav" x-show="sidebarnavopen" x-transition x-data="{
	pages:[
		{'path':'/{{preferredlocale}}/index', 'name':'{{text['index']}}'},
		{'path':'/{{preferredlocale}}/pray', 'name':'{{text['pray']}}'},
		{'path':'/{{preferredlocale}}/about', 'name':'{{text['about']}}'},
		{'path':'/{{preferredlocale}}/help', 'name':'{{text['help']}}'},
		{'path':'/{{preferredlocale}}/donate', 'name':'{{text['donate']}}'},
		{'path':'/{{preferredlocale}}/credit', 'name':'{{text['credit']}}'},
	]
	}">
	<template x-for="page in pages">
		<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
	</template>

</nav>
