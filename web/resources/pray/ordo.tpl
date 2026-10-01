<p x-text="date"></p>
<h3 x-text="$store.pray.ordo.primarium"></h3>
<template x-for="commemoration in $store.pray.ordo.commemorationes">
  <p x-text="$commemoration.name"></p>
</template>

