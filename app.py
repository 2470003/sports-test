import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("個人スコア・順位＋レーダーチャート表示アプリ")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    # 2行目（単位行）をスキップして読み込み
    df = pd.read_csv(uploaded, skiprows=[1])

    # 1列目をインデックスに設定
    df.set_index(df.columns[0], inplace=True)

    # --- ID の .0 を消す（float → int → str） ---
    df.index = df.index.astype(str).str.replace(r"\.0$", "", regex=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    # --- 数値列（種目） ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # --- 0 を除外（NaN に置換） ---
    df[numeric_cols] = df[numeric_cols].replace(0, np.nan)

    # --- ID 選択 ---
    st.subheader("② ID を選択")
    id_list = df.index.tolist()
    selected_id = st.selectbox("ID を選んでください", id_list)

    # --- 個人データ ---
    st.subheader("③ 個人データ")
    st.dataframe(df.loc[[selected_id]])

    # --- 各種目の順位計算 ---
    st.subheader("④ 各種目の順位")

    result_list = []

    for col in numeric_cols:
        series = df[col].dropna()
        sorted_series = series.sort_values(ascending=False)

        my_score = df.loc[selected_id, col]

        if pd.isna(my_score):
            result_list.append([col, "データなし", "-", "-"])
            continue

        rank = sorted_series.index.get_loc(selected_id) + 1
        total = len(sorted_series)

        result_list.append([col, my_score, rank, total])

    result_df = pd.DataFrame(result_list, columns=["種目", "スコア", "順位", "人数"])
    st.dataframe(result_df)

    # --- レーダーチャート ---
    st.subheader("⑤ レーダーチャート")

    # スコアがある種目だけ使用
    radar_df = result_df[result_df["スコア"] != "データなし"]

    if len(radar_df) > 2:  # レーダーは最低3項目必要
        labels = radar_df["種目"].tolist()
        values = radar_df["スコア"].astype(float).tolist()

        # 円を閉じるために最初の値を追加
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        st.pyplot(fig)
    else:
        st.info("レーダーチャートを作成するには 3 種目以上のデータが必要です。")

else:
    st.info("CSV ファイルをアップロードしてください。")
