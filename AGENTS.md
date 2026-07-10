# Repository Instructions

This project is a data-driven liturgical text generation system. All code changes
must preserve the architecture described in `architecture.org`; read that file
before making non-trivial backend, frontend, or data-shape changes.

## Architectural Rules

- Keep liturgical behavior data-driven. Prefer tagged JSON data, rule tables,
  category files, discrimina tables, and sequentes rules over hard-coded feast,
  date, or text-selection logic.
- Preserve the main backend flow: request parsing in `server.py`, kalendar lookup
  in `kalendar/`, prioritization in `prioritizer.py`, data loading in
  `datamanage.py`, content assembly/search in `breviarium.py`, and psalm lookup in
  `psalms.py`.
- Keep HTTP concerns at the edge. `server.py` should parse parameters, call pure
  domain functions, and serialize results; avoid placing reusable liturgical
  rules or search logic in route handlers unless `architecture.org` explicitly
  documents that exception.
- Do not bypass the tag system. New content lookup should be expressed as tag-set
  queries and resolved through the established search/discrimination pipeline.
- Treat tags as the central domain model. Tags are lowercase hyphen-separated
  strings; collections of tags should normally be `frozenset` when they represent
  immutable domain facts.
- Respect positional and temporal contradiction handling. Do not introduce code
  that silently allows mutually exclusive tags from `data/{book}/categoriae/` to
  coexist in a resolved query.
- Keep frontend state and rendering aligned with `architecture.org`: Bottle
  templates provide the page shell, Alpine manages UI state, `pray.js` handles
  events, and `ritegen.js` defines ritual ambits/rendering structure.
- Update `architecture.org` in the same change when you intentionally alter module
  responsibilities, endpoint behavior, data flow, tag semantics, or file layout.

## Python Style

- Prefer functional, explicit transformations over object-heavy designs.
- Write small pure functions that accept all required inputs as parameters and
  return new values rather than mutating inputs or relying on hidden globals.
- Use immutable values for domain data: `frozenset` for tag sets, tuples for fixed
  sequences, and copied dictionaries/lists when deriving modified structures.
- Avoid classes unless they provide a clear architectural benefit. Prefer plain
  dictionaries, typed tuples, dataclasses with `frozen=True`, or simple module-level
  functions for domain records and transformations.
- Keep side effects isolated at boundaries: file/network I/O in data-loading or
  server layers, caching in clearly named loader functions, and rendering or HTTP
  serialization at the outer edge.
- Do not mix data loading, rule application, and presentation formatting in one
  function. Compose these as separate transformations when behavior grows.
- Make dependencies explicit. Pass `book`, `day`, `query`, `pile`, selected tag
  sets, alternates, and options into functions instead of reading ambient state.
- Preserve referential transparency where practical: the same inputs should produce
  the same outputs, especially in kalendar calculation, prioritization, search,
  discrimination, tag expansion, and rite assembly.
- Prefer expressions, comprehensions, `map`/`filter` only when readable, and
  standard-library functions over manual stateful loops. Use loops when they are
  clearer, but keep mutation local and do not leak partially built state.
- Avoid in-place mutation of caller-owned collections. If mutation is necessary
  for performance or clarity, copy first or confine it to a private local value.
- Keep functions deterministic except where their purpose is explicitly I/O,
  caching, logging, or time/date acquisition.
- Use precise names from the domain model (`tagset`, `query`, `pile`, `selected`,
  `alternates`, `datum`, `quaesitum`, `commemorationes`) instead of generic names
  when working in the liturgical pipeline.
- Keep comments rare and useful. Explain non-obvious liturgical or architectural
  reasoning; do not narrate simple assignments.
- Use ASCII in code unless the existing data/text requires Latin diacritics or
  another established project convention.

## Data And Tagging

- Keep JSON content files declarative. Do not encode procedural behavior in content
  strings or ad hoc keys when an existing tag, rule table, category, or discrimina
  mechanism can express it.
- Preserve the expected entry shape: `tags`, `datum`, optional `src`, and the
  documented expansion behavior for extra keys in `datamanage.py`.
- When adding tags, verify that they belong in the appropriate category file if
  they participate in positional, temporal, object, or feast classification.
- When multiple entries can match a query, prefer fixing tags or discrimina rules
  over adding special-case search code.
- Keep translations parallel to source content through language tags and the
  existing translation lookup mechanism.

## Testing And Verification

- Add or update tests for changes to kalendar generation, prioritization, tag
  expansion, search/discrimination, psalm lookup, data loading, endpoint output,
  or rendering-relevant JSON shape.
- Prefer focused regression tests that encode the liturgical scenario, input date,
  tags, and expected selected content or ordering.
- Run the relevant test subset before finishing. If the appropriate command is not
  obvious, inspect the repository and use the smallest command that validates the
  changed behavior.
- For data-only changes, validate that affected JSON parses and that representative
  `/day` or `/rite` generation paths still resolve without ambiguity.

## Change Discipline

- Make the smallest correct change that preserves the documented data flow.
- Do not add compatibility layers, fallback behavior, or duplicated pathways unless
  there is a concrete persisted-data or external-consumer requirement.
- Do not introduce new dependencies or frameworks without a clear architectural
  reason and user approval.
- If a requested change conflicts with `architecture.org`, stop and ask whether to
  update the architecture or choose a design that fits it.
- Before considering work complete, check that the change preserves functional
  purity where practical, keeps side effects at boundaries, and does not hard-code
  liturgical decisions that belong in data.
