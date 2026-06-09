import streamlit as st
import pandas as pd
import numpy as np

st.title("種目別 上位/下位 表示アプリ")
st.write("種目を選ぶと、上位10人または下位10人を表示できます。")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    # 2行目（単位行）をスキップして読み込み
    df = pd.read_csv(uploaded, skiprows=[1])

    # 1列目をインデックスに設定（ID）
    df.set_index(df.columns[0], inplace=True)

    # ID の .0 を消す
    df.index = df.index.astype(str).str.replace(r"\.0$", "", regex=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    # 数値列（種目）
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # 0 を除外（NaN に置換）
    df[numeric_cols] = df[numeric_cols].replace(0, np.nan)

    # 性別列があるか確認
    has_gender = "性別" in df.columns

    st.subheader("② 表示対象を選択")
    if has_gender:
        gender_option = st.radio("対象を選んでください", ["総合", "男", "女"])

        if gender_option == "男":
            df_filtered = df[df["性別"] == "男"]
        elif gender_option == "女":
            df_filtered = df[df["性別"] == "女"]
        else:
            df_filtered = df
    else:
        st.info("性別列がないため総合のみ表示します。")
        df_filtered = df

    # 種目選択
    st.subheader("③ 種目を選択")
    target_col = st.selectbox("種目を選んでください", numeric_cols)

    # 上位/下位切り替え
    st.subheader("④ 上位/下位を選択")
    order_option = st.radio("並び順", ["上位10人", "下位10人"])

    ascending_flag = True if order_option == "下位10人" else False

    # 並び替え
    df_sorted = df_filtered.sort_values(by=target_col, ascending=ascending_flag)

    # 上位 or 下位 10人を表示
    st.subheader("⑤ 結果表示")
    st.dataframe(df_sorted[[target_col]].head(10))

else:
    st.info("CSV ファイルをアップロードしてください。")
