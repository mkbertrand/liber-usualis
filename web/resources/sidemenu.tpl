<nav id="sidebar-nav" x-show="sidebarnavopen" x-transition x-data="{
	pages:[
		{'path':'/{{locale}}/index', 'name':'{{text['index']}}'},
		{'path':'/{{locale}}/pray', 'name':'{{text['pray']}}'},
		{'path':'/{{locale}}/about', 'name':'{{text['about']}}'},
		{'path':'/{{locale}}/help', 'name':'{{text['help']}}'},
		{'path':'/{{locale}}/donate', 'name':'{{text['donate']}}'},
		{'path':'/{{locale}}/credit', 'name':'{{text['credit']}}'},
	]
	}">
	<template x-for="page in pages">
		<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
	</template>

</nav>
