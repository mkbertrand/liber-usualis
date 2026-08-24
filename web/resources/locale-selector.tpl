% import version_management
<select id="locale-selector" onchange="window.location.assign('/' + this.value + window.location.pathname.slice(3) + window.location.search)">
  % for loc in version_management.DEFINED_LOCALES:
    <option value={{loc}} {{!'selected' if loc == locale else ''}}>{{loc.upper()}}</option>
  % end
</select>
