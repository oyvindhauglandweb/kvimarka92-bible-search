# Data folder

## Source

The current CrossWire ZIP is expected here:

```txt
data/Source/NorskUtgave1930.zip
```

The import script also supports these fallback paths:

```txt
data/source/NorskUtgave1930.zip
data/source/crosswire-norsk-raw.zip
```

## Generated files

Run:

```bash
pip install -r requirements.txt
python scripts/import-crosswire-norsk.py
```

The script generates:

```txt
data/normalized/nb-1930-books.json
data/normalized/nb-1930-verses.json
data/normalized/nb-1930-passages.json
data/index/nb-1930-search-index.json
data/source-manifest.json
```
