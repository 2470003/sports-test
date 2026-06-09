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
            sorted_series = series.sort_values(ascending=True)

            my_score = df.loc[selected_id, col]
            if pd.isna(my_score):
                result_list.append([col, "データなし", "-"])
                continue

            rank = sorted_series.index.get_loc(selected_id) + 1
            total = len(sorted_series)

            result_list.append([col, my_score, f"{rank}/{total}"])

        st.dataframe(pd.DataFrame(result_list, columns=["種目", "スコア", "順位"]))

    # ============================================================
    # ② 種目モード（順位×スコア散布図）
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

        st.subheader("⑤ 上位/下位を選択")
        order_option = st.radio("並び順", ["上位10人", "下位10人"])
        ascending_flag = True if order_option == "上位10人" else False

        df_sorted = df_filtered.sort_values(by=target_col, ascending=ascending_flag)
        top10 = df_sorted.head(10)

        result = []
        for idx, row in top10.iterrows():
            score = row[target_col]
            if pd.isna(score):
                continue

            series = df_filtered[target_col].dropna()
            sorted_series = series.sort_values(ascending=ascending_flag)

            rank = sorted_series.index.get_loc(idx) + 1
            total = len(sorted_series)

            if ascending_flag:
                rank_display = f"{rank}/{total}"
            else:
                rank_display = f"{total - rank + 1}/{total}"

            gender = row["性別"] if has_gender else "-"
            result.append([idx, gender, score, rank_display])

        st.subheader("⑥ 結果表示")
        st.dataframe(pd.DataFrame(result, columns=["ID", "性別", "スコア", "順位"]))

        # ============================================================
        # ⑦ 散布図（横＝順位 × 縦＝スコア）
        # ============================================================
        st.subheader("⑦ 散布図（順位 × スコア）")

        scatter_df = df_filtered[[target_col, "性別"]].dropna()

        # 順位計算（小さい順＝上位）
        scatter_df["順位"] = scatter_df[target_col].rank(method="min", ascending=True)

        fig, ax = plt.subplots(figsize=(8, 5))

        # 男（青）
        male_df = scatter_df[scatter_df["性別"] == "男"]
        ax.scatter(
            male_df["順位"] + np.random.normal(0, 0.1, size=len(male_df)),
            male_df[target_col],
            color="#66CCFF",
            alpha=0.6,
            label="男"
        )

        # 女（薄い赤）
        female_df = scatter_df[scatter_df["性別"] == "女"]
        ax.scatter(
            female_df["順位"] + np.random.normal(0, 0.1, size=len(female_df)),
            female_df[target_col],
            color="#FF9999",
            alpha=0.6,
            label="女"
        )

        ax.set_title(f"{target_col} の散布図（順位 × スコア）")
        ax.set_xlabel("順位（1位＝左）")
        ax.set_ylabel("スコア")
        ax.legend()

        st.pyplot(fig)

else:
    st.info("CSV ファイルをアップロードしてください。")
