export function normalizeNorwegianBibleText(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFKC")
    .replace(/[.,;:!?()[\]{}«»"“”'`´]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function expandNorwegianBibleVariants(value) {
  const text = normalizeNorwegianBibleText(value);
  const variants = new Set([text]);

  const replacements = [
    ["meg", "mig"],
    ["deg", "dig"],
    ["dere", "eder"],
    ["deres", "eders"],
    ["ikke", "ei"],
    ["hvem", "hvo"],
    ["å", "aa"]
  ];

  for (const [modern, oldForm] of replacements) {
    if (text.includes(modern)) variants.add(text.replaceAll(modern, oldForm));
    if (text.includes(oldForm)) variants.add(text.replaceAll(oldForm, modern));
  }

  return [...variants];
}

export function tokenize(value) {
  return normalizeNorwegianBibleText(value)
    .split(" ")
    .map(token => token.trim())
    .filter(token => token.length >= 2);
}
