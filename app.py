import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
import re

st.title("拠点検索 Webアプリ（自動更新型・外部PDF対応）")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# 拠点名の正規表現（Amazon FC の形式）
# 例：HND3, KIX2, NGO5, AOM1 など
pattern = re.compile(r"^[A-Z]{2,4}\d{1,2}$")

# --- PDF 内のリンク注釈と周囲テキストから拠点名を抽出 ---
for page in doc:
    links = page.get_links()
    blocks = page.get_text("blocks")

    for link in links:
        if "uri" not in link:
            continue

        uri = link["uri"]
        lx0, ly0, lx1, ly1 = link["from"]
        link_center = ((lx0 + lx1) / 2, (ly0 + ly1) / 2)

        # 周囲テキストから最も近いものを取得
        nearest_text = None
        nearest_dist = 999999

        for block in blocks:
            bx0, by0, bx1, by1, text, *_ = block
            text_center = ((bx0 + bx1) / 2, (by0 + by1) / 2)

            dist = abs(text_center[0] - link_center[0]) + abs(text_center[1] - link_center[1])

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_text = text.strip()

        # 正規表現で拠点名だけを抽出
        if nearest_text:
            candidate = nearest_text.split()[0]  # 先頭の単語を取る
            if pattern.match(candidate):
                base_points[candidate] = uri

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
