import streamlit as st
import pandas as pd

st.title("CSV 自動分析アプリ（順位表示版）")
st.write("CSV の中身が分からなくても、自動で順位を表示できるアプリです。")

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

    # 性別列があるか確認
    has_gender = "性別" in df.columns

    st.subheader("② 項目を選んで順位を表示")

    # 項目選択（数値列のみ）
    target_col = st.selectbox("順位を表示する項目を選択", numeric_cols)

    # 性別フィルタ
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

    # 順位計算（大きい方が良いと仮定）
    df_filtered = df_filtered.sort_values(by=target_col, ascending=False)

    # 上位10人
    st.subheader("③ 上位10人")
    st.dataframe(df_filtered.head(10))

    # 11位以下の表示切り替え
    if st.checkbox("10位以下を表示する"):
        st.subheader("④ 10位以下")
        st.dataframe(df_filtered.iloc[10:])

else:
    st.info("CSV ファイルをアップロードしてください。")
