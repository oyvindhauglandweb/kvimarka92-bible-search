import {
  normalizeNorwegianBibleText,
  expandNorwegianBibleVariants,
  tokenize
} from "./normalize.js";

const STOPWORDS = new Set([
  "at", "av", "de", "den", "det", "der", "du",
  "en", "er", "et", "for", "fra", "han", "ham", "har", "hun", "hva",
  "i", "jeg", "og", "om", "på", "seg", "som",
  "var", "ved", "vi", "vil", "å"
]);

const KEEP_TOKENS = new Set([
  "ikke",
  "med",
  "til",
  "deg",
  "meg",
  "dere",
  "deres"
]);

const TOKEN_VARIANTS = {
  "meg": ["meg", "mig"],
  "mig": ["mig", "meg"],
  "deg": ["deg", "dig"],
  "dig": ["dig", "deg"],
  "dere": ["dere", "eder", "i"],
  "eder": ["eder", "dere", "i"],
  "deres": ["deres", "eders"],
  "eders": ["eders", "deres"],
  "ikke": ["ikke", "ei"],
  "ei": ["ei", "ikke"],
  "hvem": ["hvem", "hvo"],
  "hvo": ["hvo", "hvem"],

  "alt": ["alt", "all", "alle", "ting"],
  "all": ["all", "alt", "alle"],
  "alle": ["alle", "all", "alt"],
  "virker": ["virker", "virke", "tjener", "tjene"],
  "virke": ["virke", "virker", "tjener", "tjene"],
  "sammen": ["sammen", "samvirker", "tjener"],
  "gode": ["gode", "godt"],
  "godt": ["godt", "gode"],

  "sorg": ["sorg", "bekymring", "bekymringer"],
  "sorgen": ["sorgen", "sorg", "bekymringen"],
  "bekymring": ["bekymring", "sorg"],
  "bekymringer": ["bekymringer", "sorg"],

  "strever": ["strever", "arbeider", "trettes"],
  "tungt": ["tungt", "byrder"],
  "bære": ["bære", "barer", "byrder"]
};

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function getQueryTokenGroups(query) {
  const rawTokens = tokenize(query);

  return rawTokens
    .filter(token => {
      if (KEEP_TOKENS.has(token)) return true;
      return !STOPWORDS.has(token);
    })
    .map(token => unique([token, ...(TOKEN_VARIANTS[token] || [])]))
    .filter(group => group.length);
}

function normalizedIncludesAny(normalizedText, variants) {
  return variants.some(token => normalizedText.includes(token));
}

function findFirstIndex(normalizedText, variants, startIndex = 0) {
  let best = -1;

  for (const token of variants) {
    const index = normalizedText.indexOf(token, startIndex);

    if (index >= 0 && (best === -1 || index < best)) {
      best = index;
    }
  }

  return best;
}

function countGroupMatches(groups, normalizedText) {
  let count = 0;

  for (const group of groups) {
    if (normalizedIncludesAny(normalizedText, group)) {
      count += 1;
    }
  }

  return count;
}

function phraseScore(queryVariants, normalizedText) {
  for (const query of queryVariants) {
    if (query && normalizedText.includes(query)) {
      return 120;
    }
  }

  return 0;
}

function coverageScore(groups, normalizedText) {
  if (!groups.length) return 0;

  const matches = countGroupMatches(groups, normalizedText);
  return Math.round((matches / groups.length) * 100);
}

function orderScore(groups, normalizedText) {
  if (groups.length < 2) return 0;

  let lastIndex = -1;
  let orderedMatches = 0;

  for (const group of groups) {
    const index = findFirstIndex(normalizedText, group, lastIndex + 1);

    if (index === -1) {
      continue;
    }

    orderedMatches += 1;
    lastIndex = index;
  }

  if (orderedMatches < 2) return 0;

  return Math.round((orderedMatches / groups.length) * 30);
}

function windowScore(verse) {
  const window = Number(verse.window || 1);

  if (window <= 1) return 35;
  if (window === 2) return 8;
  return 0;
}

function lengthPenalty(text) {
  const length = String(text || "").length;

  if (length < 180) return 0;
  return Math.min(20, Math.round((length - 180) / 80));
}

function queryContainsAll(normalizedQuery, words) {
  return words.every(word => normalizedQuery.includes(word));
}

function referenceBoostScore(query, verse) {
  const normalizedQuery = normalizeNorwegianBibleText(query);
  const reference = String(verse?.reference || "");

  const boosts = [
    {
      words: ["frykt", "ikke", "med"],
      references: {
        "Jesaja 41,10": 80,
        "5 Mosebok 31,6": 35,
        "Josva 1,9": 35
      }
    },
    {
      words: ["kast", "sorg"],
      references: {
        "1 Peter 5,7": 90
      }
    },
    {
      words: ["kom", "alle", "strever"],
      references: {
        "Matteus 11,28": 90
      }
    },
    {
      words: ["alle", "ting", "gode"],
      references: {
        "Romerne 8,28": 90
      }
    },
    {
      words: ["alt", "virker", "gode"],
      references: {
        "Romerne 8,28": 90
      }
    }
  ];

  let score = 0;

  for (const boost of boosts) {
    if (!queryContainsAll(normalizedQuery, boost.words)) {
      continue;
    }

    for (const [boostReference, boostScore] of Object.entries(boost.references)) {
      if (reference === boostReference || reference.startsWith(`${boostReference}-`)) {
        score += boostScore;
      }
    }
  }

  return score;
}

function makeSnippet(text, groups) {
  const source = String(text || "");
  if (!source) return "";

  const normalizedSource = normalizeNorwegianBibleText(source);
  let bestIndex = 0;

  for (const group of groups) {
    const index = findFirstIndex(normalizedSource, group);

    if (index >= 0) {
      bestIndex = Math.max(0, index - 55);
      break;
    }
  }

  const snippet = source.slice(bestIndex, bestIndex + 220).trim();
  return bestIndex > 0 ? `…${snippet}` : snippet;
}

function resultDedupeKey(result) {
  const verse = result.verse || {};

  return [
    verse.bookNo || verse.book || "",
    verse.chapter || "",
    verse.verseFrom || verse.verse || "",
    verse.verseTo || verse.verse || ""
  ].join(":");
}

function overlapGroupKey(result) {
  const verse = result.verse || {};

  return [
    verse.bookNo || verse.book || "",
    verse.chapter || "",
    verse.verseFrom || verse.verse || ""
  ].join(":");
}

function rangesOverlap(aFrom, aTo, bFrom, bTo) {
  return Number(aFrom) <= Number(bTo) && Number(bFrom) <= Number(aTo);
}

function removeRedundantWindows(results) {
  const singleVerseResults = results.filter(result => Number(result.verse?.window || 1) === 1);

  return results.filter(result => {
    const verse = result.verse || {};
    const window = Number(verse.window || 1);

    if (window <= 1) {
      return true;
    }

    const from = Number(verse.verseFrom || verse.verse || 0);
    const to = Number(verse.verseTo || verse.verse || from);

    const overlappingSingle = singleVerseResults.find(single => {
      const singleVerse = single.verse || {};

      if (String(singleVerse.bookNo || singleVerse.book) !== String(verse.bookNo || verse.book)) {
        return false;
      }

      if (String(singleVerse.chapter) !== String(verse.chapter)) {
        return false;
      }

      const singleFrom = Number(singleVerse.verseFrom || singleVerse.verse || 0);
      const singleTo = Number(singleVerse.verseTo || singleVerse.verse || singleFrom);

      return rangesOverlap(from, to, singleFrom, singleTo) && single.score >= result.score - 20;
    });

    return !overlappingSingle;
  });
}

function dedupeResults(results) {
  const exactSeen = new Set();
  const overlapBest = new Map();

  const cleanedResults = removeRedundantWindows(results);

  for (const result of cleanedResults) {
    const exactKey = resultDedupeKey(result);

    if (exactSeen.has(exactKey)) {
      continue;
    }

    exactSeen.add(exactKey);

    const overlapKey = overlapGroupKey(result);
    const existing = overlapBest.get(overlapKey);

    if (!existing || result.score > existing.score) {
      overlapBest.set(overlapKey, result);
    }
  }

  return [...overlapBest.values()]
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;

      const aw = Number(a.verse?.window || 1);
      const bw = Number(b.verse?.window || 1);
      if (aw !== bw) return aw - bw;

      return String(a.reference).localeCompare(String(b.reference), "no");
    });
}

export function searchBibleVerses(query, verses, options = {}) {
  const limit = Number(options.limit || 10);
  const queryVariants = expandNorwegianBibleVariants(query);
  const groups = getQueryTokenGroups(query);

  if (!groups.length) return [];

  const minCoverage =
    groups.length <= 2 ? 1 : Math.max(2, Math.ceil(groups.length * 0.45));

  const scored = verses
    .map(verse => {
      const normalizedText =
        verse.normalizedText || normalizeNorwegianBibleText(verse.text);

      const groupMatches = countGroupMatches(groups, normalizedText);

      if (groupMatches < minCoverage) {
        return null;
      }

      const score =
        phraseScore(queryVariants, normalizedText) +
        coverageScore(groups, normalizedText) +
        orderScore(groups, normalizedText) +
        windowScore(verse) +
        referenceBoostScore(query, verse) -
        lengthPenalty(verse.text);

      return {
        reference: verse.reference,
        score,
        matches: groupMatches,
        snippet: makeSnippet(verse.text, groups),
        verse
      };
    })
    .filter(Boolean)
    .filter(result => result.score > 0)
    .sort((a, b) => b.score - a.score);

  return dedupeResults(scored).slice(0, limit);
}
