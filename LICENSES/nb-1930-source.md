# Norwegian Bible 1930 source and license notes

## Source used

```txt
Source name: CrossWire SWORD module Norsk
Module name: Norsk
Book name: Bibelen på Norsk (1930)
Download URL: https://www.crosswire.org/sword/servlet/SwordMod.Verify?modName=Norsk&pkgType=raw
Module info: https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=Norsk
Imported file: data/Source/NorskUtgave1930.zip
```

## Module metadata from `mods.d/norsk.conf`

```txt
[Norsk]
ModDrv=zText
DataPath=./modules/texts/ztext/norsk/
CompressType=ZIP
BlockType=BOOK
Encoding=UTF-8
SourceType=OSIS
SwordVersionDate=2020-02-08
Lang=nb
LCSH=Bible.Norwegian Bokmal
Versification=KJV
Abbreviation=Bibelen på Norsk
Description=Bibelen på Norsk (1930)
TextSource=http://unbound.biola.edu/
DistributionLicense=Public Domain
Version=2.0
InstallSize=1822998
```

## About text from CrossWire module

```txt
Denne er det Norsk Bibelselskapets 1930 utgave av Bibelen på Norsk (Bokmål)

This is the Norwegian Bible Society’s 1930 edition of the Bible in Bokmål Norwegian

Text scanned and proofed by H. Priebe and co-workers. Based on the version prepared by Tore Vamraak.
```

## Project policy

This repository should stay private until:

```txt
- the imported text has been verified
- source/license notes have been reviewed
- generated full-text files have been quality checked
```

## Generated files

The import process generates:

```txt
data/normalized/nb-1930-books.json
data/normalized/nb-1930-verses.json
data/normalized/nb-1930-passages.json
data/index/nb-1930-search-index.json
data/source-manifest.json
```
