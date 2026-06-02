import streamlit as st
import pandas as pd

st.title("CSV 自動分析アプリ（種目別順位表示版）")
st.write("競技（種目）を選ぶだけで、ID・性別・成績の順位を表示できます。")

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

    # ① 種目（数値列）を選択
    st.subheader("② 種目を選択")
    target_col = st.selectbox("競技（項目）を選択してください", numeric_cols)

    # ② 性別フィルタ
    st.subheader("③ 表示対象を選択")
    if has_gender:
        gender_option = st.radio("対象", ["全体", "男", "女"])
        if gender_option == "男":
            df_filtered = df[df["性別"] == "男"]
        elif gender_option == "女":
            df_filtered = df[df["性別"] == "女"]
        else:
            df_filtered = df
    else:
        st.info("性別列がないため、全体のみ表示します。")
        df_filtered = df

    # ③ 上位 or 下位 の切り替え
    order_option = st.radio("順位の種類", ["上位", "下位"])
    ascending_flag = True if order_option == "下位" else False

    # 並び替え
    df_filtered = df_filtered.sort_values(by=target_col, ascending=ascending_flag)

    # 表示する列を3つに限定
    display_cols = ["ID"]
    if has_gender:
        display_cols.append("性別")
    display_cols.append(target_col)

    # 上位/下位10人を表示（タイトルは表示しない）
    st.subheader("④ 順位表")
    st.dataframe(df_filtered[display_cols].head(10))

    # 11位以下の表示切り替え
    if st.checkbox("10位以下を表示する"):
        st.dataframe(df_filtered[display_cols].iloc[10:])

else:
    st.info("CSV ファイルをアップロードしてください。")
