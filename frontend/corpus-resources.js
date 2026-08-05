export class CorpusResources {
  constructor() {
    this.ready = false;
    this.invitatoria = null;
    this.psalmTones = null;
    this.euouaes = null;
  }

  async load() {
    Promise.allSettled([
      fetch('/chant/liber-usualis-chant/nocturnale/untagged/invitatoria.json').then(data => data.json()).then(json => this.invitatoria = json),
      fetch('/chant/liber-usualis-chant/untagged/toni-psalmorum.json').then(data => data.json()).then(json => this.psalmTones = json),
      fetch('/chant/liber-usualis-chant/untagged/euouae.json').then(data => data.json()).then(json => this.euouaes = json)
    ]).then(() => this.ready = true);
  }
}
