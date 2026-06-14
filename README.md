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
