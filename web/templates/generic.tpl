<!DOCTYPE html>

<!-- Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

% import json
% from pathlib import Path
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
    % include('web/resources/themer.tpl')
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei-icon.png">
		<link rel="apple-touch-icon" href="/resources/agnus-dei-apple-touch-icon.png">
		<link rel="preload" href="/resources/fonts/OldStandardTT-Regular.woff2" as="font" type="font/woff2" crossorigin>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/dist/style.css')}}>
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource('/styles/generic.css')}}>
    % if Path(f'/web/resources/styles/{page}.css').exists():
		<link rel="stylesheet" type="text/css" href={{version_management.get_versioned_resource(f'/styles/{page}.css')}}>
    % end
	</head>
	<body>
		<div id="site-wrapper">
			% include('web/resources/top-bar.tpl', locale=locale, options=False, text=json.load(open(f'web/locales/{locale}/resources/top-bar.json')))
			% include(version_management.bestlocalized(f'/pages/{page}.html', locales))
		</div>
	</body>
</html>
