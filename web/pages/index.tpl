<!DOCTYPE html>

<!-- Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al. -->

<html lang='en'>
	<head>
		<title>Home</title>
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
		<link rel="stylesheet" type="text/css" href="/resources/styles/index.css?v=1">
		<link rel="stylesheet" type="text/css" href="/resources/styles/style.css?v=11">
		<link rel="apple-touch-icon" href="/resources/agnus-dei.png">
		<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.x.x/dist/cdn.min.js"></script>
		<script type="text/javascript" defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div id="site-wrapper-home">
			<div id="top-bar-title">
				<div id="project-logo">
					<a href="/{{preferredlocale}}/index/"><img id="logo" src="/resources/agnus-dei.png" alt="LIBER USUALIS PROJECT"></a>
				</div>
			</div>
			<div id="content-container-outer-home">
				<div id="side-panel-left">
				</div>
				<div id="home-screen">
					<h1 id="main-title-label">LIBER USUALIS PROJECT</h1>
					<nav id="center-nav" x-data="{
						pages:[
							{'path':'/{{preferredlocale}}/pray/', 'name':'{{text['pray']}}'},
							{'path':'/{{preferredlocale}}/about/', 'name':'{{text['about']}}'},
							{'path':'/{{preferredlocale}}/help/', 'name':'{{text['help']}}'},
							{'path':'/{{preferredlocale}}/credit/', 'name':'{{text['credit']}}'}
						]
						}">
						<template x-for="page in pages">
							<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
						</template>

					</nav>
					<div style="height:2em;"></div>
					<form id="paypal-donate-button" action="https://www.paypal.com/donate" method="post" target="_top">
					<input type="hidden" name="hosted_button_id" value="25CUBHQKYN67Y" />
					<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
					<img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" />
					</form>
				</div>
				<div id="side-panel-right">
				</div>
			</div>
		</div>
	</body>
</html>
