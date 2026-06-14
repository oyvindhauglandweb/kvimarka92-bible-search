#!/usr/bin/env python3
"""
Import CrossWire SWORD module Norsk / Bibelen på Norsk (1930) to JSON.\n\nVersion: v2 - fixed OSIS keys for 1/2 Kings and 1/2 Chronicles.

Expected source file, one of:
  data/Source/NorskUtgave1930.zip
  data/source/NorskUtgave1930.zip
  data/source/crosswire-norsk-raw.zip

Requires:
  pip install -r requirements.txt

Run:
  python scripts/import-crosswire-norsk.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from pysword.modules import SwordModules
except ImportError:
    print("ERROR: Missing dependency: pysword")
    print("Run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[1]

SOURCE_CANDIDATES = [
    ROOT / "data" / "Source" / "NorskUtgave1930.zip",
    ROOT / "data" / "source" / "NorskUtgave1930.zip",
    ROOT / "data" / "source" / "crosswire-norsk-raw.zip",
]

OUT_NORMALIZED = ROOT / "data" / "normalized"
OUT_INDEX = ROOT / "data" / "index"
OUT_MANIFEST = ROOT / "data" / "source-manifest.json"

# KJV versification chapter counts.
BOOKS = [
    ("Genesis", "1mos", "1 Mosebok", 50),
    ("Exodus", "2mos", "2 Mosebok", 40),
    ("Leviticus", "3mos", "3 Mosebok", 27),
    ("Numbers", "4mos", "4 Mosebok", 36),
    ("Deuteronomy", "5mos", "5 Mosebok", 34),
    ("Joshua", "jos", "Josva", 24),
    ("Judges", "dom", "Dommerne", 21),
    ("Ruth", "rut", "Rut", 4),
    ("1 Samuel", "1sam", "1 Samuel", 31),
    ("2 Samuel", "2sam", "2 Samuel", 24),
    ("1 Kings", "1kong", "1 Kongebok", 22),
    ("2 Kings", "2kong", "2 Kongebok", 25),
    ("1 Chronicles", "1krøn", "1 Krønikebok", 29),
    ("2 Chronicles", "2krøn", "2 Krønikebok", 36),
    ("Ezra", "esra", "Esra", 10),
    ("Nehemiah", "neh", "Nehemja", 13),
    ("Esther", "est", "Ester", 10),
    ("Job", "job", "Job", 42),
    ("Psalms", "sal", "Salmene", 150),
    ("Proverbs", "ord", "Ordspråkene", 31),
    ("Ecclesiastes", "fork", "Forkynneren", 12),
    ("Song of Solomon", "høys", "Høysangen", 8),
    ("Isaiah", "jes", "Jesaja", 66),
    ("Jeremiah", "jer", "Jeremia", 52),
    ("Lamentations", "klag", "Klagesangene", 5),
    ("Ezekiel", "esek", "Esekiel", 48),
    ("Daniel", "dan", "Daniel", 12),
    ("Hosea", "hos", "Hosea", 14),
    ("Joel", "joel", "Joel", 3),
    ("Amos", "amos", "Amos", 9),
    ("Obadiah", "obad", "Obadja", 1),
    ("Jonah", "jona", "Jona", 4),
    ("Micah", "mika", "Mika", 7),
    ("Nahum", "nah", "Nahum", 3),
    ("Habakkuk", "hab", "Habakkuk", 3),
    ("Zephaniah", "sef", "Sefanja", 3),
    ("Haggai", "hag", "Haggai", 2),
    ("Zechariah", "sak", "Sakarja", 14),
    ("Malachi", "mal", "Malaki", 4),
    ("Matthew", "matt", "Matteus", 28),
    ("Mark", "mark", "Markus", 16),
    ("Luke", "luk", "Lukas", 24),
    ("John", "joh", "Johannes", 21),
    ("Acts", "apg", "Apostlenes gjerninger", 28),
    ("Romans", "rom", "Romerne", 16),
    ("1 Corinthians", "1kor", "1 Korinter", 16),
    ("2 Corinthians", "2kor", "2 Korinter", 13),
    ("Galatians", "gal", "Galaterne", 6),
    ("Ephesians", "ef", "Efeserne", 6),
    ("Philippians", "fil", "Filipperne", 4),
    ("Colossians", "kol", "Kolosserne", 4),
    ("1 Thessalonians", "1tess", "1 Tessaloniker", 5),
    ("2 Thessalonians", "2tess", "2 Tessaloniker", 3),
    ("1 Timothy", "1tim", "1 Timoteus", 6),
    ("2 Timothy", "2tim", "2 Timoteus", 4),
    ("Titus", "tit", "Titus", 3),
    ("Philemon", "filem", "Filemon", 1),
    ("Hebrews", "heb", "Hebreerne", 13),
    ("James", "jak", "Jakob", 5),
    ("1 Peter", "1pet", "1 Peter", 5),
    ("2 Peter", "2pet", "2 Peter", 3),
    ("1 John", "1joh", "1 Johannes", 5),
    ("2 John", "2joh", "2 Johannes", 1),
    ("3 John", "3joh", "3 Johannes", 1),
    ("Jude", "jud", "Judas", 1),
    ("Revelation", "åp", "Åpenbaringen", 22),
]


BOOK_KEY_CANDIDATES = {
    "Genesis": ["genesis", "gen", "1mos"],
    "Exodus": ["exodus", "exod", "exo", "2mos"],
    "Leviticus": ["leviticus", "lev", "3mos"],
    "Numbers": ["numbers", "num", "4mos"],
    "Deuteronomy": ["deuteronomy", "deut", "deu", "5mos"],
    "Joshua": ["joshua", "josh", "jos"],
    "Judges": ["judges", "judg", "jdg", "dom"],
    "Ruth": ["ruth", "rut"],
    "1 Samuel": ["1 samuel", "1samuel", "1 sam", "1sam"],
    "2 Samuel": ["2 samuel", "2samuel", "2 sam", "2sam"],
    "1 Kings": ["1Kgs", "1 Kings", "1 kings", "1kings", "1 kgs", "1kgs", "1Ki", "1ki", "1kong"],
    "2 Kings": ["2Kgs", "2 Kings", "2 kings", "2kings", "2 kgs", "2kgs", "2Ki", "2ki", "2kong"],
    "1 Chronicles": ["1Chr", "1 Chronicles", "1 chronicles", "1chronicles", "1 chr", "1chr", "1chron", "1krøn"],
    "2 Chronicles": ["2Chr", "2 Chronicles", "2 chronicles", "2chronicles", "2 chr", "2chr", "2chron", "2krøn"],
    "Ezra": ["ezra", "esra"],
    "Nehemiah": ["nehemiah", "neh"],
    "Esther": ["esther", "est"],
    "Job": ["job"],
    "Psalms": ["psalms", "psalm", "ps", "psa", "sal"],
    "Proverbs": ["proverbs", "prov", "pro", "ord"],
    "Ecclesiastes": ["ecclesiastes", "eccl", "ecc", "fork"],
    "Song of Solomon": ["song of solomon", "song", "songs", "sos", "høysangen", "høys"],
    "Isaiah": ["isaiah", "isa", "jes"],
    "Jeremiah": ["jeremiah", "jer"],
    "Lamentations": ["lamentations", "lam", "klag"],
    "Ezekiel": ["ezekiel", "ezek", "eze", "esek"],
    "Daniel": ["daniel", "dan"],
    "Hosea": ["hosea", "hos"],
    "Joel": ["joel"],
    "Amos": ["amos"],
    "Obadiah": ["obadiah", "obad"],
    "Jonah": ["jonah", "jona"],
    "Micah": ["micah", "mic", "mika"],
    "Nahum": ["nahum", "nah"],
    "Habakkuk": ["habakkuk", "hab"],
    "Zephaniah": ["zephaniah", "zeph", "sef"],
    "Haggai": ["haggai", "hag"],
    "Zechariah": ["zechariah", "zech", "sak"],
    "Malachi": ["malachi", "mal"],
    "Matthew": ["matthew", "matt", "mat", "matteus"],
    "Mark": ["mark", "mrk", "markus"],
    "Luke": ["luke", "luk", "lukas"],
    "John": ["john", "joh", "johannes"],
    "Acts": ["acts", "act", "apg"],
    "Romans": ["romans", "rom"],
    "1 Corinthians": ["1 corinthians", "1corinthians", "1 cor", "1cor", "1kor"],
    "2 Corinthians": ["2 corinthians", "2corinthians", "2 cor", "2cor", "2kor"],
    "Galatians": ["galatians", "gal"],
    "Ephesians": ["ephesians", "eph", "ef"],
    "Philippians": ["philippians", "phil", "fil"],
    "Colossians": ["colossians", "col", "kol"],
    "1 Thessalonians": ["1 thessalonians", "1thessalonians", "1 thess", "1thess", "1tess"],
    "2 Thessalonians": ["2 thessalonians", "2thessalonians", "2 thess", "2thess", "2tess"],
    "1 Timothy": ["1 timothy", "1timothy", "1 tim", "1tim"],
    "2 Timothy": ["2 timothy", "2timothy", "2 tim", "2tim"],
    "Titus": ["titus", "tit"],
    "Philemon": ["philemon", "phlm", "filem"],
    "Hebrews": ["hebrews", "heb"],
    "James": ["james", "jas", "jak"],
    "1 Peter": ["1 peter", "1peter", "1 pet", "1pet"],
    "2 Peter": ["2 peter", "2peter", "2 pet", "2pet"],
    "1 John": ["1 john", "1john", "1 joh", "1joh"],
    "2 John": ["2 john", "2john", "2 joh", "2joh"],
    "3 John": ["3 john", "3john", "3 joh", "3joh"],
    "Jude": ["jude", "judas", "jud"],
    "Revelation": ["revelation", "rev", "åpenbaringen", "åp"],
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_search_text(value: str) -> str:
    text = (value or "").lower()
    text = re.sub(r"[.,;:!?()[\]{}«»\"“”'`´]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_verse_text(value: str) -> str:
    text = value or ""

    # pysword usually cleans OSIS, but keep a defensive cleanup.
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def find_source_zip() -> Path:
    for candidate in SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate

    print("ERROR: Could not find source ZIP.")
    print("Looked for:")
    for candidate in SOURCE_CANDIDATES:
        print(f"  {candidate.relative_to(ROOT)}")
    sys.exit(1)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_first_working_book_key(bible, english_name: str) -> str | None:
    candidates = BOOK_KEY_CANDIDATES.get(english_name, [english_name.lower()])

    for key in candidates:
        try:
            text = bible.get(books=[key], chapters=[1], verses=[1])
            if clean_verse_text(text):
                return key
        except Exception:
            continue

    return None


def read_verse(bible, book_key: str, chapter: int, verse: int) -> str:
    try:
        return clean_verse_text(bible.get(
            books=[book_key],
            chapters=[chapter],
            verses=[verse]
        ))
    except Exception:
        return ""


def read_book_verses(bible, book_no: int, english_name: str, abbr: str, norwegian_name: str, chapter_count: int):
    book_key = get_first_working_book_key(bible, english_name)

    if not book_key:
        print(f"WARNING: Could not find book key for {english_name}")
        return [], None

    print(f"{book_no:02d}. {norwegian_name}: using key '{book_key}'")

    verses = []

    for chapter in range(1, chapter_count + 1):
        empty_run = 0

        # KJV has no chapter with more than 176 verses. 200 is a safe upper bound.
        for verse in range(1, 201):
            text = read_verse(bible, book_key, chapter, verse)

            if not text:
                empty_run += 1
                if empty_run >= 5 and verse > 5:
                    break
                continue

            empty_run = 0
            reference = f"{norwegian_name} {chapter},{verse}"
            verse_id = f"{book_no:02d}-{chapter:03d}-{verse:03d}"

            verses.append({
                "id": verse_id,
                "book": norwegian_name,
                "bookEnglish": english_name,
                "bookAbbr": abbr,
                "bookNo": book_no,
                "chapter": chapter,
                "verse": verse,
                "reference": reference,
                "text": text,
                "normalizedText": normalize_search_text(text),
                "source": "CrossWire SWORD Norsk 2.0"
            })

    return verses, book_key


def build_passages(verses, max_window=3):
    passages = []

    by_chapter = {}
    for verse in verses:
        key = (verse["bookNo"], verse["chapter"])
        by_chapter.setdefault(key, []).append(verse)

    for chapter_verses in by_chapter.values():
        chapter_verses.sort(key=lambda row: row["verse"])

        for i, first in enumerate(chapter_verses):
            for window in range(1, max_window + 1):
                selected = chapter_verses[i:i + window]

                if len(selected) != window:
                    continue

                last = selected[-1]
                if window == 1:
                    reference = first["reference"]
                else:
                    reference = f'{first["book"]} {first["chapter"]},{first["verse"]}-{last["verse"]}'

                text = " ".join(row["text"] for row in selected)

                passages.append({
                    "id": f'{first["id"]}-w{window}',
                    "reference": reference,
                    "book": first["book"],
                    "bookNo": first["bookNo"],
                    "chapter": first["chapter"],
                    "verseFrom": first["verse"],
                    "verseTo": last["verse"],
                    "window": window,
                    "text": text,
                    "normalizedText": normalize_search_text(text),
                    "source": "CrossWire SWORD Norsk 2.0"
                })

    return passages


def build_search_index(passages):
    index = []

    for item in passages:
        index.append({
            "id": item["id"],
            "reference": item["reference"],
            "book": item["book"],
            "bookNo": item["bookNo"],
            "chapter": item["chapter"],
            "verseFrom": item["verseFrom"],
            "verseTo": item["verseTo"],
            "window": item["window"],
            "text": item["text"],
            "normalizedText": item["normalizedText"],
        })

    return index


def main():
    source_zip = find_source_zip()
    OUT_NORMALIZED.mkdir(parents=True, exist_ok=True)
    OUT_INDEX.mkdir(parents=True, exist_ok=True)

    print(f"Source ZIP: {source_zip.relative_to(ROOT)}")
    print("Loading SWORD module with pysword...")

    modules = SwordModules(str(source_zip))
    found_modules = modules.parse_modules()

    if "Norsk" not in found_modules:
        print("ERROR: Module 'Norsk' not found in ZIP.")
        print("Found modules:", ", ".join(found_modules.keys()))
        sys.exit(1)

    bible = modules.get_bible_from_module("Norsk")

    books = []
    verses = []
    key_map = {}

    for book_no, (english_name, abbr, norwegian_name, chapter_count) in enumerate(BOOKS, start=1):
        book_verses, book_key = read_book_verses(
            bible=bible,
            book_no=book_no,
            english_name=english_name,
            abbr=abbr,
            norwegian_name=norwegian_name,
            chapter_count=chapter_count
        )

        if book_key:
            key_map[english_name] = book_key

        books.append({
            "bookNo": book_no,
            "book": norwegian_name,
            "bookEnglish": english_name,
            "bookAbbr": abbr,
            "chapters": chapter_count,
            "importedVerses": len(book_verses),
            "swordKey": book_key
        })

        verses.extend(book_verses)

    if len(verses) < 31000:
        print(f"WARNING: Only imported {len(verses)} verses. Expected about 31,100 for KJV versification.")

    passages = build_passages(verses, max_window=3)
    search_index = build_search_index(passages)

    (OUT_NORMALIZED / "nb-1930-books.json").write_text(
        json.dumps(books, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (OUT_NORMALIZED / "nb-1930-verses.json").write_text(
        json.dumps(verses, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (OUT_NORMALIZED / "nb-1930-passages.json").write_text(
        json.dumps(passages, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (OUT_INDEX / "nb-1930-search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    manifest = {
        "sourceName": "CrossWire SWORD module Norsk",
        "moduleName": "Norsk",
        "bookName": "Bibelen på Norsk (1930)",
        "downloadUrl": "https://www.crosswire.org/sword/servlet/SwordMod.Verify?modName=Norsk&pkgType=raw",
        "moduleInfoUrl": "https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=Norsk",
        "sourceFile": str(source_zip.relative_to(ROOT)).replace("\\", "/"),
        "sourceSha256": file_sha256(source_zip),
        "importedAtUtc": datetime.now(timezone.utc).isoformat(),
        "moduleVersion": "2.0",
        "swordVersionDate": "2020-02-08",
        "licenseStatedByCrossWire": "Public Domain",
        "verseCount": len(verses),
        "passageCount": len(passages),
        "bookKeyMap": key_map
    }

    OUT_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("")
    print("Done.")
    print(f"Books:    {len(books)}")
    print(f"Verses:   {len(verses)}")
    print(f"Passages: {len(passages)}")
    print("")
    print("Generated:")
    print("  data/normalized/nb-1930-books.json")
    print("  data/normalized/nb-1930-verses.json")
    print("  data/normalized/nb-1930-passages.json")
    print("  data/index/nb-1930-search-index.json")
    print("  data/source-manifest.json")


if __name__ == "__main__":
    main()
