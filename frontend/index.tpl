<!DOCTYPE html>
<html lang='en'>
	<head>
		<title>Psalterium</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="icon" type="image/x-icon" href="/resources/agnus-dei.png">
		<link rel="stylesheet" type="text/css" href="/styles/index.css">
		<link rel="stylesheet" type="text/css" href="/styles/breviarium.css">
		<script async data-main="/js/gabc-chant.js" src="/js/require.js"></script>
		<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
	</head>
	<body>
		<div class='lyric-font' style='font-size: 1px; visibility: hidden;' >I<span class='b'>I<span class='i'>I</span></span><span class='i'>I</span><span style="font-family:'Exsurge Characters';">V. R.</span></div>
		<div x-data="{
			day: new Date(),
			get Hour() {
				return fetch('/breviarium?date=' + this.day.toISOString().substring(0,10) + '&hour=vesperae&chant=false').then((response) => response.text())
			}
			}">
			<div id='content-wrapper'>
				<div x-html="Hour"></div>
			</div>
		</div>
	</body>
</html>
