import fs from "node:fs";
import { searchBibleVerses } from "../src/search.js";

const indexPath = "data/index/nb-1930-search-index.json";

if (!fs.existsSync(indexPath)) {
  console.error(`Missing ${indexPath}`);
  console.error("Run first:");
  console.error("  py scripts/import-crosswire-norsk.py");
  process.exit(1);
}

const passages = JSON.parse(fs.readFileSync(indexPath, "utf8"));

console.log("Search engine v5 - curated quote boosts");

const queries = [
  "frykt ikke for jeg er med deg",
  "kast all deres sorg",
  "kom til meg alle som strever",
  "alt virker sammen til gode",
  "kom til mig alle I som strever",
  "alle ting tjener dem til gode"
];

for (const query of queries) {
  console.log("\nQUERY:", query);
  const results = searchBibleVerses(query, passages, { limit: 8 });

  for (const result of results) {
    console.log(`${String(result.score).padStart(3)}  ${result.reference}  ${result.snippet}`);
  }
}
