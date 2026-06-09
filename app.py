import streamlit as st
import pandas as pd

st.title("個人スコア参照アプリ（Streamlit版）")
st.write("ID を選んで、その人のデータを確認できます。")

# --- CSV アップロード ---
uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    # 2行目（単位行）をスキップして読み込み
    df = pd.read_csv(uploaded, skiprows=[1])

    # 1列目をインデックスに設定（ID列）
    df.set_index(df.columns[0], inplace=True)

    st.subheader("① データプレビュー（先頭5行）")
    st.dataframe(df.head())

    # --- ID 一覧を取得 ---
    id_list = df.index.tolist()

    st.subheader("② ID を選択")
    selected_id = st.selectbox("ID を選んでください", id_list)

    # --- 選択した ID のデータを表示 ---
    st.subheader("③ 個人データ")
    st.dataframe(df.loc[[selected_id]])

else:
    st.info("CSV ファイルをアップロードしてください。")
