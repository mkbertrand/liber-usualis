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
			hour: 'vesperae',
			search: '',
			get Hour() {
				return fetch('/breviarium?date=' + this.day.toISOString().substring(0, 10) + '&hour=' + this.hour + '&chant=false').then((response) => response.text())
			},
			get Ritual() {
				function render(data, parameters, language = null, translation = null) {
					if (typeof data === 'object' && Array.isArray(data)) {
						let ret = [];
						// Ridiculous language requires me to store the count because variable scope doesn't matter apparently.
						for (let i = 0, count = data.length; i < count; i++) {
							const rendered = render(data[i], parameters, language, null);
							if (Array.isArray(rendered)) {
								// I guess js doesn't actually like for in loops for unclear reasons
								for (let j = 0; j < rendered.length; j++) {
									ret.push(rendered[j]);
								}
							} else {
								ret.push(rendered);
							}
						};
						return ret;
					// Native function to check if an object is a dictionary? No need
					} else if (typeof data === 'object') {
						return render(data['datum'], parameters, language, null);
					} else if (typeof data === 'string') {
						let numbers = data.match(/[0-9]+/g);
						if (numbers !== null) {
							numbers.reverse();
							for (i in numbers) {
								data = data.replaceAll(i, '<span class=\'verse-number\'>' + i + '</span>');
							}
						}
						data = data.replace(/\//g, '<br>')
							.replace(/\n/g, '<br>')
							.replace(/N\./g, '<span class=\'red\'>N.</span>')
							.replace(/R\./g, '<span class=\'red\'>&#8479;.</span>')
							.replace(/V\./g, '<span class=\'red\'>&#8483;.</span>')
							.replace(/R\. br./g, '<span class=\'red\'>&#8479;. br.</span>')
							.replace(/✠/g, '<span class=\'red\'>&malt;</span>')
							.replace(/✙/g, '<span class=\'red\'>&#10009;</span>')
							.replace(/\+/g, '<span class=\'red\'>&dagger;</span>')
							.replace(/\*/g, '<span class=\'red\'>&ast;</span>');
						return data;
					} else {
						return 'error';
					}
				};

				// Just guarantees that the return is an array so that the x-for doesn't break
				function outerrender(data, parameters, language = null, translation = null) {
					const rendered = render(data, parameters, language, translation);
					return Array.isArray(rendered) ? rendered : [rendered];
				};
				return fetch('/ritual?date=' + this.day.toISOString().substring(0, 10) + '&hour=' + this.hour + '&chant=false').then((response) => response.json()).then((data) => outerrender(data, null, null, null))
			}
		}">
			<div id="top-fixed-wrapper">
				<div id="hour-selector-wrapper">
					<div class="hour-selector-item-container">
						<button id="button-selector-matutinum-laudes" class="hour-selector-button" @click="hour = 'matutinum+laudes'">Matins &amp; Lauds</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-prima" class="hour-selector-button" @click="hour = 'prima'">Prime</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-tertia" class="hour-selector-button" @click="hour = 'tertia'">Terce</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-sexta" class="hour-selector-button" @click="hour = 'sexta'">Sext</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-nona" class="hour-selector-button" @click="hour = 'nona'">None</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-vesperae" class="hour-selector-button" @click="hour = 'vesperae'">Vespers</button>
					</div>
					<div class="hour-selector-item-container">
						<button id="button-selector-completorium" class="hour-selector-button" @click="hour = 'completorium'">Compline</button>
					</div>
				</div>
			</div>
			<div id="content-wrapper">
				<template x-for="element in Ritual">
					<div class="text-content-latin">
						<p x-html="element"></p>
					</div>
				</template>
			</div>
			<div id="date-selector-wrapper">
				<div class="date-selector-item-container">
					<button id="date-selector-decrement" class="date-selector-button" @click="day = new Date(day.getTime() - 86400000); search = day.toISOString().substring(0,10)">&#8592;</button>
				</div>
				<div class="date-selector-item-container">
					<input id="date-selector-text" type="date" x-model="search" x-init="search = day.toISOString().substring(0,10)">
				</div>
				<div class="date-selector-item-container">
					<button id="date-selector-text-submit" class="date-selector-button" @click="day = new Date(search + new Date().toISOString().substring(10))">&#8629;</button>
				</div>
				<div class="date-selector-item-container">
					<button id="date-selector-increment" class="date-selector-button" @click="day = new Date(day.getTime() + 86400000); search = day.toISOString().substring(0,10)">&#8594;</button>
				</div>
			</div>
		</div>
	</body>
</html>
