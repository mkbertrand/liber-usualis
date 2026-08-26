<!DOCTYPE html>

<!-- Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% import os
% import version_management
% locale = locales[0]

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
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei-icon.png">
		<link rel="apple-touch-icon" href="/resources/agnus-dei-apple-touch-icon.png">
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/style.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/generic.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource(f'/styles/{page}.css')}}>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body x-data="{darkMode: $persist(false).as('dark-mode')}" :data-theme="darkMode ? 'dark' : 'light'">
		<div id="site-wrapper" x-cloak x-data="{sidebarnavopen: false, locale: '{{locale}}'}">
			<div id="top-bar-title">
				<button id="sidebar-nav-toggle-wrapper" @click="sidebarnavopen = !sidebarnavopen">
				% include('web/resources/svg/hamburger-menu.tpl')
			</button>
				<div id="project-logo">
					<div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.webp" alt="LIBER USUALIS"></a></div>
				</div>
			</div>
			% include('web/resources/sidemenu.tpl', locale=locale, text=json.load(open(f'web/locales/{locale}/resources/sidemenu.json')))
			% if os.path.exists(f'web/pages/{page}.html'):
				% include(f'web/pages/{page}.html')
			% else:
				% include(f'web/pages/{page}.tpl', text=json.load(open(version_management.bestlocalized(f'/pages/{page}.json', locales))))
		</div>
	</body>
</html>
