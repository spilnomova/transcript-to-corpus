import streamlit as st
import pandas as pd
import numpy
import tokenize_uk
import pymorphy3
from collections import Counter

# Global variables

morph = pymorphy3.MorphAnalyzer(lang="uk")

VESUM = set()
with open("dict/vesum.txt", "r") as f:
    for line in f.readlines():
        VESUM.add(line.strip())

FUNCTIONAL = {"PREP", "CONJ", "PRCL", "INTJ"}

# Pre-processing with pymorphy3

def get_morph(word):
    morphs = morph.parse(word)
    for i in range(len(morphs)):
        if morphs[i].tag.POS in {"NPRO", "PREP", "NUMR"} or \
            morphs[i].normal_form in {"бути", "хотіти", "людина"}:
            return morphs[i]
    return morphs[0]

def get_lemma(word_morph):
    if word_morph.word == "можна":
        return "можна"
    elif word_morph.word == "зуби":
        return "зуб"
    elif word_morph.word == "окуляри":
        return "окуляри"
    else:
        return word_morph.normal_form

def get_pos(word_morph):
    if word_morph.tag.POS == None:
        return "UNKN"
    elif word_morph.word == "ще":
        return "NPRO"
    else:
        return word_morph.tag.POS

def language(lemma, pos):
    if lemma == "ще":
        return (1, numpy.nan)
    if pos in {None, "UNKN"} or lemma == "носок":
        return (numpy.nan, 1)
    score = 1
    if pos in FUNCTIONAL or lemma in {"ні", "так", "нє", "нєт", "да"}:
        score = 0.3
    if lemma in VESUM:
        return (score, numpy.nan)
    else:
        return (numpy.nan, score)

# The Browser App

st.title("Перетворення стенограми у корпус мовлення дитини")

uploaded = st.file_uploader("Завантажити вхідну табличку", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    st.write("Завантажив табличку.")
    st.write("Працюю :)")

    transcript_list = df[df["Хто говорить"]=="Дитина"]["Стенограма"].to_list()
    transcript = " ".join(transcript_list)

    st.write("Прочитав стенограму.")
    st.write("Ще трішки!")

    transcript_tok = [w for w in tokenize_uk.tokenize_words(transcript) if w.isalpha()]
    transcript_tok_lower = [t.lower().replace("ʼ", "'") for t in transcript_tok]
    transcript_tok_morph = [get_morph(w) for w in transcript_tok_lower]
    transcript_tok_lemma = [get_lemma(m) for m in transcript_tok_morph]
    transcript_tok_pos = [get_pos(m) for m in transcript_tok_morph]

    df_out = pd.DataFrame({
        'id_': range(1, len(transcript_tok) + 1),
        'слово_': transcript_tok,
        'слово_з_малої': transcript_tok_lower,
        'лема': [m.normal_form for m in transcript_tok_morph],
        'частина мови': [get_pos(m) for m in transcript_tok_morph]
    })

    df_out_sorted = df_out.sort_values(by='лема')

    transcript_tok_lang = []
    lemma_cur = ""
    for lemma, pos in zip(df_out_sorted['лема'], df_out_sorted['частина мови']):
        if lemma == lemma_cur:
            transcript_tok_lang.append((numpy.nan, numpy.nan))
        else:
            transcript_tok_lang.append(language(lemma, pos))
            lemma_cur = lemma

    df_out_sorted.insert(0, "id", df_out['id_'].tolist())
    df_out_sorted.insert(1, "слово", df_out['слово_'].tolist())
    df_out_sorted.insert(2, "_", [numpy.nan] * len(transcript_tok))
    df_out_sorted['українське'] = [l[0] for l in transcript_tok_lang]
    df_out_sorted['неукраїнське'] = [l[1] for l in transcript_tok_lang]

    csv_1 = df_out_sorted.to_csv(
        sep=';',
        index=False,
        encoding="utf-8-sig"
    )

    df_for_freq = df_out_sorted[['лема', 'українське', 'неукраїнське']]
    df_out_stats = df_for_freq[~numpy.isnan(df_for_freq['українське']) | ~numpy.isnan(df_for_freq['неукраїнське'])]
    freqs = Counter(df_for_freq['лема'])
    df_out_stats.insert(1, "частотність", [freqs[lemma] for lemma in df_out_stats['лема']])

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
