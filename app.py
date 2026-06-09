import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# -------------------------
# 日本語フォント設定（文字化け対策）
# -------------------------
font_path = "ipaexg.ttf"  # ← GitHub に置いたフォント
font_manager.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "IPAexGothic"

st.title("スポーツテスト測定")

uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# 大きい方が上位になる種目
reverse_cols = ["CMJ", "DJ-跳躍高", "DJ-RSI"]

if uploaded:
    df = pd.read_csv(uploaded, skiprows=[1])
    df.set_index(df.columns[0], inplace=True)
    df.index = df.index.astype(str).str.replace(r"\.0$", "", regex=True)

    st.subheader("① データプレビュー")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    df[numeric_cols] = df[numeric_cols].replace(0, np.nan)

    has_gender = "性別" in df.columns

    st.subheader("② モード選択")
    mode = st.radio("表示方法を選んでください", ["IDで表示", "種目で表示"])

    # ============================================================
    # ① ID モード
    # ============================================================
    if mode == "IDで表示":

        st.subheader("③ 表示対象（男女別）")
        if has_gender:
            gender_option = st.radio("対象", ["総合", "男", "女"])
            if gender_option == "男":
                df_filtered = df[df["性別"] == "男"]
            elif gender_option == "女":
                df_filtered = df[df["性別"] == "女"]
            else:
                df_filtered = df
        else:
            df_filtered = df

        st.subheader("④ ID を選択")
        selected_id = st.selectbox("ID を選んでください", df_filtered.index.tolist())

        st.subheader("⑤ 個人データ")
        st.dataframe(df.loc[[selected_id]])

        st.subheader("⑥ 各種目の順位")
        result_list = []

        for col in numeric_cols:
            series = df_filtered[col].dropna()

            # 種目ごとに昇順/降順を切り替え
            ascending_flag = False if col in reverse_cols else True

            # 同率順位（method="min"）
            rank_series = df_filtered[col].rank(method="min", ascending=ascending_flag)

            my_score = df.loc[selected_id, col]
            if pd.isna(my_score):
                result_list.append([col, "データなし", "-"])
                continue

            rank = int(rank_series[selected_id])
            total = len(rank_series.dropna())

            result_list.append([col, my_score, f"{rank}/{total}"])

        st.dataframe(pd.DataFrame(result_list, columns=["種目", "スコア", "順位"]))

    # ============================================================
    # ② 種目モード（同率順位＋種目別昇降順対応）
    # ============================================================
    else:
        st.subheader("③ 表示対象（男女別）")
        if has_gender:
            gender_option = st.radio("対象", ["総合", "男", "女"])
            if gender_option == "男":
                df_filtered = df[df["性別"] == "男"]
            elif gender_option == "女":
                df_filtered = df[df["性別"] == "女"]
            else:
                df_filtered = df
        else:
            df_filtered = df

        st.subheader("④ 種目を選択")
        target_col = st.selectbox("種目を選んでください", numeric_cols)

        # 種目ごとに昇順/降順を切り替え
        ascending_flag = False if target_col in reverse_cols else True

        st.subheader("⑤ 上位/下位を選択")
        order_option = st.radio("並び順", ["上位10人", "下位10人"])

        # 上位 → ascending_flag のまま
        # 下位 → ascending_flag を反転
        sort_flag = ascending_flag if order_option == "上位10人" else not ascending_flag

        df_sorted = df_filtered.sort_values(by=target_col, ascending=sort_flag)
        top10 = df_sorted.head(10)

        # 全員の順位（同率対応）
        rank_series = df_filtered[target_col].rank(method="min", ascending=ascending_flag)

        result = []
        for idx, row in top10.iterrows():
            score = row[target_col]
            if pd.isna(score):
                continue

            rank = int(rank_series[idx])
            total = len(rank_series.dropna())

            gender = row["性別"] if has_gender else "-"
            result.append([idx, gender, score, f"{rank}/{total}"])

        st.subheader("⑥ 結果表示")
        st.dataframe(pd.DataFrame(result, columns=["ID", "性別", "スコア", "順位"]))

else:
    st.info("CSV ファイルをアップロードしてください。")
