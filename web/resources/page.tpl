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
		<link rel="stylesheet" type="text/css" href="/resources/styles/{{page}}.css?v=22">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css?v=12">
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen"><img id="sidebar-nav-toggle" src="/resources/svg/burger-menu.svg" /></button>
				<div id="project-logo">
					<a href="/"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS"></a>
				</div>
			</div>
			% include(f'web/locales/{locale}/resources/sidemenu.html')
			% if page == 'pray':
				% include(f'web/resources/{page}.tpl', ritegenversion='16', text=json.load(open(f'web/locales/{locale}/pages/{page}.json')))
			% else:
				% include(f'web/locales/{locale}/pages/{page}.html')

		</div>
	</body>
</html>
