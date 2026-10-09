<a class="rite-link" href="/{{locale}}/officium/{{date}}/officium-defunctorum/matutinum-laudes" data-rite-link data-prayer-type="officium" data-select="officium-defunctorum" data-occasion="matutinum-laudes">Officium Defunctorum (Ad Matutinum et Laudes)</a>
<a class="rite-link" href="/{{locale}}/officium/{{date}}/officium-defunctorum/vesperae" data-rite-link data-prayer-type="officium" data-select="officium-defunctorum" data-occasion="vesperae">Officium Defunctorum (Ad Vesperas)</a>
% for rites_menu_entry in [['psalmi-graduales', 'Psalmi Graduales'], ['psalmi-poenitentiales', 'Psalmi Pœnitentiales'], ['ordo-commendationis-animae', 'Ordo Commendationis Animæ'], ['formula-indulgentiam-articulo-mortis', 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis']]:
<a class="rite-link" href="/{{locale}}/ritus/{{date}}/{{rites_menu_entry[0]}}" data-rite-link data-prayer-type="ritus" data-select="primarium" data-occasion="{{rites_menu_entry[0]}}">{{!rites_menu_entry[1]}}</a>
% end
<a class="rite-link" href="/{{locale}}/ritus/{{date}}/pro-prandio" data-rite-link data-prayer-type="ritus" data-select="primarium" data-occasion="pro-prandio">Benedictio Mensæ (Pro Prandio)</a>
<a class="rite-link" href="/{{locale}}/ritus/{{date}}/pro-coena" data-rite-link data-prayer-type="ritus" data-select="primarium" data-occasion="pro-coena">Benedictio Mensæ (Pro Cœna)</a>
<a class="rite-link" href="/{{locale}}/ritus/{{date}}/itinerarium" data-rite-link data-prayer-type="ritus" data-select="primarium" data-occasion="itinerarium">Itinerarium Clericorum</a>
