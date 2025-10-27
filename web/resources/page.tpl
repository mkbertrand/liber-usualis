<!DOCTYPE html>

<!-- Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json

<html lang="{{locale.split('-')[0]}}">
	<head>
		<title>{{title}}</title>
		<script type="application/ld+json">
		{
			"@context":"https://schema.org",
			"@type":"WebSite",
			"name":"Liber Usualis",
			"url":"https://liberusualis.org/"
		}
		</script>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei.png">
		<link rel="stylesheet" type="text/css" href="/resources/styles/{{page}}.css?v=30">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css?v=13">
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap');
</style>
	</head>
	<body>
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen"><img id="sidebar-nav-toggle" src="/resources/svg/burger-menu.svg" /></button>
				<div id="project-logo">
					<a href="/{{preferredlocale}}/index"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS"></a>
				</div>
			</div>
			% include('web/resources/sidemenu.tpl', preferredlocale=preferredlocale, text=json.load(open(f'web/locales/{preferredlocale}/resources/sidemenu.json')))
			% if page == 'pray':
				% include(f'web/pages/{page}.tpl', ritegenversion='22', text=json.load(open(f'web/locales/{locale}/pages/{page}.json')))
			% else:
				% include(f'web/locales/{locale}/pages/{page}.html')

		</div>
	</body>
</html>
