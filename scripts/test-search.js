import { searchBibleVerses } from "../src/search.js";
import { normalizeNorwegianBibleText } from "../src/normalize.js";

const sampleVerses = [
  {
    id: "isa-41-10",
    reference: "Jesaja 41,10",
    text: "Frykt ikke, for jeg er med dig; se dig ikke engstelig om, for jeg er din Gud."
  },
  {
    id: "1pet-5-7",
    reference: "1 Peter 5,7",
    text: "Og kast all eders sorg på ham! for han har omsorg for eder."
  },
  {
    id: "mat-11-28",
    reference: "Matteus 11,28",
    text: "Kom til mig, alle I som strever og har tungt å bære, og jeg vil gi eder hvile!"
  }
].map(verse => ({
  ...verse,
  normalizedText: normalizeNorwegianBibleText(verse.text)
}));

const queries = [
  "frykt ikke for jeg er med deg",
  "kast all deres sorg",
  "kom til meg alle som strever"
];

for (const query of queries) {
  console.log("\nQUERY:", query);
  const results = searchBibleVerses(query, sampleVerses);

  for (const result of results) {
    console.log(`${result.score}\t${result.reference}\t${result.snippet}`);
  }
}
