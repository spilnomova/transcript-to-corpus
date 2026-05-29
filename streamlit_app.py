import streamlit as st
import pandas as pd

st.title("CSV Annotation Tool")

uploaded = st.file_uploader("Upload CSV", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    # your processing here
    df["processed"] = True

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Result",
        csv,
        "result.csv",
        "text/csv"
    )
