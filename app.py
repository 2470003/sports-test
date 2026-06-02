import streamlit as st
import pandas as pd

st.title("CSV 自動分析アプリ（データプレビュー版）")
st.write("CSV の中身が分からなくても、まずはデータを確認できます。")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    # 2行目が単位行などの場合 → 自動削除
    if df.iloc[0].astype(str).str.contains("cm|秒|m/s|%").any():
        df = df.drop(index=0).reset_index(drop=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

else:
    st.info("CSV ファイルをアップロードしてください。")
