# kvimarka92-bible-search

Norwegian Bible 1930 search index and quote lookup prototype for Kvimarka92.


## Search v3 notes

Search v3 improves quote lookup by:

```txt
- reducing duplicate overlapping passage windows
- expanding old/new Norwegian forms: meg/mig, deg/dig, deres/eders
- improving token scoring for remembered quote fragments
- adding initial synonym support for common remembered phrases
- preferring shorter/single-verse results when scores are equal
```

Example test on Windows PowerShell:

```powershell
npm.cmd test
```


## Search v4 notes

Search v4 improves result presentation by:

```txt
- removing redundant overlapping passage windows
- preferring direct single-verse hits when they contain the same quote
- keeping multi-verse windows only when they add value
```

Example test on Windows PowerShell:

```powershell
npm.cmd test
```


## Search v5 notes

Search v5 adds a small curated boost table for well-known quote fragments.

Examples:

```txt
frykt ikke ... med          -> Jesaja 41,10
kast ... sorg               -> 1 Peter 5,7
kom ... alle ... strever    -> Matteus 11,28
alt virker sammen til gode  -> Romerne 8,28
alle ting ... gode          -> Romerne 8,28
```

The boost does not hide other valid matches; it only ranks likely known references higher.


## Search v5.1 note

This version only fixes the test output label from v4 to v5.
