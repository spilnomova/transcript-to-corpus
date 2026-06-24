import streamlit as st
import pandas as pd
import numpy
import tokenize_uk
from collections import Counter
from src.lang_id import *
from src.parse_pm3 import *
from src.utils import *

# The Browser App

st.title("Перетворення стенограми у корпус мовлення дитини")

uploaded = st.file_uploader("Завантажте вхідну табличку, яка містить колонки" +
                            " \"Хто говорить\" і \"Стенограма\":", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    st.write("Завантажив табличку.")

    if "Хто говорить" not in df.columns or "Стенограма" not in df.columns:
        st.error("ПОМИЛКА: Формат таблиці некоректний. Перевірте наявність" +
                 " колонок \"Хто говорить\" і \"Стенограма\".")
        
    elif not (df["Хто говорить"] == "Дитина").any():
        st.error("ПОМИЛКА: Перевірте наявність рядків \"Дитина\" у колонці" +
                 " \"Хто говорить\".")
        
    else:
        transcript_list = df[df["Хто говорить"]=="Дитина"]["Стенограма"].to_list()
        transcript_list = [i for i in transcript_list if isinstance(i, str)]
        transcript = " ".join(transcript_list)
    
        st.write("Прочитав стенограму.")
        st.write("Працюю :)")

        # Full parse of the transcript
    
        transcript_tok = [w for w in tokenize_uk.tokenize_words(transcript)
                          if w.isalpha()]
        transcript_tok_lower = [t.lower().replace("ʼ", "'")
                                for t in transcript_tok]
        transcript_tok_morph = [get_morph(w) for w in transcript_tok_lower]
        transcript_tok_lemma = [get_lemma(m) for m in transcript_tok_morph]
        transcript_tok_pos = [get_pos(m) for m in transcript_tok_morph]
    
        df_out = pd.DataFrame({
            'id_': range(1, len(transcript_tok) + 1),
            'слово_': transcript_tok,
            'слово_з_малої': transcript_tok_lower,
            'лема': transcript_tok_lemma,
            'частина мови': transcript_tok_pos
        })
    
        df_out_sorted = df_out.sort_values(by='лема',
                                           key=lambda s: s.map(sort_ua))
        df_out_sorted.insert(0, "id", df_out['id_'].tolist())
        df_out_sorted.insert(1, "слово", df_out['слово_'].tolist())
        df_out_sorted.insert(2, "_", [numpy.nan] * len(transcript_tok))
    
        csv_full = df_out_sorted.to_csv(
            sep=';',
            index=False,
            encoding="utf-8-sig"
        )
    
        st.write("Ще трішки!")
    
        # Statistics and language analysis
        
        word_forms, lang_ids = dict(), dict()
        lemma_cur = ""
        for word, lemma, pos in zip(df_out_sorted['слово_з_малої'],
                                    df_out_sorted['лема'],
                                    df_out_sorted['частина мови']):
            if lemma == lemma_cur:
                word_forms[lemma].add(word)
            else:
                word_forms[lemma] = {word}
                lang_ids[lemma] = language(lemma, pos)
                lemma_cur = lemma
    
        freqs = Counter(df_out_sorted['лема'])
        lemmas = sorted(freqs.keys(), key=lambda x: sort_ua(x))
        df_out_stats = pd.DataFrame({
            "лема": lemmas,
            "словоформи": [", ".join(word_forms[lemma]) for lemma in lemmas],
            "частотність": [freqs[lemma] for lemma in lemmas],
            "українське": [lang_ids[lemma]["ua"] for lemma in lemmas],
            "неукраїнське": [lang_ids[lemma]["non-ua"] for lemma in lemmas],
            "питомо українське": [lang_ids[lemma]["only-ua"] for lemma in lemmas]
        })
    
        csv_stats = df_out_stats.to_csv(
            sep=';',
            index=False,
            encoding="utf-8-sig"
        )
    
        st.write("Готово! Забирай і перевіряй!")
    
        st.download_button(
            "Завантажити корпус",
            csv_stats,
            "Корпус_" + uploaded.name,
            "text/csv"
        )
        st.download_button(
            "Завантажити повний розбір",
            csv_full,
            "Розбір_" + uploaded.name,
            "text/csv"
        )
