import streamlit as st
import pandas as pd
import numpy as np

st.title("個人スコア・順位表示アプリ")
st.write("ID を選ぶと、その人の全種目の順位を表示します。")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    # 2行目（単位行）をスキップして読み込み
    df = pd.read_csv(uploaded, skiprows=[1])

    # 1列目をインデックスに設定（ID）
    df.set_index(df.columns[0], inplace=True)

    # --- ID の .0 を消す（float → str） ---
    df.index = df.index.astype(str).str.replace(r"\.0$", "", regex=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    # --- 数値列（種目） ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # --- 0 を除外（NaN に置換） ---
    df[numeric_cols] = df[numeric_cols].replace(0, np.nan)

    # --- 性別列があるか確認 ---
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
        st.info("性別列がないため、総合のみ表示します。")
        df_filtered = df

    # --- ID 一覧（性別フィルタ後） ---
    id_list = df_filtered.index.tolist()

    st.subheader("③ ID を選択")
    selected_id = st.selectbox("ID を選んでください", id_list)

    # --- 個人データ ---
    st.subheader("④ 個人データ")
    st.dataframe(df.loc[[selected_id]])

    # --- 各種目の順位計算 ---
    st.subheader("⑤ 各種目の順位")

    result_list = []

    for col in numeric_cols:
        # 性別フィルタ後のデータで順位計算
        series = df_filtered[col].dropna()

        # 並び替え（大きい方が良いと仮定）
        sorted_series = series.sort_values(ascending=False)

        # 選んだ ID のスコア
        my_score = df.loc[selected_id, col]

        # スコアが NaN（0除外）ならスキップ
        if pd.isna(my_score):
            result_list.append([col, "データなし", "-", "-"])
            continue

        # 順位（1位から）
        rank = sorted_series.index.get_loc(selected_id) + 1
        total = len(sorted_series)

        result_list.append([col, my_score, rank, total])

    # --- 結果を表にまとめる ---
    result_df = pd.DataFrame(result_list, columns=["種目", "スコア", "順位", "人数"])
    st.dataframe(result_df)

else:
    st.info("CSV ファイルをアップロードしてください。")
