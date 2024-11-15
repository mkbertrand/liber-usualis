<!DOCTYPE html>
<html lang='en'>
	<head>
		<title>{{title}}</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei.png">
		<link rel="stylesheet" type="text/css" href="/resources/styles/{{page}}.css">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css">
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen"><img id="sidebar-nav-toggle" src="/resources/svg/burger-menu.svg" /></button>
				<div id="project-logo">
					<h1 id="website-temp-name">LIBER VSVALIS</h1>
				</div>
			</div>
			<nav id="sidebar-nav" x-show="sidebarnavopen" x-data="{
				pages:[
					{'path':'/', 'name':'Pray'},
					{'path':'/about/', 'name':'About'},
					{'path':'/help/', 'name':'Help'},
					{'path':'/credit/', 'name':'Credit'}
				]
				}">
				<template x-for="page in pages">
					<div class="nav-element">
						<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
					</div>
				</template>

			</nav>
			% include(f'frontend/pages/{page}.html')
		</div>
	</body>
</html>
