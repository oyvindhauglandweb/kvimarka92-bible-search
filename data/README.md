# Data folder

This folder will contain source text, normalized verse data and generated search indexes.

## Folders

```txt
source/
  Raw imported source files.

normalized/
  Structured verse and passage JSON generated from source.

index/
  Search indexes generated from normalized data.
```

## Expected verse shape

```json
{
  "id": "isa-41-10",
  "book": "Jesaja",
  "bookNo": 23,
  "chapter": 41,
  "verse": 10,
  "reference": "Jesaja 41,10",
  "text": "...",
  "normalizedText": "..."
}
```
