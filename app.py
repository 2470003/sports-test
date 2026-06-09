import streamlit as st
import pandas as pd

st.title("CSV 参照アプリ（Streamlit版）")
st.write("CSV をアップロードして内容を確認できます。")

# --- CSV アップロード ---
uploaded = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded:
    # 2行目（単位行）をスキップして読み込み
    df = pd.read_csv(uploaded, skiprows=[1])

    # 1列目をインデックスに設定
    df.set_index(df.columns[0], inplace=True)

    st.subheader("① データプレビュー（先頭5行）")
    st.dataframe(df.head())

    st.subheader("② 列名一覧")
    st.write(df.columns.tolist())

else:
    st.info("CSV ファイルをアップロードしてください。")
