# Transcript to corpus

This is a Streamlit app that reads a transcribed interview with a child based in Ukraine, extracts the child's lines, and processes them in the following way:
- splits into tokens;
- filters out punctuation;
- extracts each word's part of speech and lemma;
- assigns a score: 1 for notional parts of speech and 0.3 for functional parts of speech;
- identifies whether the word is in Ukrainian;
- outputs two csv files: an annotated frequency distribution of lemmas in the child's speech and a full log of the analysis.

The input csv is expected to have columns "Хто говорить" and "Стенограма". The lines with what the child says should be labelled as "Дитина" in the "Хто говорить" column.
