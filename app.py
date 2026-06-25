import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
import re
import os

st.title("拠点検索")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# 拠点名の形式（例：HND3, KIX2, NGO5）
pattern = re.compile(r"^[A-Z]{2,4}\d{1,2}$")

# --- PDF 全ページから拠点名リンクだけを抽出 ---
for page in doc:
    links = page.get_links()

    for link in links:
        if "uri" not in link:
            continue

        uri = link["uri"]

        # mailto: は除外
        if uri.startswith("mailto:"):
            continue

        # URL の末尾のファイル名を取得
        filename = os.path.basename(uri).replace(".pdf", "").upper()

        # 拠点名の形式に一致するものだけ採用
        if pattern.match(filename):
            base_points[filename] = uri

# --- 拠点名をソートして表示 ---
all_keys = sorted(base_points.keys())

selected = st.selectbox("拠点を選択してください", all_keys)

# --- 選択された拠点の情報を表示 ---
if selected:
    url = base_points[selected]

    st.subheader(f"{selected} のPDF")
    st.markdown(f"[PDFを開く]({url})")

    st.components.v1.iframe(url, height=600)
