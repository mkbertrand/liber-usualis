<div id="rites-menu-wrapper" x-cloak x-show="ritesMenuOpen" x-transition @click.outside="ritesMenuOpen = false">
  <h3 id="rites-menu-title">{{text['rites-menu-title']}}</h3>
    <a class="rite-link" href="/{{locale}}/officium/{{date}}/officium-defunctorum/matutinum-laudes" x-rite-link :href="$store.router.makeURL({prayerType: 'officium', select: 'officium-defunctorum', occasion: 'matutinum-laudes'})" @click="ritesMenuOpen = false">Officium Defunctorum (Ad Matutinum et Laudes)</a>
    <a class="rite-link" href="/{{locale}}/officium/{{date}}/officium-defunctorum/vesperae" x-rite-link :href="$store.router.makeURL({prayerType: 'officium', select: 'officium-defunctorum', occasion: 'vesperae'})" @click="ritesMenuOpen = false">Officium Defunctorum (Ad Vesperas)</a>
  % for rites_menu_entry in [['psalmi-graduales', 'Psalmi Graduales'], ['psalmi-poenitentiales', 'Psalmi Pœnitentiales'], ['ordo-commendationis-animae', 'Ordo Commendationis Animæ'], ['formula-indulgentiam-articulo-mortis', 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis']]:
  <a class="rite-link" href="/{{locale}}/ritus/{{date}}/{{rites_menu_entry[0]}}" x-rite-link :href="$store.router.makeURL({prayerType: 'ritus', select: 'primarium', occasion: '{{rites_menu_entry[0]}}'})" @click="ritesMenuOpen = false">{{!rites_menu_entry[1]}}</a>
  % end
  <a class="rite-link" href="/{{locale}}/ritus/{{date}}/pro-prandio" x-rite-link :href="$store.router.makeURL({prayerType: 'ritus', select: 'primarium', occasion: 'pro-prandio'})" @click="ritesMenuOpen = false">Benedictio Mensæ (Pro Prandio)</a>
  <a class="rite-link" href="/{{locale}}/ritus/{{date}}/pro-coena" x-rite-link :href="$store.router.makeURL({prayerType: 'ritus', select: 'primarium', occasion: 'pro-coena'})" @click="ritesMenuOpen = false">Benedictio Mensæ (Pro Cœna)</a>
  <a class="rite-link" href="/{{locale}}/ritus/{{date}}/itinerarium" x-rite-link :href="$store.router.makeURL({prayerType: 'ritus', select: 'primarium', occasion: 'itinerarium'})" @click="ritesMenuOpen = false">Itinerarium Clericorum</a>
</div>
