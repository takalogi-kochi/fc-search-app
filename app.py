import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
import re

st.title("拠点検索")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# 拠点名の形式（例：HND3, KIX2, NGO5）
pattern = re.compile(r"^[A-Z]{2,4}\d{1,2}$")

# --- PDF 全ページから拠点名とURLを抽出 ---
for page in doc:
    blocks = page.get_text("blocks")
    annots = page.annots()

    if not annots:
        continue

    for annot in annots:
        if annot.type[0] != 1:
            continue

        uri = annot.info.get("uri", "")
        if not uri or uri.startswith("mailto:"):
            continue

        # リンクの中心座標
        x0, y0, x1, y1 = annot.rect
        link_center = ((x0 + x1) / 2, (y0 + y1) / 2)

        # 最も近いテキストブロックを探す
        nearest_text = None
        nearest_dist = 999999

        for block in blocks:
            bx0, by0, bx1, by1, text, *_ = block
            text_center = ((bx0 + bx1) / 2, (by0 + by1) / 2)

            dist = abs(text_center[0] - link_center[0]) + abs(text_center[1] - link_center[1])

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_text = text.strip()

        # テキストから拠点名を抽出
        if nearest_text:
            candidate = nearest_text.split()[0]
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
