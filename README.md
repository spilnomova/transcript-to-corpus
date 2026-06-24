# Transcript to corpus

## High-Level Description

This is a Streamlit app that reads a transcribed interview with a child based in Ukraine, extracts the child's lines, and processes them in the following way:
- splits into tokens;
- filters out punctuation;
- extracts each word's part of speech and lemma;
- assigns a score: 1 for notional parts of speech and 0.3 for functional parts of speech;
- identifies whether the word is in Ukrainian;
- identifies whether the Ukrainian word is a cognate of russian;
- outputs two csv files: an annotated frequency distribution of lemmas in the child's speech and a full log of the analysis.

The input csv is expected to have columns "Хто говорить" and "Стенограма". The lines with what the child says should be labelled as "Дитина" in the "Хто говорить" column.

## Dictionaries Used

The Ukrainian-russian dictionary used to detect potential cognates is made of:
- [wiktionary-ua2ru.json](dict/wiktionary-ua2ru.json), parsed from the dump of the Ukrainian Wiktionary (see [parse_wiktionary.ipynb](scripts/parse_wiktionary.ipynb));
- [custom-ua2ru.json](dict/custom-ua2ru.json), compiled semi-manually from the translations missing from Wiktionary, translated by DeepL, and verified manually.

The list of Ukrainian words [vesum.txt](dict/vesum.txt) was extracted from the VESUM dictionary at https://github.com/brown-uk/dict_uk.
