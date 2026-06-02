import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("CSV 自動分析アプリ（汎用版）")
st.write("CSV の中身が分からなくても、自動で分析できるアプリです。")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    # 2行目が単位行などの場合 → 自動削除
    if df.iloc[0].astype(str).str.contains("cm|秒|m/s|%").any():
        df = df.drop(index=0).reset_index(drop=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    # 数値列とカテゴリ列を自動判定
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    object_cols = df.select_dtypes(include="object").columns.tolist()

    st.write("検出された数値列:", numeric_cols)
    st.write("検出されたカテゴリ列:", object_cols)

    # ====== 基本統計量 ======
    if len(numeric_cols) > 0:
        st.subheader("② 数値列の基本統計量")
        st.dataframe(df[numeric_cols].describe())

    # ====== 散布図（ユーザーが列を選択） ======
    if len(numeric_cols) >= 2:
        st.subheader("③ 散布図（任意の2列）")
        x_col = st.selectbox("X軸を選択", numeric_cols)
        y_col = st.selectbox("Y軸を選択", numeric_cols, index=1)

        fig, ax = plt.subplots()
        ax.scatter(df[x_col], df[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        st.pyplot(fig)

    # ====== ヒストグラム ======
    if len(numeric_cols) > 0:
        st.subheader("④ ヒストグラム（任意の1列）")
        hist_col = st.selectbox("ヒストグラムの列を選択", numeric_cols)

        fig2, ax2 = plt.subplots()
        ax2.hist(df[hist_col], bins=20)
        ax2.set_xlabel(hist_col)
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

    # ====== カテゴリ列の集計 ======
    if len(object_cols) > 0:
        st.subheader("⑤ カテゴリ列の集計")
        cat_col = st.selectbox("集計するカテゴリ列を選択", object_cols)

        st.write(df[cat_col].value_counts())

else:
    st.info("CSV ファイルをアップロードしてください。")
