import { signal } from '@preact/signals-core';

export function makeLiturgyStore() {
  const votives = signal(JSON.parse(localStorage.getItem('votivePreferences') || '[]'));
  const setVotives = (newVotives) => {
    localStorage.setItem('votivePreferences', JSON.stringify(newVotives));
    votives.value = newVotives;
  };

  return {
    votives: votives,
    setVotives: setVotives,
    toggleVotive: (tag) => { setVotives(votives.value.includes(tag) ? votives.value.filter(v => v != tag) : [...votives.value, tag]); }
  };
}
