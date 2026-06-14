import {
  normalizeNorwegianBibleText,
  expandNorwegianBibleVariants,
  tokenize
} from "./normalize.js";

function countMatches(tokens, normalizedText) {
  let count = 0;
  for (const token of tokens) {
    if (normalizedText.includes(token)) count += 1;
  }
  return count;
}

function phraseScore(queryVariants, normalizedText) {
  for (const query of queryVariants) {
    if (query && normalizedText.includes(query)) return 100;
  }
  return 0;
}

function tokenScore(tokens, normalizedText) {
  if (!tokens.length) return 0;
  const matches = countMatches(tokens, normalizedText);
  return Math.round((matches / tokens.length) * 60);
}

function orderScore(tokens, normalizedText) {
  if (tokens.length < 2) return 0;
  let lastIndex = -1;
  for (const token of tokens) {
    const index = normalizedText.indexOf(token, lastIndex + 1);
    if (index === -1) return 0;
    lastIndex = index;
  }
  return 20;
}

function makeSnippet(text, tokens) {
  const source = String(text || "");
  if (!source) return "";

  const lower = normalizeNorwegianBibleText(source);
  let bestIndex = 0;

  for (const token of tokens) {
    const index = lower.indexOf(token);
    if (index >= 0) {
      bestIndex = Math.max(0, index - 45);
      break;
    }
  }

  const snippet = source.slice(bestIndex, bestIndex + 180).trim();
  return bestIndex > 0 ? `…${snippet}` : snippet;
}

export function searchBibleVerses(query, verses, options = {}) {
  const limit = Number(options.limit || 10);
  const queryVariants = expandNorwegianBibleVariants(query);
  const tokens = tokenize(query);

  if (!tokens.length) return [];

  return verses
    .map(verse => {
      const normalizedText =
        verse.normalizedText || normalizeNorwegianBibleText(verse.text);

      const score =
        phraseScore(queryVariants, normalizedText) +
        tokenScore(tokens, normalizedText) +
        orderScore(tokens, normalizedText);

      return {
        reference: verse.reference,
        score,
        snippet: makeSnippet(verse.text, tokens),
        verse
      };
    })
    .filter(result => result.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
