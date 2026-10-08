<div id="options-panel">
	<h2>{{text['options-panel-title']}}</h2>
	<h3>{{text['display-title']}}</h3>
	% if locale != 'la':
	<div>
		<input type="checkbox" id="translation-toggle" />
		<label for="translation-toggle">{{text['translation-toggle']}}</label>
	</div>
	<div>
		<input type="checkbox" id="side-by-side-toggle" />
		<label for="side-by-side-toggle">{{text['side-by-side-toggle']}}</label>
	</div>
	% end
	<div>
		<input type="checkbox" id="chant-toggle" />
		<label for="chant-toggle">{{text['chant-toggle']}}</label>
	</div>
	<div>
		<input type="checkbox" id="play-chant-toggle" />
		<label for="play-chant-toggle">{{text['play-chant-toggle']}}</label>
	</div>
  <div>
		<input type="checkbox" id="priest-toggle" />
		<label for="priest-toggle">{{text['priest-toggle']}}</label>
  </div>
	<div id="desired-select-wrapper" class="options-panel-section">
		<div id="desired-select-container" class="options-panel-section">
			<h3>{{text['selection-title']}}</h3>
			% # [id, label, select, opt tag]
			% for ambit_entry in [['omnes', 'Officium', 'primarium', ''], ['diei', 'Officium diei', 'primarium', 'sine-ritibus'], ['officium-parvum-bmv', 'Officium Parvum B.M.V.', 'officium-parvum-bmv', ''], ['semper-cum-opbmv', 'Officium diei cum Officio Parvo B.M.V.', 'primarium', 'cum-opbmv']]:
				<div>
					<input type="radio" name="desired" autocomplete="off" value="{{ambit_entry[0]}}" id="desired-select-{{ambit_entry[0]}}" data-select="{{ambit_entry[2]}}" data-opt-tag="{{ambit_entry[3]}}" />
					<label for="desired-select-{{ambit_entry[0]}}">{{ambit_entry[1]}}</label>
				</div>
			% end
		</div>
	</div>
	<div class="options-panel-section">
		<h3>{{text['votive-office-select-title']}}</h3>
		<div id="votive-office-selection-inner" class="options-panel-section">
			% for votive_entry in [['de-sanctis-angelis', 'De Ss. Angelis.'], ['de-sanctis-apostolis', 'De Ss. Apostolis.'], ['de-joseph', 'De S. Joseph.'], ['de-eucharistiae-sacramento', 'De Ss. Eucharistiæ Sacramento.'], ['de-passione', 'De Passione D.N.J.C.'], ['de-immaculata-conceptione', 'De Immaculata Conceptione.']]:
				<div class="votive-office-entry">
					<input type="checkbox" value="{{votive_entry[0]}}" id="votive-select-{{votive_entry[0]}}" data-votive="{{votive_entry[0]}}" />
					<label for="votive-select-{{votive_entry[0]}}">{{votive_entry[1]}}</label>
				</div>
			% end
		</div>
	</div>
</div>
