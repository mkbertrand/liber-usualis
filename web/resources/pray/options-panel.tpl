<div id="options-panel">
	<template>
		<div id="options-panel-require-initialized-container">
			<div id="coincidences-list-container">
				<h3 class="options-panel-section-head">{{text['coincidences-list-title']}}</h3>
				<h4 class="coincidences-label">{{text['coincidences-list-primary']}}</h4>
				<div id="primary-entry" class="coincidence-entry" x-text="Pray.abbreviateName(liturgicalDay.primary[0])"></div>
				<h4 class="coincidences-label">{{text['coincidences-list-commemorations']}}</h4>
				<template x-for="commemoration in liturgicalDay.commemorations.filter((commemoration) => !commemoration[1].includes('suffragium'))">
					<div class="coincidence-entry" x-text="Pray.abbreviateName(commemoration[0])"></div>
				</template>
				<h4 class="coincidences-label">{{text['coincidences-list-omissions']}}</h4>
				<template x-for="omission in liturgicalDay.omissions">
					<div class="coincidence-entry" x-text="Pray.abbreviateName(omission[0])"></div>
				</template>
				<h4 class="coincidences-label">{{text['coincidences-list-votives']}}</h3>
			</div>
		</div>
	</template>
	<h3 class="options-panel-section-head">{{text['options-panel-title']}}</h3>
	% if locale != 'la':
	<div>
		<input type="checkbox" id="translation-toggle" x-model="displayParameters.showTranslation" />
		<label for="translation-toggle">{{text['translation-toggle']}}</label>
	</div>
	<div>
		<input type="checkbox" id="side-by-side-toggle" x-model="displayParameters.sideBySide" :disabled="!displayParameters.showTranslation" />
		<label for="side-by-side-toggle" :class="displayParameters.showTranslation ? '' : 'option-disabled'">{{text['side-by-side-toggle']}}</label>
	</div>
	% end
	<div>
		<input type="checkbox" id="chant-toggle" x-model="displayParameters.chant" @change="if (!displayParameters.chant) Pray.stopChantPlayback()" />
		<label for="chant-toggle">{{text['chant-toggle']}}</label>
	</div>
	<div>
		<input type="checkbox" id="play-chant-toggle" x-model="displayParameters['play-chant']" :disabled="!displayParameters.chant" @change="if (!displayParameters['play-chant']) Pray.stopChantPlayback()" />
		<label for="play-chant-toggle" :class="displayParameters.chant ? '' : 'option-disabled'">{{text['play-chant-toggle']}}</label>
	</div>
  <div>
		<input type="checkbox" id="priest-toggle" :checked="!contentParameters().opt.includes('privata')" @change="togglePriest()" />
		<label for="priest-toggle">{{text['priest-toggle']}}</label>
  </div>
	<div>
		<input type="checkbox" value="bottomPanelEnabled" id="bottom-panel-toggle" x-model="bottomPanelEnabled" />
		<label for="bottom-panel-toggle">{{text['bottom-panel-toggle']}}</label>
	</div>
	<div id="desired-select-wrapper">
		<div id="desired-select-container" x-data="{ambitEntries: [
			['omnes', 'Officium', 'primarium', ''],
			['diei', 'Officium diei', 'primarium', 'sine-ritibus'],
			['officium-parvum-bmv', 'Officium Parvum B.M.V.', 'officium-parvum-bmv', ''],
			['semper-cum-opbmv', 'Officium diei cum Officio Parvo B.M.V.', 'primarium', 'cum-opbmv']
		]}">
			<h3 class="options-panel-section-head">{{text['selection-title']}}</h3>
			<template x-for="entry in ambitEntries">
				<div>
					<input type="radio" :value="entry[0]" :id="`desired-select-${entry[0]}`" :checked="contentParameters().select == entry[2] && contentParameters().opt.filter(t => t != 'privata').join('+') == entry[3]" @change="setDesired(entry[2], entry[3])" />
					<label :for="`desired-select-${entry[0]}`" x-text="entry[1]" />
				</div>
			</template>
		</div>
	</div>
  <div id="rite-selector-container" x-data="{rites: [
			['psalmi-graduales', 'Psalmi Graduales'],
			['psalmi-poenitentiales', 'Psalmi Pœnitentiales'],
			['ordo-commendationis-animae', 'Ordo Commendationis Animæ'],
			['formula-indulgentiam-articulo-mortis', 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis'],
			['pro-prandio', 'Benedictio Mensæ (pro prandio)'],
			['pro-coena', 'Benedictio Mensæ (pro cœna)'],
			['itinerarium', 'Itinerarium Clericorum']
  ]}">
    <h3 class="options-panel-section-head">Rites</h3>
    <a href="/{{locale}}/officium/{{date}}/officium-defunctorum/matutinum-laudes">Officium Defunctorum (Ad Matutinum et Laudes)</a>
    <a href="/{{locale}}/officium/{{date}}/officium-defunctorum/vesperae">Officium Defunctorum (Ad Vesperas)</a>
    <template x-for="entry in rites">
      <a :href="'/{{locale}}/ritus/{{date}}/' + entry[0]" x-text="entry[1]" />
    </template>
  </div>
	<div x-data="{votiveEntries: [
		['de-sanctis-angelis', 'De Ss. Angelis.'],
		['de-sanctis-apostolis', 'De Ss. Apostolis.'],
		['de-joseph', 'De S. Joseph.'],
		['de-eucharistiae-sacramento', 'De Ss. Eucharistiæ Sacramento.'],
		['de-passione', 'De Passione D.N.J.C.'],
		['de-immaculata-conceptione', 'De Immaculata Conceptione.']
	]}">
		<h3 class="options-panel-section-head">{{text['votive-office-select-title']}}</h3>
		<div id="votive-office-selection-inner">
			<template x-for="entry in votiveEntries">
				<div class="votive-office-entry">
					<input type="checkbox" :value="entry[0]" :id="`votive-select-${entry[0]}`" :checked="contentParameters().votives.includes(entry[0])" @change="toggleVotive(entry[0])"/>
					<label :for="`votive-select-${entry[0]}`" x-text="entry[1]"></label>
				</div>
			</template>
		</div>
	</div>
</div>
