import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO

st.title("拠点検索アプリ")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# --- PDF 内のリンク注釈から拠点名とURLを抽出 ---
for page in doc:
    annots = page.annots()
    if annots is None:
        continue

    for annot in annots:
        if annot.type[0] == 1:  # リンク注釈
            uri = annot.info.get("uri", None)
            if uri:
                text = annot.info.get("content", "").strip()
                if text:
                    base_points[text] = uri

# --- 検索窓 ---
keyword = st.text_input("拠点名を検索")

# --- 絞り込み ---
filtered_keys = [k for k in base_points.keys() if keyword.lower() in k.lower()]

# --- 拠点一覧 ---
selected = st.selectbox("拠点を選択", filtered_keys)

# --- 選択された拠点の情報を表示 ---
if selected:
    url = base_points[selected]

    st.subheader(f"{selected} のPDF")
    st.markdown(f"[PDFを開く]({url})")

    st.components.v1.iframe(url, height=600)
