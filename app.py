import streamlit as st
import pandas as pd

st.title("CSV 自動分析アプリ（並び替え版）")
st.write("CSV の中身が分からなくても、自動で並び替えて表示できるアプリです。")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    # 2行目が単位行などの場合 → 自動削除
    if df.iloc[0].astype(str).str.contains("cm|秒|m/s|%").any():
        df = df.drop(index=0).reset_index(drop=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    # 数値列を抽出
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # 数値列の0をNaNに置き換え
    df[numeric_cols] = df[numeric_cols].replace(0, pd.NA)

    # 性別列があるか確認
    has_gender = "性別" in df.columns

    st.subheader("② 並び替え設定")

    # 並び替え対象の項目（数値列）を選択
    sort_col = st.selectbox("並び替える項目を選択してください", numeric_cols)

    # 上位 or 下位 の切り替え
    order_option = st.radio("並び順", ["上位（大きい順）", "下位（小さい順）"])
    ascending_flag = True if order_option == "下位（小さい順）" else False

    # 並び替え
    df_sorted = df.sort_values(by=sort_col, ascending=ascending_flag)

    # 表示する列を限定
    display_cols = ["ID"]
    if has_gender:
        display_cols.append("性別")
    display_cols.append(sort_col)

    st.subheader("③ 並び替え結果")
    st.dataframe(df_sorted[display_cols])

else:
    st.info("CSV ファイルをアップロードしてください。")
