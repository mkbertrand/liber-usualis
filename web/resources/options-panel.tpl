<div id="options-panel">
	<template x-if="initialized">
		<div id="options-panel-require-initialized-container">
			<div id="coincidences-list-container">
				<h3 class="options-panel-section-head">{{text['coincidences-list-title']}}</h3>
				<h4 class="coincidences-label">{{text['coincidences-list-primary']}}</h4>
				<div id="primary-entry" class="coincidence-entry" x-text="abbreviateName(liturgicalDay.primary[0])"></div>
				<h4 class="coincidences-label">{{text['coincidences-list-commemorations']}}</h4>
				<template x-for="commemoration in liturgicalDay.commemorations.filter((commemoration) => !commemoration[1].includes('suffragium'))">
					<div class="coincidence-entry" x-text="abbreviateName(commemoration[0])"></div>
				</template>
				<h4 class="coincidences-label">{{text['coincidences-list-omissions']}}</h4>
				<template x-for="omission in liturgicalDay.omissions">
					<div class="coincidence-entry" x-text="abbreviateName(omission[0])"></div>
				</template>
				<h4 class="coincidences-label">{{text['coincidences-list-votives']}}</h3>
			</div>
		</div>
	</template>
	<h3 class="options-panel-section-head">{{text['options-panel-title']}}</h3>
	% if locale != 'la':
	<div>
		<input type="checkbox" id="translation-toggle" x-model="parameters.translation" />
		<label for="translation-toggle">{{text['translation-toggle']}}</label>
	</div>
	<div>
		<input type="checkbox" id="side-by-side-toggle" x-model="parameters['side-by-side']" :disabled="!resolveParameters(parameters).translation" />
		<label for="side-by-side-toggle" :class="resolveParameters(parameters).translation ? '' : 'option-disabled'">Side-by-side translation (experimental)</label>
	</div>
	% end
	<div>
		<div>
			<input type="radio" value="plainchant" id="recitation-select-plainchant" x-model="parameters.recitation" />
			<label for="recitation-select-plainchant">{{text['recitation-select-plainchant']}}</label>
		</div>
		<div>
			<input type="radio" value="recto-tono" id="recitation-select-recto-tono" x-model="parameters.recitation" />
			<label for="recitation-select-recto-tono">{{text['recitation-select-recto-tono']}}</label>
		</div>
		<div>
			<input type="radio" value="private" id="recitation-select-private" x-model="parameters.recitation" />
			<label for="recitation-select-private">{{text['recitation-select-private']}}</label>
		</div>
	</div>
	<div>
		<input type="checkbox" value="bottompanel" id="bottom-panel-toggle" x-model="bottompanel" />
		<label for="bottom-panel-toggle">{{text['bottom-panel-toggle']}}</label>
	</div>
	<div id="desired-select-wrapper">
		<div id="desired-select-container" x-data="{ambitEntries: [
			['omnes', 'Officium'],
			['diei', 'Officium diei'],
			['officium-parvum-bmv', 'Officium Parvum B.M.V.'],
			['officium-defunctorum', 'Officium Defunctorum'],
			['semper-cum-opbmv', 'Officium diei cum Officio Parvo B.M.V.'],
			['psalmi-graduales', 'Psalmi Graduales'],
			['psalmi-poenitentiales', 'Psalmi Pœnitentiales'],
			['ordo-commendationis-animae', 'Ordo Commendationis Animæ'],
			['formula-indulgentiam-articulo-mortis', 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis'],
			['benedictio-mensae', 'Benedictio Mensæ'],
			['itinerarium', 'Itinerarium Clericorum']
		]}">
			<h3 class="options-panel-section-head">{{text['selection-title']}}</h3>
			<template x-for="entry in ambitEntries">
				<div>
					<input type="radio" :value="entry[0]" :id="`desired-select-${entry[0]}`" x-model="parameters.desired" />
					<label :for="`desired-select-${entry[0]}`" x-text="entry[1]" />
				</div>
			</template>
		</div>
	</div>
	<div x-data="{votiveEntries: [
		['de-sanctis-angelis', 'De Ss. Angelis.'],
		['de-sanctis-apostolis', 'De Ss. Apostolis.'],
		['de-joseph', 'De S. Joseph.'],
		['de-eucharistiae-sacramento', 'De Ss. Eucharistiæ Sacramento.'],
		['de-passione', 'De Passione D.N.J.C.'],
		['de-immaculata-conceptione', 'De Immaculata Conceptione.']
	]}">
		<h3 class="options-panel-section-head">Votive Offices.</h3>
		<div id="votive-office-selection-inner">
			<template x-for="entry in votiveEntries">
				<div class="votive-office-entry">
					<input type="checkbox" :value="entry[0]" :id="`votive-select-${entry[0]}`" x-model="parameters.votives[entry[0]]"/>
					<label :for="`votive-select-${entry[0]}`" x-text="entry[1]"></label>
				</div>
			</template>
		</div>
	</div>
</div>
