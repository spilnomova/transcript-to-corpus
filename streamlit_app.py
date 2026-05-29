import streamlit as st
import pandas as pd
import numpy
import tokenize_uk
import pymorphy3

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
    transcript_tok_lang = [language(lemma, pos) for lemma, pos in zip(transcript_tok_lemma, transcript_tok_pos)]

    df_out = pd.DataFrame({
        'слово': transcript_tok,
        'слово_з_малої': transcript_tok_lower,
        'лема': [m.normal_form for m in transcript_tok_morph],
        'частина мови': [get_pos(m) for m in transcript_tok_morph],
        'українське': [l[0] for l in transcript_tok_lang],
        'неукраїнське': [l[1] for l in transcript_tok_lang]
    })

    st.write("Готово! Забирай і перевіряй!")

    csv = df_out.to_csv(index=False)

    st.download_button(
        "Завантажити результат",
        csv,
        "result.csv",
        "text/csv"
    )
