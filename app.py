import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
import re

st.title("拠点検索アプリ")

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
    annots = page.annots()
    if not annots:
        continue

    for annot in annots:
        if annot.type[0] != 1:  # リンク注釈のみ
            continue

        uri = annot.info.get("uri", "")
        if not uri:
            continue

        # mailto: は除外
        if uri.startswith("mailto:"):
            continue

        # 拠点名は annotation の title または content に入っている
        title = annot.info.get("title", "").strip()
        content = annot.info.get("content", "").strip()

        candidate = title or content

        # 正規表現で拠点名だけ抽出
        if pattern.match(candidate):
            base_points[candidate] = uri

# --- 拠点名をソートして表示 ---
all_keys = sorted(base_points.keys())

selected = st.selectbox("拠点を選択してください", all_keys)

# --- 選択された拠点の情報を表示 ---
if selected:
    url = base_points[selected]

    st.subheader(f"{selected} のPDF")
    st.markdown(f"[PDFを開く]({url})")

    st.components.v1.iframe(url, height=600)
