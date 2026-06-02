import streamlit as st
import pandas as pd

st.title("CSV 自動分析アプリ（順位表示版）")
st.write("CSV の中身が分からなくても、自動で表示できるアプリです。")

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

    # 数値列の0をNaNに置き換え（0は無効データとして扱う）
    df[numeric_cols] = df[numeric_cols].replace(0, pd.NA)

    st.subheader("② 項目を選んで順位を表示")

    # 項目選択（数値列のみ）
    target_col = st.selectbox("競技（項目）を選択", numeric_cols)

    # 性別フィルタ
    has_gender = "性別" in df.columns
    if has_gender:
        gender_option = st.radio("表示対象", ["全体", "男", "女"])
        if gender_option == "男":
            df_filtered = df[df["性別"] == "男"]
        elif gender_option == "女":
            df_filtered = df[df["性別"] == "女"]
        else:
            df_filtered = df
    else:
        st.info("性別列がないため、全体のみ表示します。")
        df_filtered = df

    # 上位 or 下位 の切り替え
    order_option = st.radio("順位の種類", ["上位", "下位"])

    # 並び替え（上位＝降順、下位＝昇順）
    ascending_flag = True if order_option == "下位" else False
    df_filtered = df_filtered.sort_values(by=target_col, ascending=ascending_flag)

    # 上位/下位10人を表示（タイトルは表示しない）
    st.dataframe(df_filtered.head(10))

    # 11位以下の表示切り替え
    if st.checkbox("10位以下を表示する"):
        st.dataframe(df_filtered.iloc[10:])

else:
    st.info("CSV ファイルをアップロードしてください。")

