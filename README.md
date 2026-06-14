# kvimarka92-bible-search

Norwegian Bible 1930 search index and quote lookup prototype for Kvimarka92.

## Purpose

This repository is intended to prototype a Norwegian Bible quote lookup system.

Typical use case:

> The user remembers part of a Bible quote and wants to find where it is written.

Example searches:

```txt
frykt ikke for jeg er med
kast all eders sorg
kom til mig alle
alt virker sammen til gode
```

The first goal is to return likely Bible references from the Norwegian 1930 Bible text.

## Planned scope

- Store/import Norwegian Bible 1930 source text.
- Normalize old/new spelling variants.
- Build searchable verse and passage data.
- Support exact phrase search.
- Support partial word search.
- Support fuzzy-ish matching.
- Return likely references with short snippets.
- Later connect this search to the Kvimarka92 Experiences app.

## Important licensing note

The actual Bible 1930 text is not included in this starter package.

Before adding source text, document:

- exact source
- source URL / origin
- license statement
- date imported
- any transformations made

See:

```txt
LICENSES/nb-1930-source.md
```

## Suggested data layout

```txt
data/source/
  nb-1930-raw.txt

data/normalized/
  nb-1930-verses.json
  nb-1930-passages.json
  nb-1930-books.json

data/index/
  nb-1930-search-index.json
```

## Development

Run current smoke test:

```bash
npm test
```

Open local test page:

```txt
public/bibel-sok.html
```

For now the test page uses a tiny in-memory sample dataset. Replace that with the real generated index later.
