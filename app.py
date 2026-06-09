import streamlit as st
import pandas as pd
import numpy as np

st.title("個人順位 & 種目別順位アプリ（順位表示修正版）")

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

    # -------------------------
    # モード選択
    # -------------------------
    st.subheader("② モード選択")
    mode = st.radio("表示方法を選んでください", ["IDで表示", "種目で表示"])

    # ============================================================
    # ① ID で表示するモード
    # ============================================================
    if mode == "IDで表示":

        # 性別フィルタ
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

        # ID 選択
        st.subheader("④ ID を選択")
        id_list = df_filtered.index.tolist()
        selected_id = st.selectbox("ID を選んでください", id_list)

        # 個人データ
        st.subheader("⑤ 個人データ")
        st.dataframe(df.loc[[selected_id]])

        # 各種目の順位
        st.subheader("⑥ 各種目の順位")

        result_list = []

        for col in numeric_cols:
            series = df_filtered[col].dropna()

            # 並び替え（大きい方が良い）
            sorted_series = series.sort_values(ascending=False)

            my_score = df.loc[selected_id, col]

            if pd.isna(my_score):
                result_list.append([col, "データなし", "-", "-"])
                continue

            rank = sorted_series.index.get_loc(selected_id) + 1
            total = len(sorted_series)

            result_list.append([col, my_score, f"{rank}/{total}"])

        result_df = pd.DataFrame(result_list, columns=["種目", "スコア", "順位"])
        st.dataframe(result_df)

    # ============================================================
    # ② 種目で表示するモード（上位/下位修正版）
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

        # 種目選択
        st.subheader("④ 種目を選択")
        target_col = st.selectbox("種目を選んでください", numeric_cols)

        # 上位/下位切り替え
        st.subheader("⑤ 上位/下位を選択")
        order_option = st.radio("並び順", ["上位10人", "下位10人"])

        # 上位 → 大きい順 / 下位 → 小さい順
        ascending_flag = True if order_option == "下位10人" else False

        # 並び替え
        df_sorted = df_filtered.sort_values(by=target_col, ascending=ascending_flag)

        # 上位/下位10人
        top10 = df_sorted.head(10)

        # 表示用データ作成
        result = []
        for idx, row in top10.iterrows():
            score = row[target_col]
            if pd.isna(score):
                continue

            # 順位計算
            series = df_filtered[target_col].dropna()

            # 上位 → 大きい順 / 下位 → 小さい順
            sorted_series = series.sort_values(ascending=ascending_flag)

            rank = sorted_series.index.get_loc(idx) + 1
            total = len(sorted_series)

            # 上位 → 1/388 の形式  
            # 下位 → 388/388 の形式  
            if ascending_flag:  # 下位
                rank_display = f"{total - rank + 1}/{total}"
            else:  # 上位
                rank_display = f"{rank}/{total}"

            gender = row["性別"] if has_gender else "-"

            result.append([idx, gender, score, rank_display])

        result_df = pd.DataFrame(result, columns=["ID", "性別", "スコア", "順位"])
        st.subheader("⑥ 結果表示")
        st.dataframe(result_df)

else:
    st.info("CSV ファイルをアップロードしてください。")

