<!DOCTYPE html>

<!-- Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

<html lang='en'>
	<head>
		<title>Breviarium Romanum</title>
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
		<link rel="stylesheet" type="text/css" href="/resources/styles/breviarium.css?v=2">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css?v=12">
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div id="site-wrapper-home">
			<div id="top-bar-title">
				<div id="project-logo">
					<div id="logo-link-wrapper"><a id="logo-link" href="/{{preferredlocale}}/index"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS"></a></div>
				</div>
			</div>
			<div id="content-container-outer-home">
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
					<p>Hi! You're on an incomplete part of the website. This navigation page is only somewhat usable (you will note that the De Anno link goes to /pray and that /rubricae does not yet have the complete rubrics). Don't worry; using this page will not break anything.</p>
					<nav id="breviarium-contents-nav" x-data="{
						pages:[
							{'path':'/{{preferredlocale}}/pray', 'name':'{{text['de-anno']}}'},
							{'path':'/{{preferredlocale}}/kalendar', 'name':'{{text['kalendar']}}'},
							{'path':'/{{preferredlocale}}/rubricae', 'name':'{{text['rubrics']}}'},
							{'path':'/{{preferredlocale}}/pray', 'name':'{{text['pray']}}'}
						]
						}">
						<template x-for="page in pages">
							<p><a class="nav-element" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a></p>
						</template>
					</nav>
				</div>
				<div id="side-panel-right">
				</div>
			</div>
		</div>
	</body>
</html>
