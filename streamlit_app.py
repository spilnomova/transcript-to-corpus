import streamlit as st
import pandas as pd
import numpy
import tokenize_uk
from collections import Counter
from aux.parse_pm3 import *
from aux.lang_id import *

# UA sorting

ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"

order = {c: i for i, c in enumerate(ALPHABET)}

def sort_ua(word):
    return [order.get(ch.lower(), 999) for ch in word]

# The Browser App

st.title("Перетворення стенограми у корпус мовлення дитини")

uploaded = st.file_uploader("Завантажте вхідну табличку, яка містить колонки" +
                            " \"Хто говорить\" і \"Стенограма\"", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    st.write("Завантажив табличку.")

    if "Хто говорить" not in df.columns or "Стенограма" not in df.columns:
        st.write("ПОМИЛКА: Формат таблиці некоректний. Перевірте наявність" +
                 " колонок \"Хто говорить\" і \"Стенограма\".")
        
    elif not (df["Хто говорить"] == "Дитина").any():
        st.write("ПОМИЛКА: Перевірте наявність рядків \"Дитина\" у колонці" +
                 " \"Хто говорить\".")
        
    else:
        transcript_list = df[df["Хто говорить"]=="Дитина"]["Стенограма"].to_list()
        transcript_list = [i for i in transcript_list if isinstance(i, str)]
        transcript = " ".join(transcript_list)
    
        st.write("Прочитав стенограму.")
        st.write("Працюю :)")
    
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
    
        transcript_tok_lang = []
        lemma_cur = ""
        for lemma, pos in zip(df_out_sorted['лема'],
                              df_out_sorted['частина мови']):
            if lemma == lemma_cur:
                transcript_tok_lang.append((numpy.nan, numpy.nan, numpy.nan))
            else:
                lang = language(lemma, pos)
                if not lang["ua"]:
                    transcript_tok_lang.append((numpy.nan, lang["score"],
                                                numpy.nan))
                elif lang["score"] == 0.3:
                    transcript_tok_lang.append((lang["score"], numpy.nan,
                                                numpy.nan))
                else:
                    cognate = related_to_ru(lemma)
                    transcript_tok_lang.append((lang["score"], numpy.nan,
                                                1.0 if cognate == False
                                                    else numpy.nan))
                lemma_cur = lemma
    
        st.write("Ще трішки!")
    
        df_out_sorted.insert(0, "id", df_out['id_'].tolist())
        df_out_sorted.insert(1, "слово", df_out['слово_'].tolist())
        df_out_sorted.insert(2, "_", [numpy.nan] * len(transcript_tok))
        df_out_sorted['українське'] = [l[0] for l in transcript_tok_lang]
        df_out_sorted['неукраїнське'] = [l[1] for l in transcript_tok_lang]
        df_out_sorted['питомо українське'] = [l[2] for l in transcript_tok_lang]
    
        csv_1 = df_out_sorted.to_csv(
            sep=';',
            index=False,
            encoding="utf-8-sig"
        )
    
        df_for_freq = df_out_sorted[['лема', 'українське', 'неукраїнське',
                                     'питомо українське']]
        df_out_stats = df_for_freq[~numpy.isnan(df_for_freq['українське']) |
                                   ~numpy.isnan(df_for_freq['неукраїнське'])]
        freqs = Counter(df_for_freq['лема'])
        df_out_stats.insert(1, "частотність",
                            [freqs[lemma] for lemma in df_out_stats['лема']])
    
        csv_2 = df_out_stats.to_csv(
            sep=';',
            index=False,
            encoding="utf-8-sig"
        )
    
        st.write("Готово! Забирай і перевіряй!")
    
        st.download_button(
            "Завантажити корпус",
            csv_2,
            "Корпус_" + uploaded.name,
            "text/csv"
        )
        st.download_button(
            "Завантажити повний розбір",
            csv_1,
            "Розбір_" + uploaded.name,
            "text/csv"
        )
