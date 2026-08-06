<!DOCTYPE html>

<!-- Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% import version_management
% locale = locales[0]

<html lang='en'>
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
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/menu.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource(f'/styles/{page}.css')}}>
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div id="site-wrapper-home">
			<div id="top-bar-title">
				<div id="project-logo">
					<div id="logo-link-wrapper"><a id="logo-link" href="/{{locale}}/index"><img id="logo" src="/resources/agnus-dei.webp" alt="LIBER USUALIS"></a></div>
				</div>
				<select id="locale-selector" onchange="window.location.assign('/' + this.value + window.location.pathname.slice(3) + window.location.search)">
					<option value="la" {{!'selected' if locale == 'la' else ''}}>LA</option>
					<option value="en" {{!'selected' if locale == 'en' else ''}}>EN</option>
					<option value="de" {{!'selected' if locale == 'de' else ''}}>DE</option>
				</select>
			</div>
			<div id="content-container-home">
				% include(f'web/pages/{page}.tpl', text=json.load(open(version_management.bestlocalized(f'/pages/{page}.json', locales))), locale=locale)
			</div>
		</div>
	</body>
</html>
